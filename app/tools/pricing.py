"""WF002 — Product Price Validation domain logic and execution tools.

Provides genuine domain execution for comparing internal product pricing
against vendor price lists, calculating percentage differences, and flagging
exceptions exceeding 10% strictly as defined in data/workflows.xlsx.
"""

from decimal import Decimal
import csv
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field

from app.agent.normalization import parse_comparison_operator, parse_percentage_threshold
from app.tools.base import BaseTool, ToolMetadata

# The official WF002 workbook defines a fixed 10.0% threshold.
DEFAULT_PRICE_THRESHOLD_PERCENTAGE: float = 10.0


class InternalPriceRecord(BaseModel):
    """Internal catalog pricing record."""

    sku: str
    product_name: str
    internal_price: Decimal
    currency: str = "USD"


class VendorPriceRecord(BaseModel):
    """Vendor catalog pricing record."""

    sku: str
    vendor_name: str
    vendor_price: Decimal
    currency: str = "USD"


class PriceComparisonItem(BaseModel):
    """Matched product price comparison and validation outcome."""

    sku: str
    product_name: str
    vendor_name: str
    internal_price: Decimal
    vendor_price: Decimal
    price_difference: float  # Signed difference: vendor_price - internal_price
    percentage_difference: float  # Absolute percentage: |diff| / internal_price * 100
    is_exception: bool  # True strictly when percentage_difference > threshold
    validation_status: str  # "EXCEPTION_EXCEEDS_10_PERCENT" or "COMPLIANT"
    currency: str = "USD"


def to_decimal(val: Any) -> Decimal:
    """Convert input numeric or string to Decimal safely without floating-point distortion."""
    if isinstance(val, Decimal):
        return val
    if isinstance(val, str):
        cleaned = val.strip().rstrip("%").strip()
        if cleaned.lower().endswith("percent"):
            cleaned = cleaned[:-7].strip()
        return Decimal(cleaned)
    return Decimal(str(val))


def parse_price(raw_price: str, row_idx: int, sku: str, context: str = "Internal") -> Decimal:
    """Parse and validate price string as a positive, finite Decimal.

    Supports optional leading '$' and standard thousands separators (e.g., '$1,200.00').
    Rejects negative, zero, non-finite, and malformed price values.
    """
    cleaned = raw_price.strip()
    if not cleaned:
        err_keyword = "price value" if context == "Internal" else "vendor price"
        raise ValueError(
            f"{context} price CSV row {row_idx} for SKU '{sku}': Invalid {err_keyword} '{raw_price}'."
        )

    # Strip optional leading currency sign
    if cleaned.startswith("$"):
        cleaned = cleaned[1:].strip()

    # Validate thousands separators if commas are present
    if "," in cleaned:
        parts = cleaned.split(".")
        int_part = parts[0]
        if len(parts) > 2:
            err_keyword = "price value" if context == "Internal" else "vendor price"
            raise ValueError(
                f"{context} price CSV row {row_idx} for SKU '{sku}': Invalid {err_keyword} '{raw_price}'."
            )
        int_chunks = int_part.split(",")
        if not (
            1 <= len(int_chunks[0]) <= 3
            and all(len(c) == 3 and c.isdigit() for c in int_chunks[1:])
        ):
            err_keyword = "price value" if context == "Internal" else "vendor price"
            raise ValueError(
                f"{context} price CSV row {row_idx} for SKU '{sku}': Invalid {err_keyword} '{raw_price}' with malformed thousands separator."
            )
        cleaned = cleaned.replace(",", "")

    # Reject non-numeric or non-finite values (like 'nan', 'inf', '-inf')
    if cleaned.lower() in ("nan", "inf", "-inf", "+inf"):
        err_keyword = "price value" if context == "Internal" else "vendor price"
        raise ValueError(
            f"{context} price CSV row {row_idx} for SKU '{sku}': Invalid {err_keyword} '{raw_price}'."
        )

    try:
        price_dec = Decimal(cleaned)
    except Exception:
        err_keyword = "price value" if context == "Internal" else "vendor price"
        raise ValueError(
            f"{context} price CSV row {row_idx} for SKU '{sku}': Invalid {err_keyword} '{raw_price}'."
        )

    # Check finite and positive
    if not price_dec.is_finite() or price_dec <= Decimal("0"):
        err_keyword = "price value" if context == "Internal" else "vendor price"
        raise ValueError(
            f"{context} price CSV row {row_idx} for SKU '{sku}': Invalid {err_keyword} '{raw_price}'."
        )

    return price_dec


VALID_OPERATORS: Dict[str, str] = {
    ">": "EXCEEDS",
    "<": "LESS_THAN",
    ">=": "AT_LEAST",
    "<=": "AT_MOST",
    "==": "EQUALS",
}

OPERATOR_SYNONYMS: Dict[str, str] = {
    ">": ">",
    "gt": ">",
    "greater": ">",
    "greater than": ">",
    "exceeds": ">",
    "exceeding": ">",
    "above": ">",
    "more than": ">",
    "<": "<",
    "lt": "<",
    "less": "<",
    "less than": "<",
    "under": "<",
    "below": "<",
    ">=": ">=",
    "gte": ">=",
    "at least": ">=",
    "greater than or equal to": ">=",
    "minimum": ">=",
    "<=": "<=",
    "lte": "<=",
    "at most": "<=",
    "less than or equal to": "<=",
    "up to": "<=",
    "==": "==",
    "eq": "==",
    "equals": "==",
    "equal to": "==",
    "exactly": "==",
}


def evaluate_price_comparison(
    internal_price: Any,
    vendor_price: Any,
    threshold_percentage: Union[str, float, int, Decimal] = DEFAULT_PRICE_THRESHOLD_PERCENTAGE,
    comparison_operator: str = ">",
) -> Tuple[float, float, bool, str]:
    """Authoritative price comparison decision using exact Decimal arithmetic.

    Decision Rule:
        A product is flagged as an exception when the absolute vendor-price
        difference satisfies the comparison against threshold_percentage% of the internal price:
        abs(vendor_price - internal_price) <op> (internal_price * threshold_percentage / 100)

        Supported operators:
          - '>' (strictly exceeding / greater than)
          - '<' (strictly less than / below)
          - '>=' (at least / greater than or equal to)
          - '<=' (at most / less than or equal to)
          - '==' (exactly equal)

    Comparing against the monetary threshold amount (internal_price * threshold / 100)
    avoids floating-point precision boundary errors (e.g. 3.30 vs 3.63 is exactly 10%,
    which float division distorts to 10.000000000000004).

    Returns:
        (price_difference, percentage_difference, is_exception, validation_status)
    """
    i_dec = to_decimal(internal_price)
    v_dec = to_decimal(vendor_price)

    if i_dec <= Decimal("0"):
        raise ValueError(f"Internal price must be strictly positive, got '{internal_price}'.")
    if v_dec <= Decimal("0"):
        raise ValueError(f"Vendor price must be strictly positive, got '{vendor_price}'.")

    try:
        threshold_dec = to_decimal(threshold_percentage)
    except Exception:
        raise ValueError(
            f"Price validation threshold must be a finite non-negative number, got '{threshold_percentage}'."
        )
    if not threshold_dec.is_finite() or threshold_dec < Decimal("0"):
        raise ValueError(f"Price validation threshold must be a finite non-negative number, got '{threshold_percentage}'.")

    raw_op = comparison_operator if comparison_operator is not None else ">"
    op_norm = parse_comparison_operator(raw_op)

    diff_dec = v_dec - i_dec
    abs_diff_dec = abs(diff_dec)
    threshold_amount = (i_dec * threshold_dec) / Decimal("100")

    if op_norm == ">":
        is_exception = abs_diff_dec > threshold_amount
    elif op_norm == "<":
        is_exception = abs_diff_dec < threshold_amount
    elif op_norm == ">=":
        is_exception = abs_diff_dec >= threshold_amount
    elif op_norm == "<=":
        is_exception = abs_diff_dec <= threshold_amount
    elif op_norm == "==":
        is_exception = abs_diff_dec == threshold_amount
    else:
        is_exception = False

    if not is_exception:
        status = "COMPLIANT"
    elif threshold_dec == Decimal("10") and op_norm == ">":
        status = "EXCEPTION_EXCEEDS_10_PERCENT"
    else:
        op_tag = VALID_OPERATORS[op_norm]
        thresh_label = (
            int(threshold_dec)
            if threshold_dec == threshold_dec.to_integral()
            else f"{threshold_dec:f}".rstrip("0").rstrip(".")
        )
        status = f"EXCEPTION_{op_tag}_{thresh_label}_PERCENT"

    # Percentage difference for display: |diff| / internal_price * 100, rounded to 2 decimals
    raw_pct_diff = (abs_diff_dec / i_dec) * Decimal("100")
    pct_diff_display = round(float(raw_pct_diff), 2)
    diff_display = float(diff_dec)

    return diff_display, pct_diff_display, is_exception, status


def _read_clean_csv(file_path: Union[str, Path]) -> Tuple[List[str], List[Dict[str, Any]]]:
    """Read a CSV file, ignoring comments and stripping whitespace.

    Strictly validates that every row contains exactly the number of columns
    defined in the header. Rows with extra or missing cells (such as unquoted commas
    in currency values like '$1,200') are rejected with actionable line-number diagnostics.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Price dataset file not found at '{path}'")

    rows: List[Dict[str, Any]] = []
    headers: List[str] = []

    with open(path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for raw_line in reader:
            line_no = reader.line_num
            # Skip empty lines
            if not raw_line or not any(field.strip() for field in raw_line):
                continue
            first_cell = raw_line[0].strip()
            # Skip comment lines
            if first_cell.startswith("#"):
                continue

            if not headers:
                headers = [h.strip() for h in raw_line]
                if not any(headers):
                    raise ValueError(f"Price CSV file at '{path}' contains an empty header row.")
            else:
                field_count = len(raw_line)
                expected_count = len(headers)
                if field_count != expected_count:
                    if field_count > expected_count:
                        raise ValueError(
                            f"CSV file '{path}' line {line_no} has {field_count} columns, "
                            f"expected {expected_count} (columns: {', '.join(headers)}). "
                            "Unquoted commas inside values (e.g. '$1,200') split fields incorrectly; "
                            "values containing commas must be enclosed in quotes (e.g. '\"$1,200\"')."
                        )
                    else:
                        raise ValueError(
                            f"CSV file '{path}' line {line_no} has {field_count} columns, "
                            f"expected {expected_count} (columns: {', '.join(headers)}). "
                            "Row is missing required columns."
                        )

                row_dict: Dict[str, Any] = {
                    headers[i]: raw_line[i].strip() for i in range(len(headers))
                }
                row_dict["_csv_line_number"] = line_no
                rows.append(row_dict)

    if not headers:
        raise ValueError(f"Price CSV file at '{path}' contains no header row or data.")

    return headers, rows


def load_internal_prices_csv(csv_path: Union[str, Path]) -> List[InternalPriceRecord]:
    """Parse and validate internal product prices CSV."""
    headers, rows = _read_clean_csv(csv_path)

    # Normalize header lookup
    hdr_map = {h.lower(): h for h in headers}
    if "sku" not in hdr_map:
        raise ValueError(f"Internal price CSV '{csv_path}' missing required column: 'sku'")
    if "internal_price" not in hdr_map and "price" not in hdr_map:
        raise ValueError(
            f"Internal price CSV '{csv_path}' missing required column: 'internal_price'"
        )

    sku_col = hdr_map["sku"]
    price_col = hdr_map.get("internal_price") or hdr_map["price"]
    name_col = hdr_map.get("product_name") or hdr_map.get("name")
    curr_col = hdr_map.get("currency")

    records: List[InternalPriceRecord] = []
    seen_skus = set()
    for fallback_idx, row in enumerate(rows, start=2):
        line_no = row.get("_csv_line_number", fallback_idx)
        raw_sku = str(row.get(sku_col, "")).strip()
        if not raw_sku:
            raise ValueError(f"Internal price CSV row {line_no}: Missing or empty SKU.")

        norm_sku = raw_sku.upper()
        if norm_sku in seen_skus:
            raise ValueError(
                f"Duplicate internal SKU detected on row {line_no}: '{raw_sku}'. "
                "Each SKU must appear only once."
            )
        seen_skus.add(norm_sku)

        raw_price = str(row.get(price_col, ""))
        price_dec = parse_price(raw_price, line_no, raw_sku, context="Internal")

        name = str(row.get(name_col, "")).strip() if name_col else raw_sku

        if curr_col:
            raw_curr = str(row.get(curr_col, "")).strip()
            if not raw_curr:
                raise ValueError(
                    f"Internal price CSV row {line_no} for SKU '{raw_sku}': "
                    "Missing or blank currency value."
                )
            currency = raw_curr.upper()
        else:
            currency = "USD"

        records.append(
            InternalPriceRecord(
                sku=raw_sku,
                product_name=name or raw_sku,
                internal_price=price_dec,
                currency=currency,
            )
        )

    return records


def load_vendor_prices_csv(csv_path: Union[str, Path]) -> List[VendorPriceRecord]:
    """Parse and validate vendor product prices CSV."""
    headers, rows = _read_clean_csv(csv_path)

    hdr_map = {h.lower(): h for h in headers}
    if "sku" not in hdr_map:
        raise ValueError(f"Vendor price CSV '{csv_path}' missing required column: 'sku'")
    if "vendor_price" not in hdr_map and "price" not in hdr_map:
        raise ValueError(
            f"Vendor price CSV '{csv_path}' missing required column: 'vendor_price'"
        )

    sku_col = hdr_map["sku"]
    price_col = hdr_map.get("vendor_price") or hdr_map["price"]
    vendor_col = hdr_map.get("vendor_name") or hdr_map.get("vendor")
    curr_col = hdr_map.get("currency")

    records: List[VendorPriceRecord] = []
    seen_skus = set()
    for fallback_idx, row in enumerate(rows, start=2):
        line_no = row.get("_csv_line_number", fallback_idx)
        raw_sku = str(row.get(sku_col, "")).strip()
        if not raw_sku:
            raise ValueError(f"Vendor price CSV row {line_no}: Missing or empty SKU.")

        norm_sku = raw_sku.upper()
        if norm_sku in seen_skus:
            raise ValueError(
                f"Duplicate vendor SKU detected on row {line_no}: '{raw_sku}'. "
                "Each SKU must appear only once."
            )
        seen_skus.add(norm_sku)

        raw_price = str(row.get(price_col, ""))
        price_dec = parse_price(raw_price, line_no, raw_sku, context="Vendor")

        vendor = str(row.get(vendor_col, "Vendor")).strip() if vendor_col else "Vendor"

        if curr_col:
            raw_curr = str(row.get(curr_col, "")).strip()
            if not raw_curr:
                raise ValueError(
                    f"Vendor price CSV row {line_no} for SKU '{raw_sku}': "
                    "Missing or blank currency value."
                )
            currency = raw_curr.upper()
        else:
            currency = "USD"

        records.append(
            VendorPriceRecord(
                sku=raw_sku,
                vendor_name=vendor or "Vendor",
                vendor_price=price_dec,
                currency=currency,
            )
        )

    return records


def match_prices_by_sku(
    internal_records: List[InternalPriceRecord],
    vendor_records: List[VendorPriceRecord],
) -> Dict[str, Any]:
    """Match internal and vendor records by SKU, detecting unmatched items."""
    internal_map = {}
    for item in internal_records:
        key = item.sku.strip().upper()
        if key in internal_map:
            raise ValueError(
                f"Duplicate internal SKU detected: '{item.sku}'. "
                "Each SKU must appear only once."
            )
        internal_map[key] = item

    vendor_map = {}
    for item in vendor_records:
        key = item.sku.strip().upper()
        if key in vendor_map:
            raise ValueError(
                f"Duplicate vendor SKU detected: '{item.sku}'. "
                "Each SKU must appear only once."
            )
        vendor_map[key] = item

    matched_pairs: List[Dict[str, Any]] = []
    unmatched_vendor: List[Dict[str, Any]] = []
    unmatched_internal: List[Dict[str, Any]] = []

    for v_sku_upper, v_rec in vendor_map.items():
        if v_sku_upper in internal_map:
            i_rec = internal_map[v_sku_upper]
            if i_rec.currency.strip().upper() != v_rec.currency.strip().upper():
                raise ValueError(
                    f"Currency mismatch for SKU '{i_rec.sku}': "
                    f"internal currency '{i_rec.currency}', "
                    f"vendor currency '{v_rec.currency}'. "
                    "Prices must use the same currency before comparison."
                )

            matched_pairs.append({
                "sku": i_rec.sku,
                "product_name": i_rec.product_name,
                "vendor_name": v_rec.vendor_name,
                "internal_price": i_rec.internal_price,
                "vendor_price": v_rec.vendor_price,
                "currency": i_rec.currency,
            })
        else:
            unmatched_vendor.append({
                "sku": v_rec.sku,
                "vendor_name": v_rec.vendor_name,
                "vendor_price": v_rec.vendor_price,
                "reason": "SKU not found in internal product catalog",
            })

    for i_sku_upper, i_rec in internal_map.items():
        if i_sku_upper not in vendor_map:
            unmatched_internal.append({
                "sku": i_rec.sku,
                "product_name": i_rec.product_name,
                "internal_price": i_rec.internal_price,
                "reason": "SKU not found in vendor price list",
            })

    return {
        "matched_pairs": matched_pairs,
        "unmatched_vendor": unmatched_vendor,
        "unmatched_internal": unmatched_internal,
        "match_count": len(matched_pairs),
    }


def compare_and_flag_prices(
    matched_pairs: List[Dict[str, Any]],
    threshold_percentage: Union[str, float, int, Decimal] = DEFAULT_PRICE_THRESHOLD_PERCENTAGE,
    comparison_operator: str = ">",
) -> Dict[str, Any]:
    """Calculate price difference, percentage difference, and flag exceptions exceeding threshold."""
    results: List[Dict[str, Any]] = []
    exceptions: List[Dict[str, Any]] = []

    for pair in matched_pairs:
        diff, pct_diff, is_exception, status = evaluate_price_comparison(
            internal_price=pair["internal_price"],
            vendor_price=pair["vendor_price"],
            threshold_percentage=threshold_percentage,
            comparison_operator=comparison_operator,
        )

        item_dict = {
            "sku": pair["sku"],
            "product_name": pair["product_name"],
            "vendor_name": pair["vendor_name"],
            "internal_price": to_decimal(pair["internal_price"]),
            "vendor_price": to_decimal(pair["vendor_price"]),
            "price_difference": diff,
            "percentage_difference": pct_diff,
            "is_exception": is_exception,
            "validation_status": status,
            "currency": pair.get("currency", "USD"),
        }
        results.append(item_dict)
        if is_exception:
            exceptions.append(item_dict)

    return {
        "compared_products": results,
        "exceptions": exceptions,
        "exception_count": len(exceptions),
    }


# ==============================================================================
# Step Tools for Generic Execution Engine
# ==============================================================================


class PriceDataLoaderTool(BaseTool):
    """Step 1 Tool: Load product prices from internal and vendor CSV files."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="price_data_loader",
            description="Load internal product prices and vendor price lists from CSV files.",
        )

    def execute(
        self,
        internal_csv_path: Optional[str] = None,
        vendor_csv_path: Optional[str] = None,
        historical_vendor_csv_path: Optional[str] = None,
        prior_vendor_csv_path: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        default_internal = Path("data/sample_internal_prices.csv")
        default_vendor = Path("data/sample_vendor_prices.csv")

        hist_path = (
            historical_vendor_csv_path
            or prior_vendor_csv_path
            or kwargs.get("historical_vendor_csv_path")
            or kwargs.get("prior_vendor_csv_path")
        )
        if hist_path:
            h_path = Path(hist_path)
            v_path = Path(vendor_csv_path) if vendor_csv_path else default_vendor
            prior_items = load_vendor_prices_csv(h_path)
            current_items = load_vendor_prices_csv(v_path)
            baseline_records = [
                InternalPriceRecord(
                    sku=item.sku,
                    product_name=f"{item.vendor_name} ({item.sku})",
                    internal_price=item.vendor_price,
                    currency=item.currency,
                )
                for item in prior_items
            ]
            return {
                "internal_prices": [item.model_dump() for item in baseline_records],
                "vendor_prices": [item.model_dump() for item in current_items],
                "total_internal": len(baseline_records),
                "total_vendor": len(current_items),
                "summary": (
                    f"Loaded {len(baseline_records)} historical vendor price record(s) and "
                    f"{len(current_items)} current vendor record(s) for period comparison."
                ),
                "is_historical_comparison": True,
            }

        i_path = Path(internal_csv_path) if internal_csv_path else default_internal
        v_path = Path(vendor_csv_path) if vendor_csv_path else default_vendor

        internal_items = load_internal_prices_csv(i_path)
        vendor_items = load_vendor_prices_csv(v_path)

        return {
            "internal_prices": [item.model_dump() for item in internal_items],
            "vendor_prices": [item.model_dump() for item in vendor_items],
            "total_internal": len(internal_items),
            "total_vendor": len(vendor_items),
            "summary": f"Loaded {len(internal_items)} internal product(s) and {len(vendor_items)} vendor record(s).",
        }


class ProductSkuMatcherTool(BaseTool):
    """Step 2 Tool: match products by SKU."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="sku_matcher",
            description="Match internal products and vendor price records by SKU.",
        )

    def execute(
        self,
        internal_prices: Optional[List[Dict[str, Any]]] = None,
        vendor_prices: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        i_records = [InternalPriceRecord(**r) for r in (internal_prices or [])]
        v_records = [VendorPriceRecord(**r) for r in (vendor_prices or [])]

        matched = match_prices_by_sku(i_records, v_records)
        return {
            "matched_pairs": matched["matched_pairs"],
            "unmatched_vendor": matched["unmatched_vendor"],
            "unmatched_internal": matched["unmatched_internal"],
            "match_count": matched["match_count"],
            "summary": f"Matched {matched['match_count']} product(s) by SKU. {len(matched['unmatched_vendor'])} vendor record(s) unmatched.",
        }


class PriceComparatorTool(BaseTool):
    """Step 3 Tool: compare internal and vendor prices."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="price_comparator",
            description="Compare internal and vendor prices for matched SKU records.",
        )

    def execute(
        self,
        matched_pairs: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        pairs = matched_pairs or []
        compared: List[Dict[str, Any]] = []
        for pair in pairs:
            diff_dec = to_decimal(pair["vendor_price"]) - to_decimal(pair["internal_price"])
            item = dict(pair)
            item["internal_price"] = to_decimal(pair["internal_price"])
            item["vendor_price"] = to_decimal(pair["vendor_price"])
            item["price_difference"] = float(diff_dec)
            compared.append(item)

        return {
            "compared_products": compared,
            "summary": f"Compared prices for {len(compared)} matched product(s).",
        }


class PercentageDifferenceCalculatorTool(BaseTool):
    """Step 4 Tool: calculate percentage difference."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="percentage_difference_calculator",
            description="Calculate percentage difference between internal and vendor prices.",
        )

    def execute(
        self,
        compared_products: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        items = compared_products or []
        evaluated: List[Dict[str, Any]] = []
        for item in items:
            diff, pct_diff, _, _ = evaluate_price_comparison(
                internal_price=item["internal_price"],
                vendor_price=item["vendor_price"],
            )

            res = dict(item)
            res["internal_price"] = to_decimal(item["internal_price"])
            res["vendor_price"] = to_decimal(item["vendor_price"])
            res["price_difference"] = diff
            res["percentage_difference"] = pct_diff
            evaluated.append(res)

        return {
            "price_evaluations": evaluated,
            "summary": f"Calculated percentage differences for {len(evaluated)} product(s).",
        }


class PriceExceptionFlaggerTool(BaseTool):
    """Step 5 Tool: flag pricing discrepancy exceptions."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="price_exception_flagger",
            description="Flag pricing discrepancies strictly exceeding 10% by default, or according to explicit request threshold and operator.",
        )

    def execute(
        self,
        price_evaluations: Optional[List[Dict[str, Any]]] = None,
        unmatched_vendor: Optional[List[Dict[str, Any]]] = None,
        unmatched_internal: Optional[List[Dict[str, Any]]] = None,
        threshold: Optional[Union[float, int, str, Decimal]] = None,
        price_threshold: Optional[Union[float, int, str, Decimal]] = None,
        threshold_percentage: Optional[Union[float, int, str, Decimal]] = None,
        operator: Optional[str] = None,
        comparison_operator: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        items = price_evaluations or []
        unmatched_v = unmatched_vendor or []
        unmatched_i = unmatched_internal or []

        # Determine effective threshold: explicit threshold parameter wins over default 10.0%
        req_thresh = (
            threshold
            if threshold is not None
            else (
                price_threshold
                if price_threshold is not None
                else (
                    threshold_percentage
                    if threshold_percentage is not None
                    else (
                        kwargs.get("threshold")
                        if kwargs.get("threshold") is not None
                        else (
                            kwargs.get("price_threshold")
                            if kwargs.get("price_threshold") is not None
                            else kwargs.get("threshold_percentage")
                        )
                    )
                )
            )
        )
        if req_thresh is not None:
            eff_thresh_val = parse_percentage_threshold(req_thresh, "Price validation threshold")
            eff_thresh = to_decimal(eff_thresh_val)
        else:
            eff_thresh = Decimal(str(DEFAULT_PRICE_THRESHOLD_PERCENTAGE))

        # Determine effective comparison operator: default is '>'
        req_op = operator or comparison_operator or kwargs.get("operator") or kwargs.get("comparison_operator")
        if req_op is not None:
            eff_op = parse_comparison_operator(req_op)
        else:
            eff_op = ">"

        validated_list: List[Dict[str, Any]] = []
        exceptions: List[Dict[str, Any]] = []

        for item in items:
            diff, pct_diff, is_exception, status = evaluate_price_comparison(
                internal_price=item["internal_price"],
                vendor_price=item["vendor_price"],
                threshold_percentage=eff_thresh,
                comparison_operator=eff_op,
            )

            res = dict(item)
            res["internal_price"] = to_decimal(item["internal_price"])
            res["vendor_price"] = to_decimal(item["vendor_price"])
            res["price_difference"] = diff
            res["percentage_difference"] = pct_diff
            res["is_exception"] = is_exception
            res["validation_status"] = status
            validated_list.append(res)
            if is_exception:
                exceptions.append(res)

        op_norm = OPERATOR_SYNONYMS.get(eff_op.lower(), eff_op)
        if eff_thresh == Decimal("10") and op_norm == ">":
            summary_msg = (
                f"Validated {len(validated_list)} products: {len(exceptions)} exception(s) "
                f"exceeding {DEFAULT_PRICE_THRESHOLD_PERCENTAGE}% threshold."
            )
        else:
            thresh_label = (
                int(eff_thresh)
                if eff_thresh == eff_thresh.to_integral()
                else f"{eff_thresh:f}".rstrip("0").rstrip(".")
            )
            op_phrase = {
                ">": "exceeding",
                "<": "less than",
                ">=": "at least",
                "<=": "at most",
                "==": "equal to",
            }.get(op_norm, "matching")
            summary_msg = (
                f"Validated {len(validated_list)} products: {len(exceptions)} exception(s) "
                f"{op_phrase} {thresh_label}% threshold."
            )

        return {
            "matched_products": validated_list,
            "exceptions": exceptions,
            "exception_count": len(exceptions),
            "total_matched": len(validated_list),
            "unmatched_vendor_records": unmatched_v,
            "unmatched_internal_records": unmatched_i,
            "summary": summary_msg,
        }

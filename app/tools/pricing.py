"""WF002 — Product Price Validation domain logic and execution tools.

Provides genuine domain execution for comparing internal product pricing
against vendor price lists, calculating percentage differences, and flagging
exceptions exceeding 10% strictly as defined in data/workflows.xlsx.
"""

import csv
import math
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field

from app.tools.base import BaseTool, ToolMetadata


class InternalPriceRecord(BaseModel):
    """Internal catalog pricing record."""

    sku: str
    product_name: str
    internal_price: float
    currency: str = "USD"


class VendorPriceRecord(BaseModel):
    """Vendor catalog pricing record."""

    sku: str
    vendor_name: str
    vendor_price: float
    currency: str = "USD"


class PriceComparisonItem(BaseModel):
    """Matched product price comparison and validation outcome."""

    sku: str
    product_name: str
    vendor_name: str
    internal_price: float
    vendor_price: float
    price_difference: float  # Signed difference: vendor_price - internal_price
    percentage_difference: float  # Absolute percentage: |diff| / internal_price * 100
    is_exception: bool  # True strictly when percentage_difference > threshold
    validation_status: str  # "EXCEPTION_EXCEEDS_THRESHOLD" or "COMPLIANT"
    currency: str = "USD"


def _read_clean_csv(file_path: Union[str, Path]) -> Tuple[List[str], List[Dict[str, str]]]:
    """Read a CSV file, ignoring comments and stripping whitespace."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Price dataset file not found at '{path}'")

    rows: List[Dict[str, str]] = []
    headers: List[str] = []

    with open(path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for raw_line in reader:
            if not raw_line or not any(raw_line):
                continue
            first_cell = raw_line[0].strip()
            if first_cell.startswith("#"):
                continue
            if not headers:
                headers = [h.strip() for h in raw_line]
            else:
                row_dict = {
                    headers[i]: raw_line[i].strip() if i < len(raw_line) else ""
                    for i in range(len(headers))
                }
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
    for idx, row in enumerate(rows, start=2):
        raw_sku = row.get(sku_col, "").strip()
        if not raw_sku:
            raise ValueError(f"Internal price CSV row {idx}: Missing or empty SKU.")

        raw_price = row.get(price_col, "").strip().replace("$", "").replace(",", "")
        try:
            price = float(raw_price)
            # Reject NaN and positive/negative infinity
            if not math.isfinite(price):
                raise ValueError
            if price <= 0:
                raise ValueError
        except (ValueError, TypeError):
            raise ValueError(
                f"Internal price CSV row {idx} for SKU '{raw_sku}': Invalid price value '{raw_price}'."
            )

        name = row.get(name_col, "").strip() if name_col else raw_sku
        currency = row.get(curr_col, "USD").strip() if curr_col else "USD"

        records.append(
            InternalPriceRecord(
                sku=raw_sku,
                product_name=name or raw_sku,
                internal_price=round(price, 2),
                currency=currency or "USD",
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
    for idx, row in enumerate(rows, start=2):
        raw_sku = row.get(sku_col, "").strip()
        if not raw_sku:
            raise ValueError(f"Vendor price CSV row {idx}: Missing or empty SKU.")

        raw_price = row.get(price_col, "").strip().replace("$", "").replace(",", "")
        try:
            price = float(raw_price)
            # Reject NaN and positive/negative infinity
            if not math.isfinite(price):
                raise ValueError
            if price <= 0:
                raise ValueError
        except (ValueError, TypeError):
            raise ValueError(
                f"Vendor price CSV row {idx} for SKU '{raw_sku}': Invalid vendor price '{raw_price}'."
            )

        vendor = row.get(vendor_col, "Vendor").strip() if vendor_col else "Vendor"
        currency = row.get(curr_col, "USD").strip() if curr_col else "USD"

        records.append(
            VendorPriceRecord(
                sku=raw_sku,
                vendor_name=vendor or "Vendor",
                vendor_price=round(price, 2),
                currency=currency or "USD",
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
    threshold_percentage: float = 10.0,
) -> Dict[str, Any]:
    """Calculate price difference, percentage difference, and flag exceptions exceeding threshold."""
    results: List[Dict[str, Any]] = []
    exceptions: List[Dict[str, Any]] = []

    for pair in matched_pairs:
        internal_p = float(pair["internal_price"])
        vendor_p = float(pair["vendor_price"])

        diff = round(vendor_p - internal_p, 2)
        raw_pct_diff = (abs(vendor_p - internal_p) / internal_p) * 100.0
        pct_diff = round(raw_pct_diff, 2)

        # Compare the unrounded percentage to the threshold.
        is_exception = raw_pct_diff > threshold_percentage
        status = "EXCEPTION_EXCEEDS_10_PERCENT" if is_exception else "COMPLIANT"

        item_dict = {
            "sku": pair["sku"],
            "product_name": pair["product_name"],
            "vendor_name": pair["vendor_name"],
            "internal_price": internal_p,
            "vendor_price": vendor_p,
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
        **kwargs: Any,
    ) -> Dict[str, Any]:
        default_internal = Path("data/sample_internal_prices.csv")
        default_vendor = Path("data/sample_vendor_prices.csv")

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
            i_p = float(pair["internal_price"])
            v_p = float(pair["vendor_price"])
            diff = round(v_p - i_p, 2)
            item = dict(pair)
            item["price_difference"] = diff
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
            i_p = float(item["internal_price"])
            v_p = float(item["vendor_price"])
            raw_pct_diff = (abs(v_p - i_p) / i_p) * 100.0

            res = dict(item)
            res["percentage_difference"] = round(raw_pct_diff, 2)
            res["_raw_percentage_difference"] = raw_pct_diff
            evaluated.append(res)

        return {
            "price_evaluations": evaluated,
            "summary": f"Calculated percentage differences for {len(evaluated)} product(s).",
        }


class PriceExceptionFlaggerTool(BaseTool):
    """Step 5 Tool: flag exceptions exceeding 10% threshold."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="price_exception_flagger",
            description="Flag pricing discrepancies strictly exceeding 10% and compile validation report.",
        )

    def execute(
        self,
        price_evaluations: Optional[List[Dict[str, Any]]] = None,
        unmatched_vendor: Optional[List[Dict[str, Any]]] = None,
        unmatched_internal: Optional[List[Dict[str, Any]]] = None,
        threshold: float = 10.0,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        items = price_evaluations or []
        unmatched_v = unmatched_vendor or []
        unmatched_i = unmatched_internal or []

        validated_list: List[Dict[str, Any]] = []
        exceptions: List[Dict[str, Any]] = []

        for item in items:
            pct = float(
                item.get("_raw_percentage_difference", item["percentage_difference"])
            )
            # Decision logic: strictly greater than 10%
            is_exception = pct > threshold
            status = "EXCEPTION_EXCEEDS_10_PERCENT" if is_exception else "COMPLIANT"

            res = dict(item)
            res.pop("_raw_percentage_difference", None)
            res["is_exception"] = is_exception
            res["validation_status"] = status
            validated_list.append(res)
            if is_exception:
                exceptions.append(res)

        summary_msg = (
            f"Validated {len(validated_list)} products: {len(exceptions)} exception(s) "
            f"exceeding {threshold}% threshold."
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

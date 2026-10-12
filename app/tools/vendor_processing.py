"""WF003 — Vendor File Processing domain logic and execution tools.

Provides genuine domain execution for reading vendor files, detecting and normalizing
column-name variations, validating required fields (SKU and product name), identifying
invalid rows, and producing a cleaned dataset without overwriting the input file.
"""

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field

from app.tools.base import BaseTool, ToolMetadata

# Standardized column name mapping rules
COLUMN_SYNONYMS: Dict[str, List[str]] = {
    "sku": ["sku", "item_sku", "product_sku", "item_id", "item_code", "code", "part_number"],
    "product_name": [
        "product_name",
        "item_title",
        "item_name",
        "name",
        "title",
        "product",
        "product_title",
        "description",
    ],
    "price": [
        "price",
        "unit_price",
        "cost",
        "wholesale_price",
        "rate",
        "vendor_price",
        "price_usd",
    ],
    "category": ["category", "product_category", "department", "dept", "item_category"],
    "stock": [
        "stock",
        "quantity_available",
        "quantity",
        "qty",
        "inventory",
        "available_units",
        "available_qty",
    ],
}


class InvalidRowRecord(BaseModel):
    """Detailed diagnostic for a rejected vendor row."""

    row_number: int
    raw_data: Dict[str, Any]
    errors: List[str]


class NormalizedVendorRecord(BaseModel):
    """Cleaned and validated vendor record."""

    sku: str
    product_name: str
    price: Optional[float] = None
    category: Optional[str] = None
    stock: Optional[int] = None
    extra_fields: Dict[str, Any] = Field(default_factory=dict)


def normalize_header_name(header: str) -> str:
    """Normalize a raw column header to its canonical schema equivalent."""
    clean = header.strip().lower().replace(" ", "_").replace("-", "_")
    for canonical, synonyms in COLUMN_SYNONYMS.items():
        if clean in synonyms:
            return canonical
    return clean


def read_vendor_file_records(
    file_path: Union[str, Path]
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """Read a vendor data file (CSV or XLSX) safely without modifying the source."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Vendor input file not found at '{path}'")

    rows: List[Dict[str, Any]] = []
    headers: List[str] = []

    if path.suffix.lower() == ".xlsx":
        import openpyxl

        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb.active
        for row_vals in ws.iter_rows(values_only=True):
            if not row_vals or all(v is None for v in row_vals):
                continue
            str_vals = [str(v).strip() if v is not None else "" for v in row_vals]
            if str_vals[0].startswith("#"):
                continue
            if not headers:
                headers = str_vals
            else:
                row_dict = {
                    headers[i]: str_vals[i] if i < len(str_vals) else ""
                    for i in range(len(headers))
                }
                rows.append(row_dict)
    else:
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
        raise ValueError(f"Vendor file at '{path}' contains no headers or data.")

    return headers, rows


def detect_and_normalize_columns(
    raw_headers: List[str], raw_rows: List[Dict[str, Any]]
) -> Tuple[Dict[str, str], List[Dict[str, Any]]]:
    """Detect column synonyms and normalize row dictionaries to canonical headers."""
    col_mapping: Dict[str, str] = {}
    for h in raw_headers:
        col_mapping[h] = normalize_header_name(h)

    normalized_rows: List[Dict[str, Any]] = []
    for row in raw_rows:
        norm_row: Dict[str, Any] = {}
        for raw_k, val in row.items():
            norm_k = col_mapping.get(raw_k, raw_k)
            norm_row[norm_k] = val
        normalized_rows.append(norm_row)

    return col_mapping, normalized_rows


def validate_vendor_records(
    normalized_rows: List[Dict[str, Any]]
) -> Tuple[List[NormalizedVendorRecord], List[InvalidRowRecord]]:
    """Validate required fields according to WF003 Decision Logic:

    Decision Logic: Rows missing SKU or product name are invalid.
    Also validates non-negative price and non-negative stock when present.
    """
    valid_records: List[NormalizedVendorRecord] = []
    invalid_records: List[InvalidRowRecord] = []

    for idx, row in enumerate(normalized_rows, start=1):
        errors: List[str] = []

        sku = str(row.get("sku", "")).strip()
        if not sku:
            errors.append("Missing required field: SKU is blank or missing.")

        product_name = str(row.get("product_name", "")).strip()
        if not product_name:
            errors.append("Missing required field: product_name is blank or missing.")

        # Price validation (optional field, but if provided must be valid non-negative float)
        price_val: Optional[float] = None
        raw_price = str(row.get("price", "")).strip().replace("$", "").replace(",", "")
        if raw_price:
            try:
                p = float(raw_price)
                if p < 0:
                    errors.append(f"Invalid price '{raw_price}': price must be non-negative.")
                else:
                    price_val = round(p, 2)
            except ValueError:
                errors.append(f"Invalid price '{raw_price}': must be a valid numeric value.")

        # Stock validation (optional field, but if provided must be valid non-negative integer)
        stock_val: Optional[int] = None
        raw_stock = str(row.get("stock", "")).strip()
        if raw_stock:
            try:
                s = int(float(raw_stock))
                if s < 0:
                    errors.append(f"Invalid stock '{raw_stock}': stock must be non-negative.")
                else:
                    stock_val = s
            except ValueError:
                errors.append(f"Invalid stock '{raw_stock}': must be a valid integer.")

        category_val = str(row.get("category", "")).strip() or None

        # Preserve any unmapped extra columns
        extra_fields = {
            k: v
            for k, v in row.items()
            if k not in ("sku", "product_name", "price", "category", "stock")
        }

        if errors:
            invalid_records.append(
                InvalidRowRecord(row_number=idx, raw_data=row, errors=errors)
            )
        else:
            valid_records.append(
                NormalizedVendorRecord(
                    sku=sku,
                    product_name=product_name,
                    price=price_val,
                    category=category_val,
                    stock=stock_val,
                    extra_fields=extra_fields,
                )
            )

    return valid_records, invalid_records


# ==============================================================================
# Step Tools for Generic Execution Engine
# ==============================================================================


class VendorFileReaderTool(BaseTool):
    """Step 1 Tool: Read file."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="vendor_file_reader",
            description="Read vendor CSV or Excel file safely without overwriting the input.",
        )

    def execute(self, file_path: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        default_path = Path("data/sample_vendor_catalog.csv")
        target_path = Path(file_path) if file_path else default_path

        headers, raw_rows = read_vendor_file_records(target_path)
        return {
            "raw_headers": headers,
            "raw_rows": raw_rows,
            "file_path": str(target_path),
            "total_rows_read": len(raw_rows),
            "summary": f"Read {len(raw_rows)} raw record(s) from '{target_path.name}'.",
        }


class ColumnDetectorTool(BaseTool):
    """Step 2 Tool: detect columns."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="column_detector",
            description="Detect columns and schema presence in vendor data.",
        )

    def execute(
        self, raw_headers: Optional[List[str]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        headers = raw_headers or []
        detected = [normalize_header_name(h) for h in headers]
        return {
            "raw_headers": headers,
            "detected_columns": detected,
            "summary": f"Detected {len(headers)} column(s): {', '.join(headers)}.",
        }


class ColumnNormalizerTool(BaseTool):
    """Step 3 Tool: normalize column names."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="column_normalizer",
            description="Normalize column variations to canonical schema headers.",
        )

    def execute(
        self,
        raw_headers: Optional[List[str]] = None,
        raw_rows: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        headers = raw_headers or []
        rows = raw_rows or []
        col_mapping, normalized = detect_and_normalize_columns(headers, rows)
        return {
            "normalized_rows": normalized,
            "column_mapping": col_mapping,
            "normalized_headers": list(set(col_mapping.values())),
            "summary": f"Normalized {len(headers)} column(s) across {len(normalized)} row(s).",
        }


class RequiredFieldsValidatorTool(BaseTool):
    """Step 4 Tool: validate required fields."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="required_fields_validator",
            description="Validate required product fields (SKU, product name) and data types.",
        )

    def execute(
        self, normalized_rows: Optional[List[Dict[str, Any]]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        rows = normalized_rows or []
        valid_items, invalid_items = validate_vendor_records(rows)
        return {
            "preliminary_valid": [item.model_dump() for item in valid_items],
            "preliminary_invalid": [item.model_dump() for item in invalid_items],
            "valid_count": len(valid_items),
            "invalid_count": len(invalid_items),
            "summary": f"Validated required fields: {len(valid_items)} passed, {len(invalid_items)} failed.",
        }


class InvalidRowsIdentifierTool(BaseTool):
    """Step 5 Tool: identify invalid rows."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="invalid_rows_identifier",
            description="Identify invalid rows and compile actionable error messages.",
        )

    def execute(
        self,
        preliminary_valid: Optional[List[Dict[str, Any]]] = None,
        preliminary_invalid: Optional[List[Dict[str, Any]]] = None,
        normalized_rows: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        if preliminary_invalid is not None and preliminary_valid is not None:
            valid_list = preliminary_valid
            invalid_list = preliminary_invalid
        else:
            v_items, inv_items = validate_vendor_records(normalized_rows or [])
            valid_list = [v.model_dump() for v in v_items]
            invalid_list = [inv.model_dump() for inv in inv_items]

        return {
            "valid_rows": valid_list,
            "invalid_rows": invalid_list,
            "valid_count": len(valid_list),
            "invalid_count": len(invalid_list),
            "summary": f"Identified {len(invalid_list)} invalid row(s) requiring remediation.",
        }


class CleanDatasetProducerTool(BaseTool):
    """Step 6 Tool: produce cleaned dataset."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="clean_dataset_producer",
            description="Produce final cleaned dataset and validation summary report without overwriting input.",
        )

    def execute(
        self,
        valid_rows: Optional[List[Dict[str, Any]]] = None,
        invalid_rows: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        valid = valid_rows or []
        invalid = invalid_rows or []
        total = len(valid) + len(invalid)

        summary_msg = (
            f"Processed vendor file: {len(valid)} valid record(s) cleaned, "
            f"{len(invalid)} invalid row(s) flagged."
        )

        return {
            "cleaned_records": valid,
            "invalid_records": invalid,
            "total_processed": total,
            "valid_count": len(valid),
            "invalid_count": len(invalid),
            "summary": summary_msg,
        }

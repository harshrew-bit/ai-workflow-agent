"""Domain tools and business logic for WF001: Inventory Restock Check."""

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from app.agent.normalization import parse_integer_threshold
from app.tools.base import BaseTool, ToolMetadata

REQUIRED_INVENTORY_COLUMNS = [
    "product_id",
    "product_name",
    "current_stock",
    "minimum_stock",
    "unit_cost",
    "supplier",
]


class InventoryItem(BaseModel):
    """Validated inventory item record."""

    product_id: str = Field(..., min_length=1)
    product_name: str = Field(..., min_length=1)
    current_stock: int = Field(..., ge=0)
    minimum_stock: int = Field(..., ge=0)
    unit_cost: float = Field(..., ge=0.0)
    supplier: str = Field(..., min_length=1)


class RestockItem(BaseModel):
    """Calculated restock item detail."""

    product_id: str
    product_name: str
    current_stock: int
    minimum_stock: int
    reorder_quantity: int = Field(..., ge=0)
    unit_cost: float = 0.0
    supplier: str = ""


# --- Pure Domain Business Logic ---

def read_and_validate_inventory_csv(
    file_path: Union[str, Path],
) -> List[InventoryItem]:
    """Read and validate inventory records from a CSV file.

    Raises FileNotFoundError if file is missing.
    Raises ValueError on missing columns or invalid/negative numeric values.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Inventory CSV file not found at: '{path.resolve()}'. Please verify the path exists."
        )

    records: List[InventoryItem] = []
    with open(path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        try:
            raw_headers = next(reader)
        except StopIteration:
            # Completely empty file
            return []

        headers = [h.strip().lower() for h in raw_headers if h is not None]
        missing_cols = [c for c in REQUIRED_INVENTORY_COLUMNS if c not in headers]
        if missing_cols:
            raise ValueError(
                f"Inventory CSV is missing required column(s): {missing_cols}. Found: {headers}"
            )

        col_indices = {col: headers.index(col) for col in REQUIRED_INVENTORY_COLUMNS}

        for row_idx, row in enumerate(reader, start=2):
            # Skip empty rows
            if not row or not any(cell.strip() for cell in row):
                continue

            row_data: Dict[str, Any] = {}
            for col_name, idx in col_indices.items():
                val = row[idx].strip() if idx < len(row) else ""
                row_data[col_name] = val

            # Validate types and constraints
            pid = row_data.get("product_id", "")
            if not pid:
                raise ValueError(f"Row {row_idx}: 'product_id' cannot be empty.")

            pname = row_data.get("product_name", "")
            if not pname:
                raise ValueError(f"Row {row_idx} ({pid}): 'product_name' cannot be empty.")

            # Validate current_stock
            raw_current = row_data.get("current_stock", "")
            try:
                current_stock = int(raw_current)
                if current_stock < 0:
                    raise ValueError("Must be non-negative")
            except Exception:
                raise ValueError(
                    f"Row {row_idx} ({pid}): invalid 'current_stock' value '{raw_current}'. "
                    "Must be a non-negative integer."
                )

            # Validate minimum_stock
            raw_min = row_data.get("minimum_stock", "")
            try:
                minimum_stock = int(raw_min)
                if minimum_stock < 0:
                    raise ValueError("Must be non-negative")
            except Exception:
                raise ValueError(
                    f"Row {row_idx} ({pid}): invalid 'minimum_stock' value '{raw_min}'. "
                    "Must be a non-negative integer."
                )

            # Validate unit_cost
            raw_cost = row_data.get("unit_cost", "")
            try:
                unit_cost = float(raw_cost)
                if unit_cost < 0.0:
                    raise ValueError("Must be non-negative")
            except Exception:
                raise ValueError(
                    f"Row {row_idx} ({pid}): invalid 'unit_cost' value '{raw_cost}'. "
                    "Must be a non-negative number."
                )

            supplier = row_data.get("supplier", "")
            if not supplier:
                raise ValueError(f"Row {row_idx} ({pid}): 'supplier' cannot be empty.")

            records.append(
                InventoryItem(
                    product_id=pid,
                    product_name=pname,
                    current_stock=current_stock,
                    minimum_stock=minimum_stock,
                    unit_cost=unit_cost,
                    supplier=supplier,
                )
            )

    return records


def calculate_restock_requirements(
    items: List[InventoryItem],
    threshold_override: Optional[int] = None,
) -> List[RestockItem]:
    """Calculate restock requirements based on decision logic:

    If current_stock < minimum_stock, mark product for restock.
    reorder_quantity = minimum_stock - current_stock.
    """
    restock_list: List[RestockItem] = []
    for item in items:
        threshold = (
            threshold_override
            if threshold_override is not None
            else item.minimum_stock
        )
        if item.current_stock < threshold:
            reorder_qty = max(0, item.minimum_stock - item.current_stock)
            restock_list.append(
                RestockItem(
                    product_id=item.product_id,
                    product_name=item.product_name,
                    current_stock=item.current_stock,
                    minimum_stock=item.minimum_stock,
                    reorder_quantity=reorder_qty,
                    unit_cost=item.unit_cost,
                    supplier=item.supplier,
                )
            )
    return restock_list


# --- BaseTool Concrete Implementations ---

class InventoryLoaderTool(BaseTool):
    """Step 1 Tool: Load inventory records from a CSV file."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="inventory_loader",
            description="Loads and validates inventory records from a CSV file.",
        )

    def execute(
        self,
        csv_path: Optional[str] = None,
        file_path: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        target_path = csv_path or file_path or "data/sample_inventory.csv"
        records = read_and_validate_inventory_csv(target_path)
        return {
            "inventory_items": [r.model_dump() for r in records],
            "total_loaded": len(records),
            "csv_path": str(target_path),
            "summary": f"Loaded {len(records)} inventory item(s) from '{target_path}'.",
        }


class StockThresholdComparatorTool(BaseTool):
    """Step 2 Tool: Compare current stock with minimum threshold."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="stock_comparator",
            description="Compares current stock with minimum stock thresholds.",
        )

    def execute(
        self,
        inventory_items: Optional[List[Dict[str, Any]]] = None,
        last_output: Optional[Any] = None,
        threshold_override: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        items_raw = inventory_items
        if items_raw is None and isinstance(last_output, dict):
            items_raw = last_output.get("inventory_items")
        if items_raw is None:
            items_raw = []

        raw_override = threshold_override
        if raw_override is None:
            raw_override = (
                kwargs.get("threshold_override")
                if kwargs.get("threshold_override") is not None
                else (
                    kwargs.get("minimum_stock")
                    if kwargs.get("minimum_stock") is not None
                    else (
                        kwargs.get("stock_threshold_override")
                        if kwargs.get("stock_threshold_override") is not None
                        else (
                            kwargs.get("minimum_stock_override")
                            if kwargs.get("minimum_stock_override") is not None
                            else kwargs.get("minimum_threshold")
                        )
                    )
                )
            )
        eff_override = None
        if raw_override is not None:
            eff_override = parse_integer_threshold(raw_override, "Stock threshold override")

        compared = []
        low_count = 0
        for raw in items_raw:
            curr = raw.get("current_stock", 0)
            orig_min = raw.get("minimum_stock", 0)
            threshold = (
                eff_override
                if eff_override is not None
                else orig_min
            )
            is_low = curr < threshold
            if is_low:
                low_count += 1
            compared.append({
                **raw,
                "is_low_stock": is_low,
                "effective_threshold": threshold,
                "minimum_stock": orig_min,
            })

        return {
            "compared_items": compared,
            "summary": f"Compared {len(compared)} product(s) against minimum stock; {low_count} below threshold.",
        }


class LowStockIdentifierTool(BaseTool):
    """Step 3 Tool: Identify products whose current stock is below threshold."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="low_stock_identifier",
            description="Filters products identified as low stock.",
        )

    def execute(
        self,
        compared_items: Optional[List[Dict[str, Any]]] = None,
        last_output: Optional[Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        comp_raw = compared_items
        if comp_raw is None and isinstance(last_output, dict):
            comp_raw = last_output.get("compared_items")
        if comp_raw is None:
            comp_raw = []

        low_stock = [item for item in comp_raw if item.get("is_low_stock", False)]
        return {
            "low_stock_items": low_stock,
            "low_stock_count": len(low_stock),
            "summary": f"Identified {len(low_stock)} product(s) requiring restock.",
        }


class ReorderQuantityCalculatorTool(BaseTool):
    """Step 4 Tool: Calculate suggested reorder quantity (minimum_stock - current_stock)."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="reorder_calculator",
            description="Calculates reorder quantity for low stock items.",
        )

    def execute(
        self,
        low_stock_items: Optional[List[Dict[str, Any]]] = None,
        last_output: Optional[Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        items_raw = low_stock_items
        if items_raw is None and isinstance(last_output, dict):
            items_raw = last_output.get("low_stock_items")
        if items_raw is None:
            items_raw = []

        restock_list = []
        total_units = 0
        for raw in items_raw:
            curr = raw.get("current_stock", 0)
            orig_min = raw.get("minimum_stock", 0)
            effective_min = raw.get("effective_threshold", orig_min)
            # Authoritative reorder quantity: minimum_stock - current_stock
            reorder_qty = max(0, orig_min - curr)
            total_units += reorder_qty
            restock_list.append({
                "product_id": raw.get("product_id"),
                "product_name": raw.get("product_name"),
                "current_stock": curr,
                "minimum_stock": orig_min,
                "effective_threshold": effective_min,
                "reorder_quantity": reorder_qty,
                "unit_cost": raw.get("unit_cost", 0.0),
                "supplier": raw.get("supplier", ""),
            })

        return {
            "restock_items": restock_list,
            "summary": f"Calculated reorder quantities for {len(restock_list)} product(s) ({total_units} total units).",
        }


class RestockReportGeneratorTool(BaseTool):
    """Step 5 Tool: Generate structured restock list report."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="restock_reporter",
            description="Formats and outputs the final inventory restock list.",
        )

    def execute(
        self,
        restock_items: Optional[List[Dict[str, Any]]] = None,
        total_loaded: Optional[int] = None,
        last_output: Optional[Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        items_raw = restock_items
        if items_raw is None and isinstance(last_output, dict):
            items_raw = last_output.get("restock_items")
        if items_raw is None:
            items_raw = []

        total_checked = total_loaded if total_loaded is not None else len(items_raw)

        return {
            "products_requiring_restock": items_raw,
            "total_products_checked": total_checked,
            "restock_required_count": len(items_raw),
            "summary": (
                f"{len(items_raw)} of {total_checked} product(s) require restocking."
                if total_checked > 0
                else "No products checked."
            ),
        }

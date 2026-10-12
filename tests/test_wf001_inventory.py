"""Tests for WF001 Inventory Restock Check domain tools and logic."""

from pathlib import Path
import pytest

from app.tools.inventory import (
    InventoryItem,
    InventoryLoaderTool,
    LowStockIdentifierTool,
    ReorderQuantityCalculatorTool,
    RestockItem,
    RestockReportGeneratorTool,
    StockThresholdComparatorTool,
    calculate_restock_requirements,
    read_and_validate_inventory_csv,
)


@pytest.fixture
def sample_csv_path() -> Path:
    """Return path to data/sample_inventory.csv."""
    path = Path(__file__).parent.parent / "data" / "sample_inventory.csv"
    assert path.is_file(), f"Sample inventory CSV missing at {path}"
    return path


def test_multiple_products_requiring_restock(sample_csv_path: Path):
    """Test 1: Identify multiple products requiring restocking from sample data."""
    records = read_and_validate_inventory_csv(sample_csv_path)
    assert len(records) == 7

    restock_items = calculate_restock_requirements(records)
    assert len(restock_items) == 4

    pids = [item.product_id for item in restock_items]
    assert pids == ["PRD-001", "PRD-003", "PRD-005", "PRD-007"]


def test_product_exactly_at_minimum_stock_threshold(tmp_path: Path):
    """Test 2: A product exactly at its minimum stock threshold is NOT restocked."""
    csv_file = tmp_path / "threshold_inventory.csv"
    csv_file.write_text(
        "product_id,product_name,current_stock,minimum_stock,unit_cost,supplier\n"
        "PRD-EQ,Equal Stock Product,15,15,10.00,Supplier A\n"
    )

    records = read_and_validate_inventory_csv(csv_file)
    restock_items = calculate_restock_requirements(records)

    # current_stock == minimum_stock is not < minimum_stock
    assert len(restock_items) == 0


def test_product_with_zero_stock(tmp_path: Path):
    """Test 3: A product with zero stock has reorder_quantity equal to minimum_stock."""
    csv_file = tmp_path / "zero_stock_inventory.csv"
    csv_file.write_text(
        "product_id,product_name,current_stock,minimum_stock,unit_cost,supplier\n"
        "PRD-ZERO,Zero Stock Product,0,45,12.50,Supplier B\n"
    )

    records = read_and_validate_inventory_csv(csv_file)
    restock_items = calculate_restock_requirements(records)

    assert len(restock_items) == 1
    assert restock_items[0].current_stock == 0
    assert restock_items[0].minimum_stock == 45
    assert restock_items[0].reorder_quantity == 45


def test_empty_inventory_data(tmp_path: Path):
    """Test 4: Empty inventory CSV returns empty record list without errors."""
    csv_file = tmp_path / "empty_inventory.csv"
    csv_file.write_text(
        "product_id,product_name,current_stock,minimum_stock,unit_cost,supplier\n"
    )

    records = read_and_validate_inventory_csv(csv_file)
    assert len(records) == 0

    restock_items = calculate_restock_requirements(records)
    assert len(restock_items) == 0


def test_missing_inventory_file(tmp_path: Path):
    """Test 5a: Missing inventory file raises FileNotFoundError with clear message."""
    missing_file = tmp_path / "does_not_exist.csv"

    with pytest.raises(FileNotFoundError) as exc_info:
        read_and_validate_inventory_csv(missing_file)

    assert "not found" in str(exc_info.value).lower()


def test_malformed_inventory_missing_columns(tmp_path: Path):
    """Test 6a: Missing required columns raises ValueError."""
    bad_csv = tmp_path / "missing_cols.csv"
    # Missing 'supplier' column
    bad_csv.write_text(
        "product_id,product_name,current_stock,minimum_stock,unit_cost\n"
        "PRD-1,Widget,5,10,2.50\n"
    )

    with pytest.raises(ValueError) as exc_info:
        read_and_validate_inventory_csv(bad_csv)

    assert "supplier" in str(exc_info.value).lower()


def test_invalid_stock_values(tmp_path: Path):
    """Test 6b: Negative or non-numeric stock values raise ValueError with row info."""
    # Negative stock
    neg_csv = tmp_path / "negative_stock.csv"
    neg_csv.write_text(
        "product_id,product_name,current_stock,minimum_stock,unit_cost,supplier\n"
        "PRD-NEG,Bad Product,-5,10,2.50,Supplier A\n"
    )

    with pytest.raises(ValueError) as exc_info:
        read_and_validate_inventory_csv(neg_csv)

    assert "current_stock" in str(exc_info.value)
    assert "PRD-NEG" in str(exc_info.value)

    # Non-numeric stock
    str_csv = tmp_path / "string_stock.csv"
    str_csv.write_text(
        "product_id,product_name,current_stock,minimum_stock,unit_cost,supplier\n"
        "PRD-STR,Bad Product,ten,10,2.50,Supplier A\n"
    )

    with pytest.raises(ValueError) as exc_info_str:
        read_and_validate_inventory_csv(str_csv)

    assert "current_stock" in str(exc_info_str.value)


def test_correct_reorder_quantity_calculation():
    """Test 7: Verify exact reorder quantity formula: minimum_stock - current_stock."""
    items = [
        InventoryItem(
            product_id="P1", product_name="Item 1", current_stock=3, minimum_stock=10, unit_cost=5.0, supplier="S1"
        ),
        InventoryItem(
            product_id="P2", product_name="Item 2", current_stock=10, minimum_stock=10, unit_cost=5.0, supplier="S1"
        ),
        InventoryItem(
            product_id="P3", product_name="Item 3", current_stock=12, minimum_stock=10, unit_cost=5.0, supplier="S1"
        ),
        InventoryItem(
            product_id="P4", product_name="Item 4", current_stock=0, minimum_stock=20, unit_cost=5.0, supplier="S1"
        ),
    ]

    restock = calculate_restock_requirements(items)
    assert len(restock) == 2

    # P1: 10 - 3 = 7
    assert restock[0].product_id == "P1"
    assert restock[0].reorder_quantity == 7

    # P4: 20 - 0 = 20
    assert restock[1].product_id == "P4"
    assert restock[1].reorder_quantity == 20


def test_step_by_step_domain_tools_cascading(sample_csv_path: Path):
    """Test step tools cascading outputs through dictionary results."""
    loader = InventoryLoaderTool()
    comparator = StockThresholdComparatorTool()
    identifier = LowStockIdentifierTool()
    calculator = ReorderQuantityCalculatorTool()
    reporter = RestockReportGeneratorTool()

    step1 = loader.execute(csv_path=str(sample_csv_path))
    assert step1["total_loaded"] == 7

    step2 = comparator.execute(inventory_items=step1["inventory_items"])
    assert len(step2["compared_items"]) == 7

    step3 = identifier.execute(compared_items=step2["compared_items"])
    assert step3["low_stock_count"] == 4

    step4 = calculator.execute(low_stock_items=step3["low_stock_items"])
    assert len(step4["restock_items"]) == 4

    step5 = reporter.execute(
        restock_items=step4["restock_items"],
        total_loaded=step1["total_loaded"],
    )
    assert step5["restock_required_count"] == 4
    assert step5["total_products_checked"] == 7
    assert "4 of 7 product(s) require restocking" in step5["summary"]

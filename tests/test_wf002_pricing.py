"""Unit tests for WF002 — Product Price Validation domain tools and business logic."""

from pathlib import Path
import pytest

from app.tools.pricing import (
    InternalPriceRecord,
    PercentageDifferenceCalculatorTool,
    PriceComparatorTool,
    PriceDataLoaderTool,
    PriceExceptionFlaggerTool,
    ProductSkuMatcherTool,
    VendorPriceRecord,
    compare_and_flag_prices,
    load_internal_prices_csv,
    load_vendor_prices_csv,
    match_prices_by_sku,
)


def test_load_sample_price_csvs():
    """Verify loading real sample internal and vendor price files."""
    internal = load_internal_prices_csv("data/sample_internal_prices.csv")
    vendor = load_vendor_prices_csv("data/sample_vendor_prices.csv")

    assert len(internal) == 8
    assert len(vendor) == 8
    assert internal[0].sku == "SKU-001"
    assert internal[0].internal_price == 25.00
    assert vendor[0].sku == "SKU-001"
    assert vendor[0].vendor_price == 26.00


def test_threshold_boundary_strictly_greater_than_10_percent():
    """Verify decision logic: flag strictly when price difference exceeds 10%.

    - Exactly 10.0% difference (e.g., 40.0 vs 44.0 or 35.0 vs 38.5) must NOT be flagged.
    - Greater than 10.0% (e.g., 10.01% or 15.0%) MUST be flagged.
    """
    pairs = [
        # Exactly 10.0% higher: (44 - 40) / 40 * 100 = 10.0% -> NOT an exception
        {
            "sku": "SKU-BOUNDARY-1",
            "product_name": "Boundary Item Exact +10%",
            "vendor_name": "TestVendor",
            "internal_price": 40.00,
            "vendor_price": 44.00,
        },
        # Exactly 10.0% lower: (90 - 100) / 100 * 100 = 10.0% -> NOT an exception
        {
            "sku": "SKU-BOUNDARY-2",
            "product_name": "Boundary Item Exact -10%",
            "vendor_name": "TestVendor",
            "internal_price": 100.00,
            "vendor_price": 90.00,
        },
        # Strictly greater than 10% (10.02%): (110.02 - 100) / 100 * 100 = 10.02% -> EXCEPTION
        {
            "sku": "SKU-EXCEED-1",
            "product_name": "Exceeds Threshold Item",
            "vendor_name": "TestVendor",
            "internal_price": 100.00,
            "vendor_price": 110.02,
        },
        # Substantially greater (15%): -> EXCEPTION
        {
            "sku": "SKU-EXCEED-2",
            "product_name": "15% Higher Item",
            "vendor_name": "TestVendor",
            "internal_price": 80.00,
            "vendor_price": 92.00,
        },
    ]

    result = compare_and_flag_prices(pairs, threshold_percentage=10.0)
    assert result["exception_count"] == 2

    # Check status of boundary items
    item_by_sku = {p["sku"]: p for p in result["compared_products"]}
    assert item_by_sku["SKU-BOUNDARY-1"]["is_exception"] is False
    assert item_by_sku["SKU-BOUNDARY-1"]["validation_status"] == "COMPLIANT"

    assert item_by_sku["SKU-BOUNDARY-2"]["is_exception"] is False
    assert item_by_sku["SKU-BOUNDARY-2"]["validation_status"] == "COMPLIANT"

    # Check status of exceeded items
    assert item_by_sku["SKU-EXCEED-1"]["is_exception"] is True
    assert item_by_sku["SKU-EXCEED-1"]["validation_status"] == "EXCEPTION_EXCEEDS_10_PERCENT"

    assert item_by_sku["SKU-EXCEED-2"]["is_exception"] is True
    assert item_by_sku["SKU-EXCEED-2"]["validation_status"] == "EXCEPTION_EXCEEDS_10_PERCENT"


def test_negative_price_difference_exceeding_10_percent():
    """Verify that vendor price significantly lower (> 10% drop) is also flagged."""
    pairs = [
        {
            "sku": "SKU-004",
            "product_name": "27-inch 4K Monitor",
            "vendor_name": "VisionTech Displays",
            "internal_price": 300.00,
            "vendor_price": 255.00,  # -15%
        }
    ]
    result = compare_and_flag_prices(pairs, threshold_percentage=10.0)
    assert result["exception_count"] == 1
    item = result["compared_products"][0]
    assert item["price_difference"] == -45.00
    assert item["percentage_difference"] == 15.00
    assert item["is_exception"] is True


def test_sku_matching_detects_unmatched_records():
    """Verify unmatched vendor SKUs and unmatched internal SKUs are tracked."""
    internal = [
        InternalPriceRecord(sku="SKU-1", product_name="Item 1", internal_price=10.0),
        InternalPriceRecord(sku="SKU-2", product_name="Item 2", internal_price=20.0),
    ]
    vendor = [
        VendorPriceRecord(sku="SKU-1", vendor_name="Vendor A", vendor_price=10.5),
        VendorPriceRecord(sku="SKU-99", vendor_name="Vendor A", vendor_price=99.0),
    ]

    matched = match_prices_by_sku(internal, vendor)
    assert matched["match_count"] == 1
    assert len(matched["matched_pairs"]) == 1
    assert matched["matched_pairs"][0]["sku"] == "SKU-1"

    # SKU-99 only in vendor
    assert len(matched["unmatched_vendor"]) == 1
    assert matched["unmatched_vendor"][0]["sku"] == "SKU-99"

    # SKU-2 only in internal catalog
    assert len(matched["unmatched_internal"]) == 1
    assert matched["unmatched_internal"][0]["sku"] == "SKU-2"


def test_invalid_price_values_rejected(tmp_path: Path):
    """Verify that negative or non-numeric prices raise actionable errors."""
    bad_csv = tmp_path / "bad_prices.csv"
    bad_csv.write_text("sku,product_name,internal_price\nSKU-01,Product,INVALID_PRICE\n")

    with pytest.raises(ValueError, match="Invalid price value"):
        load_internal_prices_csv(bad_csv)

    zero_csv = tmp_path / "zero_price.csv"
    zero_csv.write_text("sku,product_name,internal_price\nSKU-01,Product,0.00\n")
    with pytest.raises(ValueError, match="Invalid price value"):
        load_internal_prices_csv(zero_csv)


def test_missing_price_csv_file():
    """Verify non-existent file produces FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_internal_prices_csv("data/non_existent_prices.csv")


def test_missing_sku_in_csv_rejected(tmp_path: Path):
    """Verify rows missing SKU are rejected during loading."""
    missing_sku_csv = tmp_path / "missing_sku.csv"
    missing_sku_csv.write_text("sku,product_name,internal_price\n,Product Without SKU,25.00\n")

    with pytest.raises(ValueError, match="Missing or empty SKU"):
        load_internal_prices_csv(missing_sku_csv)


def test_step_by_step_wf002_tools_cascading():
    """Test all 5 step tools executing sequentially and passing context data."""
    loader = PriceDataLoaderTool()
    matcher = ProductSkuMatcherTool()
    comparator = PriceComparatorTool()
    calculator = PercentageDifferenceCalculatorTool()
    flagger = PriceExceptionFlaggerTool()

    # Step 1: Load product prices
    out1 = loader.execute(
        internal_csv_path="data/sample_internal_prices.csv",
        vendor_csv_path="data/sample_vendor_prices.csv",
    )
    assert out1["total_internal"] == 8
    assert out1["total_vendor"] == 8

    # Step 2: match products by SKU
    out2 = matcher.execute(
        internal_prices=out1["internal_prices"],
        vendor_prices=out1["vendor_prices"],
    )
    assert out2["match_count"] == 7
    assert len(out2["unmatched_vendor"]) == 1
    assert len(out2["unmatched_internal"]) == 1

    # Step 3: compare internal and vendor prices
    out3 = comparator.execute(matched_pairs=out2["matched_pairs"])
    assert len(out3["compared_products"]) == 7

    # Step 4: calculate percentage difference
    out4 = calculator.execute(compared_products=out3["compared_products"])
    assert len(out4["price_evaluations"]) == 7

    # Step 5: flag exceptions
    out5 = flagger.execute(
        price_evaluations=out4["price_evaluations"],
        unmatched_vendor=out2["unmatched_vendor"],
        unmatched_internal=out2["unmatched_internal"],
        threshold=10.0,
    )
    assert out5["total_matched"] == 7
    assert out5["exception_count"] == 3  # SKU-002 (+15%), SKU-004 (-15%), SKU-006 (+25%)
    assert len(out5["unmatched_vendor_records"]) == 1
    assert len(out5["unmatched_internal_records"]) == 1

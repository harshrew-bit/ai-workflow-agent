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

@pytest.mark.parametrize("raw_price", ["nan", "inf", "-inf"])
def test_non_finite_internal_prices_rejected(tmp_path: Path, raw_price: str):
    csv_path = tmp_path / "non_finite_internal.csv"
    csv_path.write_text(
        f"sku,product_name,internal_price\nSKU-1,Test,{raw_price}\n"
    )

    with pytest.raises(ValueError, match="Invalid price value"):
        load_internal_prices_csv(csv_path)


@pytest.mark.parametrize("raw_price", ["nan", "inf", "-inf"])
def test_non_finite_vendor_prices_rejected(tmp_path: Path, raw_price: str):
    csv_path = tmp_path / "non_finite_vendor.csv"
    csv_path.write_text(
        f"sku,vendor_name,vendor_price\nSKU-1,Vendor,{raw_price}\n"
    )

    with pytest.raises(ValueError, match="Invalid vendor price"):
        load_vendor_prices_csv(csv_path)

def test_currency_mismatch_is_rejected():
    internal = [
        InternalPriceRecord(
            sku="SKU-1",
            product_name="Test Product",
            internal_price=100.0,
            currency="USD",
        )
    ]
    vendor = [
        VendorPriceRecord(
            sku="SKU-1",
            vendor_name="Test Vendor",
            vendor_price=110.0,
            currency="EUR",
        )
    ]

    with pytest.raises(ValueError, match="Currency mismatch"):
        match_prices_by_sku(internal, vendor)


def test_duplicate_internal_skus_are_rejected():
    internal = [
        InternalPriceRecord(
            sku="SKU-1", product_name="Product A", internal_price=100.0
        ),
        InternalPriceRecord(
            sku="sku-1", product_name="Product A duplicate", internal_price=120.0
        ),
    ]

    with pytest.raises(ValueError, match="Duplicate internal SKU"):
        match_prices_by_sku(internal, [])


def test_duplicate_vendor_skus_are_rejected():
    vendor = [
        VendorPriceRecord(
            sku="SKU-1", vendor_name="Vendor A", vendor_price=100.0
        ),
        VendorPriceRecord(
            sku="sku-1", vendor_name="Vendor B", vendor_price=110.0
        ),
    ]

    with pytest.raises(ValueError, match="Duplicate vendor SKU"):
        match_prices_by_sku([], vendor)

def test_wf002_flags_unrounded_percentage_above_threshold():
    """A raw difference above 10% must be flagged even if rounded to 10.0%."""
    comparator = PriceComparatorTool()
    calculator = PercentageDifferenceCalculatorTool()
    flagger = PriceExceptionFlaggerTool()

    # The actual difference is 10.004%, but its displayed value rounds to 10.0%.
    pairs = [
        {
            "sku": "EXACT-10",
            "product_name": "Exact boundary",
            "vendor_name": "Test",
            "internal_price": 100.00,
            "vendor_price": 110.00,
        },
        {
            "sku": "JUST-OVER",
            "product_name": "Just over boundary",
            "vendor_name": "Test",
            "internal_price": 100.00,
            "vendor_price": 110.004,
        },
    ]

    compared = comparator.execute(matched_pairs=pairs)
    calculated = calculator.execute(
        compared_products=compared["compared_products"]
    )
    result = flagger.execute(
        price_evaluations=calculated["price_evaluations"],
        unmatched_vendor=[],
        unmatched_internal=[],
        threshold=10.0,
    )

    evaluations = {
        item["sku"]: item
        for item in result["matched_products"]
    }

    assert evaluations["EXACT-10"]["percentage_difference"] == 10.0
    assert evaluations["EXACT-10"]["is_exception"] is False

    assert evaluations["JUST-OVER"]["percentage_difference"] == 10.0
    assert evaluations["JUST-OVER"]["is_exception"] is True


def test_boundary_decimal_precision_3_30_vs_3_63_and_3_64():
    """Verify exact Decimal boundary logic for 3.30 vs 3.63 and 3.64.

    3.30 + 10% is exactly 3.63:
      - 3.30 vs 3.63 has difference 0.33, which equals (3.30 * 10 / 100).
        Because threshold comparison is strictly greater than, this is COMPLIANT.
      - 3.30 vs 3.64 has difference 0.34, which exceeds 0.33 -> EXCEPTION.
      - 3.30 vs 2.97 has difference -0.33, absolute difference 0.33 -> COMPLIANT.
      - 3.30 vs 2.96 has difference -0.34, absolute difference 0.34 -> EXCEPTION.
    """
    pairs = [
        {
            "sku": "SKU-EXACT-UP",
            "product_name": "Item Exact +10%",
            "vendor_name": "Vendor A",
            "internal_price": 3.30,
            "vendor_price": 3.63,
        },
        {
            "sku": "SKU-OVER-UP",
            "product_name": "Item Over +10%",
            "vendor_name": "Vendor A",
            "internal_price": 3.30,
            "vendor_price": 3.64,
        },
        {
            "sku": "SKU-EXACT-DOWN",
            "product_name": "Item Exact -10%",
            "vendor_name": "Vendor A",
            "internal_price": 3.30,
            "vendor_price": 2.97,
        },
        {
            "sku": "SKU-OVER-DOWN",
            "product_name": "Item Over -10%",
            "vendor_name": "Vendor A",
            "internal_price": 3.30,
            "vendor_price": 2.96,
        },
    ]

    res = compare_and_flag_prices(pairs, threshold_percentage=10.0)
    items = {item["sku"]: item for item in res["compared_products"]}

    # Exact +10%: compliant
    assert items["SKU-EXACT-UP"]["price_difference"] == 0.33
    assert items["SKU-EXACT-UP"]["percentage_difference"] == 10.0
    assert items["SKU-EXACT-UP"]["is_exception"] is False
    assert items["SKU-EXACT-UP"]["validation_status"] == "COMPLIANT"

    # Over +10%: exception
    assert items["SKU-OVER-UP"]["price_difference"] == 0.34
    assert items["SKU-OVER-UP"]["percentage_difference"] == 10.3
    assert items["SKU-OVER-UP"]["is_exception"] is True
    assert items["SKU-OVER-UP"]["validation_status"] == "EXCEPTION_EXCEEDS_10_PERCENT"

    # Exact -10%: compliant
    assert items["SKU-EXACT-DOWN"]["price_difference"] == -0.33
    assert items["SKU-EXACT-DOWN"]["percentage_difference"] == 10.0
    assert items["SKU-EXACT-DOWN"]["is_exception"] is False
    assert items["SKU-EXACT-DOWN"]["validation_status"] == "COMPLIANT"

    # Over -10%: exception
    assert items["SKU-OVER-DOWN"]["price_difference"] == -0.34
    assert items["SKU-OVER-DOWN"]["percentage_difference"] == 10.3
    assert items["SKU-OVER-DOWN"]["is_exception"] is True
    assert items["SKU-OVER-DOWN"]["validation_status"] == "EXCEPTION_EXCEEDS_10_PERCENT"


def test_unquoted_comma_in_csv_rejected_with_line_number_and_guidance(tmp_path: Path):
    """Verify that unquoted commas (e.g., $1,200) raise actionable errors with line number."""
    csv_file = tmp_path / "unquoted_comma.csv"
    csv_file.write_text(
        "sku,product_name,internal_price,currency\n"
        "SKU-01,High-End Camera,$1,200.00,USD\n"
    )

    with pytest.raises(ValueError) as excinfo:
        load_internal_prices_csv(csv_file)

    err_msg = str(excinfo.value)
    assert "line 2 has 5 columns, expected 4" in err_msg
    assert "Unquoted commas inside values" in err_msg
    assert "values containing commas must be enclosed in quotes" in err_msg


def test_quoted_comma_currency_parsed_properly(tmp_path: Path):
    """Verify that properly quoted currency values with commas are parsed as positive Decimals."""
    csv_file = tmp_path / "quoted_comma.csv"
    csv_file.write_text(
        'sku,product_name,internal_price,currency\n'
        'SKU-01,High-End Camera,"$1,200.50",USD\n'
        'SKU-02,Studio Monitor,"$2,500",USD\n'
    )

    records = load_internal_prices_csv(csv_file)
    assert len(records) == 2
    assert records[0].sku == "SKU-01"
    assert records[0].internal_price == 1200.50
    assert records[1].sku == "SKU-02"
    assert records[1].internal_price == 2500.00


def test_blank_currency_in_csv_rejected(tmp_path: Path):
    """Verify that rows with empty or blank currency values are rejected."""
    csv_file = tmp_path / "blank_curr.csv"
    csv_file.write_text(
        "sku,product_name,internal_price,currency\n"
        "SKU-01,Valid Item,10.00,   \n"
    )

    with pytest.raises(ValueError, match="Missing or blank currency value"):
        load_internal_prices_csv(csv_file)


def test_duplicate_skus_in_csv_rejected(tmp_path: Path):
    """Verify duplicate SKUs are caught at CSV load time with row number."""
    int_csv = tmp_path / "dup_internal.csv"
    int_csv.write_text(
        "sku,product_name,internal_price\n"
        "SKU-01,Item 1,10.00\n"
        "sku-01,Item 2,12.00\n"
    )
    with pytest.raises(ValueError, match="Duplicate internal SKU detected on row 3"):
        load_internal_prices_csv(int_csv)

    ven_csv = tmp_path / "dup_vendor.csv"
    ven_csv.write_text(
        "sku,vendor_name,vendor_price\n"
        "SKU-01,Vendor A,10.00\n"
        "SKU-01,Vendor B,12.00\n"
    )
    with pytest.raises(ValueError, match="Duplicate vendor SKU detected on row 3"):
        load_vendor_prices_csv(ven_csv)


def test_no_raw_percentage_difference_leaked_in_output():
    """Ensure no internal fields like _raw_percentage_difference exist in outputs."""
    calculator = PercentageDifferenceCalculatorTool()
    flagger = PriceExceptionFlaggerTool()

    pairs = [
        {
            "sku": "SKU-1",
            "product_name": "Test",
            "vendor_name": "Vendor",
            "internal_price": 100.0,
            "vendor_price": 115.0,
        }
    ]

    calc_res = calculator.execute(compared_products=pairs)
    assert "_raw_percentage_difference" not in calc_res["price_evaluations"][0]

    flag_res = flagger.execute(
        price_evaluations=calc_res["price_evaluations"],
        unmatched_vendor=[],
        unmatched_internal=[],
    )
    for prod in flag_res["matched_products"]:
        assert "_raw_percentage_difference" not in prod
    for exc in flag_res["exceptions"]:
        assert "_raw_percentage_difference" not in exc


def test_price_exception_flagger_tool_ignores_15_percent_threshold_argument():
    """Verify that PriceExceptionFlaggerTool enforces fixed 10% policy and ignores threshold argument."""
    from decimal import Decimal

    flagger = PriceExceptionFlaggerTool()
    # 12% difference: 100.00 vs 112.00
    evaluations = [
        {
            "sku": "SKU-12PCT",
            "product_name": "12 Percent Item",
            "vendor_name": "Vendor A",
            "internal_price": Decimal("100.00"),
            "vendor_price": Decimal("112.00"),
            "price_difference": 12.0,
            "percentage_difference": 12.0,
        }
    ]

    # Passing threshold=15.0 to WF002 tool must NOT alter WF002's fixed 10% policy
    res = flagger.execute(
        price_evaluations=evaluations,
        unmatched_vendor=[],
        unmatched_internal=[],
        threshold=15.0,
    )

    assert res["exception_count"] == 1
    assert res["matched_products"][0]["is_exception"] is True
    assert res["matched_products"][0]["validation_status"] == "EXCEPTION_EXCEEDS_10_PERCENT"
    assert "10.0% threshold" in res["summary"]

    # In contrast, the standalone helper compare_and_flag_prices accepts custom threshold
    standalone_res = compare_and_flag_prices(
        [
            {
                "sku": "SKU-12PCT",
                "product_name": "12 Percent Item",
                "vendor_name": "Vendor A",
                "internal_price": Decimal("100.00"),
                "vendor_price": Decimal("112.00"),
            }
        ],
        threshold_percentage=15.0,
    )
    # Under standalone 15%, 12% is compliant
    assert standalone_res["exception_count"] == 0
    assert standalone_res["compared_products"][0]["is_exception"] is False
    assert standalone_res["compared_products"][0]["validation_status"] == "COMPLIANT"


def test_end_to_end_precision_preservation_via_csv(tmp_path: Path):
    """Prove exact source decimal values are preserved end-to-end from CSV input."""
    from decimal import Decimal

    int_csv = tmp_path / "int_exact.csv"
    int_csv.write_text(
        "sku,product_name,internal_price,currency\n"
        "SKU-PREC,Precision Sensor,100.00,USD\n"
    )
    ven_csv = tmp_path / "ven_exact.csv"
    ven_csv.write_text(
        "sku,vendor_name,vendor_price,currency\n"
        "SKU-PREC,Precision Vendor,110.004,USD\n"
    )

    internal_records = load_internal_prices_csv(int_csv)
    vendor_records = load_vendor_prices_csv(ven_csv)

    assert isinstance(internal_records[0].internal_price, Decimal)
    assert isinstance(vendor_records[0].vendor_price, Decimal)
    assert vendor_records[0].vendor_price == Decimal("110.004")

    # Step tools cascading
    loader = PriceDataLoaderTool()
    matcher = ProductSkuMatcherTool()
    comparator = PriceComparatorTool()
    calculator = PercentageDifferenceCalculatorTool()
    flagger = PriceExceptionFlaggerTool()

    loaded = loader.execute(internal_csv_path=str(int_csv), vendor_csv_path=str(ven_csv))
    matched = matcher.execute(
        internal_prices=loaded["internal_prices"],
        vendor_prices=loaded["vendor_prices"],
    )
    compared = comparator.execute(matched_pairs=matched["matched_pairs"])
    evaluated = calculator.execute(compared_products=compared["compared_products"])
    flagged = flagger.execute(
        price_evaluations=evaluated["price_evaluations"],
        unmatched_vendor=matched["unmatched_vendor"],
        unmatched_internal=matched["unmatched_internal"],
    )

    prod = flagged["matched_products"][0]
    assert isinstance(prod["internal_price"], Decimal)
    assert isinstance(prod["vendor_price"], Decimal)
    assert prod["internal_price"] == Decimal("100.00")
    assert prod["vendor_price"] == Decimal("110.004")
    assert str(prod["vendor_price"]) == "110.004"
    assert prod["is_exception"] is True
    assert prod["validation_status"] == "EXCEPTION_EXCEEDS_10_PERCENT"

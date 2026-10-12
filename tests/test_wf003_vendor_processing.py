"""Unit tests for WF003 — Vendor File Processing domain tools and validation logic."""

from pathlib import Path
import pytest

from app.tools.vendor_processing import (
    CleanDatasetProducerTool,
    ColumnDetectorTool,
    ColumnNormalizerTool,
    InvalidRowsIdentifierTool,
    RequiredFieldsValidatorTool,
    VendorFileReaderTool,
    detect_and_normalize_columns,
    normalize_header_name,
    read_vendor_file_records,
    validate_vendor_records,
)


def test_normalize_header_name_variations():
    """Verify supported column name synonyms normalize to canonical names."""
    assert normalize_header_name("Item_SKU") == "sku"
    assert normalize_header_name("product_sku") == "sku"
    assert normalize_header_name("Item_Title") == "product_name"
    assert normalize_header_name("Title") == "product_name"
    assert normalize_header_name("Unit_Price") == "price"
    assert normalize_header_name("Cost") == "price"
    assert normalize_header_name("Quantity_Available") == "stock"
    assert normalize_header_name("Product_Category") == "category"


def test_sample_vendor_catalog_processing():
    """Verify processing real sample vendor catalog with valid and invalid rows."""
    headers, rows = read_vendor_file_records("data/sample_vendor_catalog.csv")
    assert len(headers) == 5
    assert len(rows) == 8

    col_map, norm_rows = detect_and_normalize_columns(headers, rows)
    assert col_map["Item_SKU"] == "sku"
    assert col_map["Item_Title"] == "product_name"

    valid, invalid = validate_vendor_records(norm_rows)
    # Total 8 rows:
    # Row 1 (VND-101): valid
    # Row 2 (missing SKU): invalid
    # Row 3 (missing product_name): invalid
    # Row 4 (VND-104): valid
    # Row 5 (both blank): invalid
    # Row 6 (VND-106): valid
    # Row 7 (negative price): invalid
    # Row 8 (VND-108): valid
    assert len(valid) == 4
    assert len(invalid) == 4

    # Verify invalid row error diagnostics
    invalid_by_row = {inv.row_number: inv for inv in invalid}
    assert 2 in invalid_by_row
    assert any("SKU is blank or missing" in err for err in invalid_by_row[2].errors)

    assert 3 in invalid_by_row
    assert any("product_name is blank or missing" in err for err in invalid_by_row[3].errors)

    assert 5 in invalid_by_row
    assert len(invalid_by_row[5].errors) == 2  # both missing

    assert 7 in invalid_by_row
    assert any("price must be non-negative" in err for err in invalid_by_row[7].errors)


def test_input_file_is_not_overwritten(tmp_path: Path):
    """Verify that vendor file processing never overwrites or modifies the input file."""
    vendor_file = tmp_path / "original_vendor.csv"
    initial_content = "Item_SKU,Item_Title,Price\nVND-01,Product 1,29.99\n,Bad Product,10.00\n"
    vendor_file.write_text(initial_content, encoding="utf-8")

    # Run processing
    headers, rows = read_vendor_file_records(vendor_file)
    _, norm_rows = detect_and_normalize_columns(headers, rows)
    valid, invalid = validate_vendor_records(norm_rows)

    # Check file on disk is strictly unchanged
    assert vendor_file.read_text(encoding="utf-8") == initial_content
    assert len(valid) == 1
    assert len(invalid) == 1


def test_missing_vendor_file_handling():
    """Verify non-existent vendor file produces FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        read_vendor_file_records("data/non_existent_vendor_file.csv")


def test_step_by_step_wf003_tools_cascading():
    """Test all 6 step tools executing sequentially and passing context data."""
    reader = VendorFileReaderTool()
    detector = ColumnDetectorTool()
    normalizer = ColumnNormalizerTool()
    validator = RequiredFieldsValidatorTool()
    identifier = InvalidRowsIdentifierTool()
    producer = CleanDatasetProducerTool()

    # Step 1: Read file
    out1 = reader.execute(file_path="data/sample_vendor_catalog.csv")
    assert out1["total_rows_read"] == 8

    # Step 2: detect columns
    out2 = detector.execute(raw_headers=out1["raw_headers"])
    assert "sku" in out2["detected_columns"]
    assert "product_name" in out2["detected_columns"]

    # Step 3: normalize column names
    out3 = normalizer.execute(
        raw_headers=out1["raw_headers"],
        raw_rows=out1["raw_rows"],
    )
    assert len(out3["normalized_rows"]) == 8

    # Step 4: validate required fields
    out4 = validator.execute(normalized_rows=out3["normalized_rows"])
    assert out4["valid_count"] == 4
    assert out4["invalid_count"] == 4

    # Step 5: identify invalid rows
    out5 = identifier.execute(
        preliminary_valid=out4["preliminary_valid"],
        preliminary_invalid=out4["preliminary_invalid"],
    )
    assert out5["valid_count"] == 4
    assert out5["invalid_count"] == 4

    # Step 6: produce cleaned dataset
    out6 = producer.execute(
        valid_rows=out5["valid_rows"],
        invalid_rows=out5["invalid_rows"],
    )
    assert out6["total_processed"] == 8
    assert len(out6["cleaned_records"]) == 4
    assert len(out6["invalid_records"]) == 4
    assert "4 valid record(s) cleaned" in out6["summary"]

"""Unit tests for WF006 — Duplicate Product Detection domain tools and similarity logic."""

from pathlib import Path
import pytest

from app.tools.duplicate_detection import (
    AttributeComparatorTool,
    CatalogLoaderTool,
    CatalogNormalizerTool,
    DuplicateConfidenceAssignerTool,
    DuplicateGrouperTool,
    IdentifierComparatorTool,
    detect_duplicates,
    load_catalog_csv,
    normalize_catalog_products,
)


def test_load_sample_catalog():
    """Verify loading real sample product catalog CSV."""
    products = load_catalog_csv("data/sample_products_catalog.csv")
    assert len(products) == 9
    assert products[0].sku == "SKU-1001"
    assert products[0].product_name == "Logitech MX Master 3S Wireless Mouse"


def test_exact_sku_duplicate_is_definite_duplicate():
    """Verify Decision Logic: Exact SKU match is a definite duplicate."""
    products = load_catalog_csv("data/sample_products_catalog.csv")
    norm_products = normalize_catalog_products(products)
    duplicates = detect_duplicates(norm_products)

    exact_sku_dupes = [d for d in duplicates if d.match_type == "exact_sku_match"]
    assert len(exact_sku_dupes) >= 1

    first_exact = exact_sku_dupes[0]
    assert first_exact.confidence == "definite"
    assert first_exact.similarity_score == 1.0
    assert "sku" in first_exact.matching_fields
    assert first_exact.primary_sku == "SKU-1001"
    assert first_exact.duplicate_sku == "SKU-1001"


def test_high_attribute_similarity_is_likely_duplicate():
    """Verify Decision Logic: High attribute similarity is a likely/possible duplicate."""
    products = load_catalog_csv("data/sample_products_catalog.csv")
    norm_products = normalize_catalog_products(products)
    duplicates = detect_duplicates(norm_products)

    likely_dupes = [d for d in duplicates if d.confidence == "likely"]
    assert len(likely_dupes) >= 1

    # Check Keychron or Sony likely duplicate pair
    keychron_dupe = next(
        (d for d in likely_dupes if "Keychron" in d.primary_name and "Keychron" in d.duplicate_name),
        None,
    )
    assert keychron_dupe is not None
    assert keychron_dupe.similarity_score >= 0.75
    assert keychron_dupe.confidence == "likely"
    assert "brand" in keychron_dupe.matching_fields


def test_distinct_products_are_not_grouped_as_duplicates():
    """Verify distinct products (e.g. MacBook Pro vs Dell Monitor) are never marked duplicates."""
    products = load_catalog_csv("data/sample_products_catalog.csv")
    norm_products = normalize_catalog_products(products)
    duplicates = detect_duplicates(norm_products)

    for d in duplicates:
        # A MacBook Pro must never be marked duplicate of a Dell monitor or Anker powerbank
        if "MacBook" in d.primary_name:
            assert "Dell" not in d.duplicate_name
            assert "Anker" not in d.duplicate_name
        if "Dell" in d.primary_name:
            assert "MacBook" not in d.duplicate_name
            assert "Anker" not in d.duplicate_name


def test_missing_catalog_file_handling():
    """Verify FileNotFoundError for missing catalog file."""
    with pytest.raises(FileNotFoundError):
        load_catalog_csv("data/non_existent_catalog.csv")


def test_step_by_step_wf006_tools_cascading():
    """Test all 6 step tools executing sequentially and compiling final report."""
    loader = CatalogLoaderTool()
    normalizer = CatalogNormalizerTool()
    id_comparator = IdentifierComparatorTool()
    attr_comparator = AttributeComparatorTool()
    grouper = DuplicateGrouperTool()
    assigner = DuplicateConfidenceAssignerTool()

    # Step 1: Load products
    out1 = loader.execute(catalog_csv_path="data/sample_products_catalog.csv")
    assert out1["total_products_loaded"] == 9

    # Step 2: normalize names/SKUs
    out2 = normalizer.execute(raw_products=out1["raw_products"])
    assert len(out2["normalized_products"]) == 9

    # Step 3: compare identifiers
    out3 = id_comparator.execute(normalized_products=out2["normalized_products"])
    assert out3["exact_duplicate_sku_count"] >= 1

    # Step 4: compare product attributes
    out4 = attr_comparator.execute(normalized_products=out2["normalized_products"])
    assert out4["total_candidates_found"] >= 2

    # Step 5: group likely duplicates
    out5 = grouper.execute(duplicate_candidates=out4["duplicate_candidates"])
    assert len(out5["grouped_duplicates"]["definite"]) >= 1
    assert len(out5["grouped_duplicates"]["likely"]) >= 1

    # Step 6: assign confidence
    out6 = assigner.execute(
        duplicate_candidates=out4["duplicate_candidates"],
        grouped_duplicates=out5["grouped_duplicates"],
        total_products_loaded=out1["total_products_loaded"],
    )
    assert out6["definite_duplicates_count"] >= 1
    assert out6["likely_duplicates_count"] >= 1
    assert "methodology" in out6
    assert "Matching Method" in out6["methodology"]

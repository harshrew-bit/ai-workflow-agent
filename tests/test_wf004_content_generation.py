"""Unit tests for WF004 — Product Description Generator domain tools and generation logic."""

import pytest

from app.tools.content_generation import (
    MetaDescriptionGeneratorTool,
    ProductAttributeValidatorTool,
    ProductDescriptionGeneratorTool,
    SeoTitleGeneratorTool,
    ShortDescriptionGeneratorTool,
    synthesize_meta_description,
    synthesize_product_description,
    synthesize_seo_title,
    synthesize_short_description,
    validate_product_content_attributes,
)


def test_full_attributes_content_generation():
    """Verify content generation when all product attributes are supplied."""
    attrs = validate_product_content_attributes(
        product_name="UltraLite Wireless Mechanical Keyboard",
        category="Computer Peripherals",
        material="Aircraft-grade Aluminum",
        color="Midnight Black",
        target_audience="Software Engineers and Gamers",
        attributes={"connectivity": "Tri-mode 2.4G/BT/USB-C", "switch_type": "Hot-swappable linear"},
    )

    assert attrs.product_name == "UltraLite Wireless Mechanical Keyboard"
    assert len(attrs.missing_attributes) == 0

    full_desc = synthesize_product_description(attrs)
    short_desc = synthesize_short_description(attrs)
    seo_title = synthesize_seo_title(attrs)
    meta_desc = synthesize_meta_description(attrs)

    assert "UltraLite Wireless Mechanical Keyboard" in full_desc
    assert "Aircraft-grade Aluminum" in full_desc
    assert "Midnight Black" in full_desc
    assert "Software Engineers and Gamers" in full_desc

    assert len(seo_title) <= 60
    assert len(meta_desc) <= 160
    assert "UltraLite" in seo_title


def test_missing_attributes_never_invented_and_explicitly_marked():
    """Verify Decision Logic: never invent attributes; explicitly mark missing information."""
    attrs = validate_product_content_attributes(
        product_name="Minimalist Wooden Desk Lamp",
        category="Home Decor",
        # material, color, target_audience, extra attributes omitted!
    )

    assert "material" in attrs.missing_attributes
    assert "color" in attrs.missing_attributes
    assert "target_audience" in attrs.missing_attributes

    full_desc = synthesize_product_description(attrs)

    # Verify no hallucinated materials or colors
    assert "Aluminum" not in full_desc
    assert "Steel" not in full_desc
    assert "Plastic" not in full_desc
    assert "Black" not in full_desc

    # Verify omitted attributes note is present
    assert "omitted to prevent hallucination" in full_desc


def test_missing_product_name_raises_value_error():
    """Verify that omitting mandatory product_name triggers a clear validation error."""
    with pytest.raises(ValueError, match="Required attribute 'product_name' is missing or empty"):
        validate_product_content_attributes(product_name="")

    with pytest.raises(ValueError, match="Required attribute 'product_name' is missing or empty"):
        validate_product_content_attributes(product_name=None)


def test_step_by_step_wf004_tools_cascading():
    """Test all 5 step tools executing sequentially and compiling final output."""
    val_tool = ProductAttributeValidatorTool()
    desc_tool = ProductDescriptionGeneratorTool()
    short_tool = ShortDescriptionGeneratorTool()
    seo_tool = SeoTitleGeneratorTool()
    meta_tool = MetaDescriptionGeneratorTool()

    # Step 1: Validate required attributes
    out1 = val_tool.execute(
        product_name="Ergonomic Vertical Mouse",
        category="Office Electronics",
        material="Soft-touch Matte Polymer",
        color="Slate Gray",
        target_audience="Office Workers",
    )
    assert out1["product_name"] == "Ergonomic Vertical Mouse"
    assert "category" in out1["provided_attributes"]

    # Step 2: create product description
    out2 = desc_tool.execute(
        product_name=out1["product_name"],
        category=out1["category"],
        material=out1["material"],
        color=out1["color"],
        target_audience=out1["target_audience"],
    )
    assert "Ergonomic Vertical Mouse" in out2["product_description"]

    # Step 3: generate short description
    out3 = short_tool.execute(
        product_name=out1["product_name"],
        category=out1["category"],
        material=out1["material"],
        color=out1["color"],
        target_audience=out1["target_audience"],
    )
    assert len(out3["short_description"]) > 10

    # Step 4: generate SEO title
    out4 = seo_tool.execute(
        product_name=out1["product_name"],
        category=out1["category"],
    )
    assert len(out4["seo_title"]) <= 60

    # Step 5: generate meta description
    out5 = meta_tool.execute(
        product_name=out1["product_name"],
        category=out1["category"],
        material=out1["material"],
        color=out1["color"],
        target_audience=out1["target_audience"],
        product_description=out2["product_description"],
        short_description=out3["short_description"],
        seo_title=out4["seo_title"],
    )
    assert out5["is_simulated"] is True
    assert out5["generator_provider"] == "simulated_content_generator"
    assert len(out5["meta_description"]) <= 160
    assert out5["product_name"] == "Ergonomic Vertical Mouse"
    assert "product_description" in out5
    assert "short_description" in out5
    assert "seo_title" in out5

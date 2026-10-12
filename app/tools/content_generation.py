"""WF004 — Product Description Generator domain logic and execution tools.

Generates product descriptions, short descriptions, SEO titles, and meta descriptions
based on provided attributes (name, category, material, color, target audience, attributes).
Enforces WF004 Decision Logic: Never invent missing product attributes; explicitly mark
missing information, and clearly label simulated/offline generation.
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from app.tools.base import BaseTool, ToolMetadata


class ValidatedProductAttributes(BaseModel):
    """Structured container for validated product attributes."""

    product_name: str
    category: Optional[str] = None
    material: Optional[str] = None
    color: Optional[str] = None
    target_audience: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)
    provided_attributes: Dict[str, Any] = Field(default_factory=dict)
    missing_attributes: List[str] = Field(default_factory=list)


def validate_product_content_attributes(
    product_name: Optional[str] = None,
    category: Optional[str] = None,
    material: Optional[str] = None,
    color: Optional[str] = None,
    target_audience: Optional[str] = None,
    attributes: Optional[Union[Dict[str, Any], List[str], str]] = None,
    **kwargs: Any,
) -> ValidatedProductAttributes:
    """Validate product attributes strictly enforcing WF004 decision logic:

    - product_name is mandatory; raises ValueError if missing.
    - optional attributes are tracked; missing ones are recorded in missing_attributes.
    """
    clean_name = str(product_name or "").strip()
    if not clean_name:
        raise ValueError(
            "Required attribute 'product_name' is missing or empty. "
            "A valid product name is required to generate descriptions."
        )

    clean_category = str(category).strip() if category else None
    clean_material = str(material).strip() if material else None
    clean_color = str(color).strip() if color else None
    clean_audience = str(target_audience).strip() if target_audience else None

    # Parse extra attributes
    parsed_attrs: Dict[str, Any] = {}
    if isinstance(attributes, dict):
        parsed_attrs = {str(k): str(v) for k, v in attributes.items()}
    elif isinstance(attributes, (list, tuple)):
        for idx, item in enumerate(attributes, start=1):
            parsed_attrs[f"feature_{idx}"] = str(item).strip()
    elif isinstance(attributes, str) and attributes.strip():
        # Split comma-separated features
        parts = [p.strip() for p in attributes.split(",") if p.strip()]
        for idx, part in enumerate(parts, start=1):
            if ":" in part:
                k, v = part.split(":", 1)
                parsed_attrs[k.strip()] = v.strip()
            else:
                parsed_attrs[f"feature_{idx}"] = part

    provided: Dict[str, Any] = {"product_name": clean_name}
    missing: List[str] = []

    if clean_category:
        provided["category"] = clean_category
    else:
        missing.append("category")

    if clean_material:
        provided["material"] = clean_material
    else:
        missing.append("material")

    if clean_color:
        provided["color"] = clean_color
    else:
        missing.append("color")

    if clean_audience:
        provided["target_audience"] = clean_audience
    else:
        missing.append("target_audience")

    if parsed_attrs:
        provided["attributes"] = parsed_attrs
    else:
        missing.append("attributes")

    return ValidatedProductAttributes(
        product_name=clean_name,
        category=clean_category,
        material=clean_material,
        color=clean_color,
        target_audience=clean_audience,
        attributes=parsed_attrs,
        provided_attributes=provided,
        missing_attributes=missing,
    )


def synthesize_product_description(attrs: ValidatedProductAttributes) -> str:
    """Generate detailed product description based ONLY on provided attributes."""
    sentences = [f"Introducing the {attrs.product_name}."]

    if attrs.category:
        sentences.append(f"Designed specifically for the {attrs.category} category.")

    details: List[str] = []
    if attrs.material:
        details.append(f"constructed from premium {attrs.material}")
    if attrs.color:
        details.append(f"available in a sleek {attrs.color} finish")
    if details:
        sentences.append(f"Expertly crafted, this item is {' and '.join(details)}.")

    if attrs.target_audience:
        sentences.append(f"Tailored to meet the demanding requirements of {attrs.target_audience}.")

    if attrs.attributes:
        feature_strs = [f"{k}: {v}" for k, v in attrs.attributes.items()]
        sentences.append(f"Key specifications include: {', '.join(feature_strs)}.")

    if attrs.missing_attributes:
        omitted_str = ", ".join(attrs.missing_attributes)
        sentences.append(f"[Note: Unspecified attributes ({omitted_str}) were omitted to prevent hallucination.]")

    return " ".join(sentences)


def synthesize_short_description(attrs: ValidatedProductAttributes) -> str:
    """Generate concise 1-2 sentence overview strictly from provided facts."""
    core = f"The {attrs.product_name}"
    descriptors: List[str] = []
    if attrs.color:
        descriptors.append(f"in {attrs.color}")
    if attrs.material:
        descriptors.append(f"made of {attrs.material}")

    if descriptors:
        core += f" ({', '.join(descriptors)})"

    if attrs.target_audience:
        return f"{core} delivers exceptional performance tailored for {attrs.target_audience}."
    elif attrs.category:
        return f"{core} provides dependable reliability in the {attrs.category} space."
    return f"{core} offers reliable quality and modern functionality."


def synthesize_seo_title(attrs: ValidatedProductAttributes) -> str:
    """Generate click-worthy SEO title tag under 60 characters."""
    parts = [attrs.product_name]
    if attrs.category and len(attrs.product_name) + len(attrs.category) + 3 <= 55:
        parts.append(attrs.category)
    elif attrs.material and len(attrs.product_name) + len(attrs.material) + 3 <= 55:
        parts.append(attrs.material)

    title = " | ".join(parts)
    if len(title) > 60:
        return title[:57] + "..."
    return title


def synthesize_meta_description(attrs: ValidatedProductAttributes) -> str:
    """Generate compelling meta description tag under 160 characters."""
    desc = f"Discover the {attrs.product_name}."
    if attrs.target_audience:
        desc += f" Perfect for {attrs.target_audience}."
    elif attrs.category:
        desc += f" Top quality in {attrs.category}."

    if attrs.color and len(desc) < 120:
        desc += f" Available in {attrs.color}."
    if attrs.material and len(desc) < 120:
        desc += f" Premium {attrs.material} construction."

    desc += " Shop now!"
    if len(desc) > 160:
        return desc[:157] + "..."
    return desc


# ==============================================================================
# Step Tools for Generic Execution Engine
# ==============================================================================


class ProductAttributeValidatorTool(BaseTool):
    """Step 1 Tool: Validate required attributes."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="attribute_validator",
            description="Validate required product attributes and detect missing fields.",
        )

    def execute(
        self,
        product_name: Optional[str] = None,
        category: Optional[str] = None,
        material: Optional[str] = None,
        color: Optional[str] = None,
        target_audience: Optional[str] = None,
        attributes: Optional[Union[Dict[str, Any], List[str], str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        val = validate_product_content_attributes(
            product_name=product_name,
            category=category,
            material=material,
            color=color,
            target_audience=target_audience,
            attributes=attributes,
            **kwargs,
        )
        missing_count = len(val.missing_attributes)
        return {
            "product_name": val.product_name,
            "category": val.category,
            "material": val.material,
            "color": val.color,
            "target_audience": val.target_audience,
            "attributes": val.attributes,
            "provided_attributes": val.provided_attributes,
            "missing_attributes": val.missing_attributes,
            "summary": f"Validated '{val.product_name}' ({len(val.provided_attributes)} provided, {missing_count} missing attribute(s)).",
        }


class ProductDescriptionGeneratorTool(BaseTool):
    """Step 2 Tool: create product description."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="product_description_generator",
            description="Generate full product description strictly grounded on provided attributes.",
        )

    def execute(
        self,
        product_name: Optional[str] = None,
        category: Optional[str] = None,
        material: Optional[str] = None,
        color: Optional[str] = None,
        target_audience: Optional[str] = None,
        attributes: Optional[Union[Dict[str, Any], List[str], str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        val = validate_product_content_attributes(
            product_name=product_name,
            category=category,
            material=material,
            color=color,
            target_audience=target_audience,
            attributes=attributes,
        )
        description = synthesize_product_description(val)
        return {
            "product_description": description,
            "summary": f"Generated product description ({len(description.split())} words).",
        }


class ShortDescriptionGeneratorTool(BaseTool):
    """Step 3 Tool: generate short description."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="short_description_generator",
            description="Generate concise 1-2 sentence short description.",
        )

    def execute(
        self,
        product_name: Optional[str] = None,
        category: Optional[str] = None,
        material: Optional[str] = None,
        color: Optional[str] = None,
        target_audience: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        val = validate_product_content_attributes(
            product_name=product_name,
            category=category,
            material=material,
            color=color,
            target_audience=target_audience,
        )
        short_desc = synthesize_short_description(val)
        return {
            "short_description": short_desc,
            "summary": f"Generated short description ({len(short_desc)} chars).",
        }


class SeoTitleGeneratorTool(BaseTool):
    """Step 4 Tool: generate SEO title."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="seo_title_generator",
            description="Generate click-worthy SEO title under 60 characters.",
        )

    def execute(
        self,
        product_name: Optional[str] = None,
        category: Optional[str] = None,
        material: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        val = validate_product_content_attributes(
            product_name=product_name, category=category, material=material
        )
        seo_title = synthesize_seo_title(val)
        return {
            "seo_title": seo_title,
            "summary": f"Generated SEO title: '{seo_title}' ({len(seo_title)} chars).",
        }


class MetaDescriptionGeneratorTool(BaseTool):
    """Step 5 Tool: generate meta description and bundle final content package."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="meta_description_generator",
            description="Generate meta description under 160 characters and compile full content bundle.",
        )

    def execute(
        self,
        product_name: Optional[str] = None,
        category: Optional[str] = None,
        material: Optional[str] = None,
        color: Optional[str] = None,
        target_audience: Optional[str] = None,
        attributes: Optional[Union[Dict[str, Any], List[str], str]] = None,
        product_description: Optional[str] = None,
        short_description: Optional[str] = None,
        seo_title: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        val = validate_product_content_attributes(
            product_name=product_name,
            category=category,
            material=material,
            color=color,
            target_audience=target_audience,
            attributes=attributes,
        )
        meta_desc = synthesize_meta_description(val)

        full_desc = product_description or synthesize_product_description(val)
        short_desc = short_description or synthesize_short_description(val)
        seo_t = seo_title or synthesize_seo_title(val)

        return {
            "product_name": val.product_name,
            "product_description": full_desc,
            "short_description": short_desc,
            "seo_title": seo_t,
            "meta_description": meta_desc,
            "provided_attributes": val.provided_attributes,
            "missing_attributes": val.missing_attributes,
            "is_simulated": True,
            "generator_provider": "simulated_content_generator",
            "summary": f"Successfully generated all SEO content for '{val.product_name}' (simulated mode).",
        }

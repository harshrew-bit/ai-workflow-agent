"""WF006 — Duplicate Product Detection domain logic and execution tools.

Provides genuine domain execution for detecting exact SKU duplicates and
high-similarity name/attribute duplicates across a product catalog, strictly
abiding by the decision logic in data/workflows.xlsx.
"""

import csv
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from pydantic import BaseModel, Field

from app.tools.base import BaseTool, ToolMetadata


class CatalogProduct(BaseModel):
    """Raw product catalog item."""

    product_id: str
    sku: str
    product_name: str
    category: str
    brand: str
    price: float


class NormalizedProduct(BaseModel):
    """Product with normalized text tokens for similarity evaluation."""

    product_id: str
    raw_sku: str
    normalized_sku: str
    raw_name: str
    normalized_name: str
    tokens: Set[str]
    category: str
    brand: str
    price: float


class DuplicateCandidate(BaseModel):
    """Pair of potential duplicate products with confidence and reasoning."""

    primary_product_id: str
    primary_sku: str
    primary_name: str
    duplicate_product_id: str
    duplicate_sku: str
    duplicate_name: str
    match_type: str  # "exact_sku_match" or "high_attribute_similarity" or "possible_similarity"
    confidence: str  # "definite", "likely", "possible"
    similarity_score: float  # 0.0 to 1.0
    matching_fields: List[str]
    explanation: str


def _tokenize(text: str) -> Set[str]:
    """Tokenize and clean string into normalized word set."""
    clean = re.sub(r"[^\w\s]", " ", text.lower())
    words = clean.split()
    # Filter short noise words
    return {w for w in words if len(w) > 1}


def _calculate_similarity(tokens1: Set[str], tokens2: Set[str]) -> float:
    """Compute Dice token overlap coefficient between two token sets."""
    if not tokens1 or not tokens2:
        return 0.0
    intersection = len(tokens1.intersection(tokens2))
    return round((2.0 * intersection) / (len(tokens1) + len(tokens2)), 4)


def load_catalog_csv(file_path: Union[str, Path]) -> List[CatalogProduct]:
    """Load product catalog from CSV safely."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Catalog file not found at '{path}'")

    products: List[CatalogProduct] = []
    with open(path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        headers = []
        for line in reader:
            if not line or not any(line):
                continue
            if line[0].strip().startswith("#"):
                continue
            if not headers:
                headers = [h.strip().lower() for h in line]
            else:
                row_dict = {
                    headers[i]: line[i].strip() if i < len(line) else ""
                    for i in range(len(headers))
                }
                raw_price = row_dict.get("price", "0").replace("$", "").replace(",", "")
                try:
                    price = float(raw_price)
                except ValueError:
                    price = 0.0

                products.append(
                    CatalogProduct(
                        product_id=row_dict.get("product_id", ""),
                        sku=row_dict.get("sku", ""),
                        product_name=row_dict.get("product_name", ""),
                        category=row_dict.get("category", "General"),
                        brand=row_dict.get("brand", "Generic"),
                        price=price,
                    )
                )
    return products


def normalize_catalog_products(products: List[CatalogProduct]) -> List[NormalizedProduct]:
    """Normalize names and SKUs for comparison."""
    normalized: List[NormalizedProduct] = []
    for p in products:
        norm_sku = re.sub(r"[\s\-_]", "", p.sku.upper())
        norm_name = p.product_name.lower().strip()
        tokens = _tokenize(norm_name)
        if p.brand:
            tokens.update(_tokenize(p.brand))

        normalized.append(
            NormalizedProduct(
                product_id=p.product_id,
                raw_sku=p.sku,
                normalized_sku=norm_sku,
                raw_name=p.product_name,
                normalized_name=norm_name,
                tokens=tokens,
                category=p.category.lower().strip(),
                brand=p.brand.lower().strip(),
                price=p.price,
            )
        )
    return normalized


def detect_duplicates(
    products: List[NormalizedProduct],
) -> List[DuplicateCandidate]:
    """Identify duplicate product pairs adhering to WF006 Decision Logic:

    - Exact SKU match is a definite duplicate (confidence: definite, score: 1.0).
    - High attribute/name similarity is a possible/likely duplicate.
    - Low similarity products are not grouped as duplicates.
    """
    candidates: List[DuplicateCandidate] = []
    n = len(products)

    for i in range(n):
        for j in range(i + 1, n):
            p1 = products[i]
            p2 = products[j]

            # 1. Exact SKU match -> Definite duplicate
            if p1.normalized_sku and p1.normalized_sku == p2.normalized_sku:
                candidates.append(
                    DuplicateCandidate(
                        primary_product_id=p1.product_id,
                        primary_sku=p1.raw_sku,
                        primary_name=p1.raw_name,
                        duplicate_product_id=p2.product_id,
                        duplicate_sku=p2.raw_sku,
                        duplicate_name=p2.raw_name,
                        match_type="exact_sku_match",
                        confidence="definite",
                        similarity_score=1.0,
                        matching_fields=["sku"],
                        explanation="Definite duplicate: Identical SKU found across multiple records.",
                    )
                )
                continue

            # 2. Attribute and Token similarity
            similarity = _calculate_similarity(p1.tokens, p2.tokens)
            same_brand = bool(p1.brand and p2.brand and p1.brand == p2.brand)
            same_category = bool(p1.category and p2.category and p1.category == p2.category)

            # High attribute similarity threshold
            if similarity >= 0.75 and same_brand:
                matching_fields = ["product_name", "brand"]
                if same_category:
                    matching_fields.append("category")
                candidates.append(
                    DuplicateCandidate(
                        primary_product_id=p1.product_id,
                        primary_sku=p1.raw_sku,
                        primary_name=p1.raw_name,
                        duplicate_product_id=p2.product_id,
                        duplicate_sku=p2.raw_sku,
                        duplicate_name=p2.raw_name,
                        match_type="high_attribute_similarity",
                        confidence="likely",
                        similarity_score=round(similarity, 2),
                        matching_fields=matching_fields,
                        explanation=f"Likely duplicate: High token similarity ({similarity:.0%}) with matching brand '{p1.brand.title()}'.",
                    )
                )
            elif similarity >= 0.65:
                # Moderate similarity -> Possible duplicate
                candidates.append(
                    DuplicateCandidate(
                        primary_product_id=p1.product_id,
                        primary_sku=p1.raw_sku,
                        primary_name=p1.raw_name,
                        duplicate_product_id=p2.product_id,
                        duplicate_sku=p2.raw_sku,
                        duplicate_name=p2.raw_name,
                        match_type="possible_attribute_similarity",
                        confidence="possible",
                        similarity_score=round(similarity, 2),
                        matching_fields=["product_name"],
                        explanation=f"Possible duplicate: Moderate name overlap ({similarity:.0%}); manual verification recommended.",
                    )
                )

    return candidates


# ==============================================================================
# Step Tools for Generic Execution Engine
# ==============================================================================


class CatalogLoaderTool(BaseTool):
    """Step 1 Tool: Load products."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="catalog_loader",
            description="Load product catalog records from CSV file.",
        )

    def execute(
        self,
        catalog_csv_path: Optional[str] = None,
        file_path: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        default_path = Path("data/sample_products_catalog.csv")
        target_path = Path(catalog_csv_path or file_path or default_path)

        products = load_catalog_csv(target_path)
        return {
            "raw_products": [p.model_dump() for p in products],
            "total_products_loaded": len(products),
            "summary": f"Loaded {len(products)} product(s) from '{target_path.name}'.",
        }


class CatalogNormalizerTool(BaseTool):
    """Step 2 Tool: normalize names/SKUs."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="catalog_normalizer",
            description="Normalize product names, SKUs, and tokens for similarity comparison.",
        )

    def execute(
        self,
        raw_products: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        items = [CatalogProduct(**p) for p in (raw_products or [])]
        norm = normalize_catalog_products(items)
        # Store for subsequent steps
        return {
            "normalized_products": [
                {
                    "product_id": p.product_id,
                    "raw_sku": p.raw_sku,
                    "normalized_sku": p.normalized_sku,
                    "raw_name": p.raw_name,
                    "normalized_name": p.normalized_name,
                    "tokens": list(p.tokens),
                    "category": p.category,
                    "brand": p.brand,
                    "price": p.price,
                }
                for p in norm
            ],
            "summary": f"Normalized {len(norm)} catalog product records.",
        }


class IdentifierComparatorTool(BaseTool):
    """Step 3 Tool: compare identifiers."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="identifier_comparator",
            description="Identify exact SKU duplicates across catalog records.",
        )

    def execute(
        self,
        normalized_products: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        items = normalized_products or []
        sku_map: Dict[str, List[Dict[str, Any]]] = {}
        exact_sku_duplicates: List[Dict[str, Any]] = []

        for p in items:
            sku = p.get("normalized_sku", "")
            if not sku:
                continue
            if sku not in sku_map:
                sku_map[sku] = []
            sku_map[sku].append(p)

        for sku, group in sku_map.items():
            if len(group) > 1:
                exact_sku_duplicates.append({
                    "sku": sku,
                    "duplicate_count": len(group),
                    "products": [g["product_id"] for g in group],
                })

        return {
            "exact_sku_matches": exact_sku_duplicates,
            "exact_duplicate_sku_count": len(exact_sku_duplicates),
            "summary": f"Identified {len(exact_sku_duplicates)} exact duplicate SKU group(s).",
        }


class AttributeComparatorTool(BaseTool):
    """Step 4 Tool: compare product attributes."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="attribute_comparator",
            description="Compare product name tokens, brand, and category for likely duplicates.",
        )

    def execute(
        self,
        normalized_products: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        raw_list = normalized_products or []
        norm_objs = [
            NormalizedProduct(
                product_id=p["product_id"],
                raw_sku=p["raw_sku"],
                normalized_sku=p["normalized_sku"],
                raw_name=p["raw_name"],
                normalized_name=p["normalized_name"],
                tokens=set(p.get("tokens", [])),
                category=p["category"],
                brand=p["brand"],
                price=p["price"],
            )
            for p in raw_list
        ]

        candidates = detect_duplicates(norm_objs)
        return {
            "duplicate_candidates": [c.model_dump() for c in candidates],
            "total_candidates_found": len(candidates),
            "summary": f"Found {len(candidates)} duplicate candidate pair(s).",
        }


class DuplicateGrouperTool(BaseTool):
    """Step 5 Tool: group likely duplicates."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="duplicate_grouper",
            description="Group duplicate candidate pairs into cohesive duplicate clusters.",
        )

    def execute(
        self,
        duplicate_candidates: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        candidates = duplicate_candidates or []
        # Group by match type
        definite_group = [c for c in candidates if c.get("confidence") == "definite"]
        likely_group = [c for c in candidates if c.get("confidence") == "likely"]
        possible_group = [c for c in candidates if c.get("confidence") == "possible"]

        return {
            "grouped_duplicates": {
                "definite": definite_group,
                "likely": likely_group,
                "possible": possible_group,
            },
            "summary": f"Grouped duplicates: {len(definite_group)} definite, {len(likely_group)} likely, {len(possible_group)} possible.",
        }


class DuplicateConfidenceAssignerTool(BaseTool):
    """Step 6 Tool: assign confidence and produce final duplicate detection report."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="duplicate_confidence_assigner",
            description="Assign confidence ratings, document limitations, and produce final report.",
        )

    def execute(
        self,
        duplicate_candidates: Optional[List[Dict[str, Any]]] = None,
        grouped_duplicates: Optional[Dict[str, Any]] = None,
        total_products_loaded: int = 0,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        candidates = duplicate_candidates or []
        definite_count = sum(1 for c in candidates if c.get("confidence") == "definite")
        likely_count = sum(1 for c in candidates if c.get("confidence") == "likely")
        possible_count = sum(1 for c in candidates if c.get("confidence") == "possible")

        summary_msg = (
            f"Detected {len(candidates)} duplicate group(s) across catalog: "
            f"{definite_count} definite (exact SKU), {likely_count} likely (high similarity), "
            f"{possible_count} possible."
        )

        matching_method_docs = (
            "Matching Method: (1) Exact normalized SKU equality marks definite duplicates. "
            "(2) Token Dice similarity >= 0.75 with matching brand marks likely duplicates. "
            "(3) Token Dice similarity between 0.65-0.74 marks possible duplicates. "
            "Limitations: Token-based matching does not parse semantic synonyms (e.g. 'lap desk' vs 'bed tray') "
            "and requires manual review for possible duplicates."
        )

        return {
            "duplicate_candidates": candidates,
            "total_duplicates_found": len(candidates),
            "definite_duplicates_count": definite_count,
            "likely_duplicates_count": likely_count,
            "possible_duplicates_count": possible_count,
            "methodology": matching_method_docs,
            "limitations": matching_method_docs,
            "summary": summary_msg,
        }

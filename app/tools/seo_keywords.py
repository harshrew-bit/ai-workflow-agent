"""Domain tools for WF008 — SEO Keyword Classification.

Steps:
1. Read keywords
2. remove duplicates
3. classify search intent
4. map keywords to categories
5. identify high-priority keywords
6. export results
"""

import csv
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field

from app.tools.base import BaseTool, ToolMetadata


class KeywordRecord(BaseModel):
    """Normalized keyword record."""
    keyword: str
    search_volume: int = 0
    cpc: float = 0.0
    competition: str = "Low"
    intent: Optional[str] = None
    category: Optional[str] = None
    target_page: Optional[str] = None
    priority: Optional[str] = None
    priority_reasoning: Optional[str] = None


def _load_keywords_csv(file_path: Path) -> List[Dict[str, Any]]:
    """Load keywords from a CSV file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Keyword file not found at '{file_path}'")

    records: List[Dict[str, Any]] = []
    with file_path.open("r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        headers: Optional[List[str]] = None
        for raw_row in reader:
            if not raw_row or not any(field.strip() for field in raw_row):
                continue
            if raw_row[0].strip().startswith("#"):
                continue
            if headers is None:
                headers = [h.strip().lower() for h in raw_row]
                continue

            row_dict: Dict[str, Any] = {}
            for h, val in zip(headers, raw_row):
                row_dict[h] = val.strip()

            kw_text = row_dict.get("keyword") or row_dict.get("keywords") or row_dict.get("query")
            if not kw_text:
                continue

            vol_raw = row_dict.get("search_volume") or row_dict.get("volume", "0")
            try:
                search_vol = int(float(vol_raw))
            except ValueError:
                search_vol = 0

            cpc_raw = row_dict.get("cpc", "0.0")
            try:
                cpc = float(cpc_raw.replace("$", ""))
            except ValueError:
                cpc = 0.0

            comp = row_dict.get("competition", "Medium")

            records.append({
                "keyword": kw_text,
                "search_volume": search_vol,
                "cpc": cpc,
                "competition": comp,
            })
    return records


class KeywordReaderTool(BaseTool):
    """Step 1 Tool: Read keywords."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="keyword_reader",
            description="Read keyword list from a CSV file or direct input list.",
        )

    def execute(
        self,
        keyword_file_path: Optional[str] = None,
        keywords: Optional[Union[List[str], str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        raw_records: List[Dict[str, Any]] = []

        if keyword_file_path:
            path = Path(keyword_file_path)
            raw_records = _load_keywords_csv(path)
        elif keywords:
            if isinstance(keywords, str):
                items = [k.strip() for k in re.split(r"[,;\n]+", keywords) if k.strip()]
            else:
                items = [str(k).strip() for k in keywords if str(k).strip()]
            for it in items:
                raw_records.append({
                    "keyword": it,
                    "search_volume": 1000,
                    "cpc": 1.0,
                    "competition": "Medium",
                })
        else:
            default_path = Path("data/sample_keywords.csv")
            if default_path.exists():
                raw_records = _load_keywords_csv(default_path)
            else:
                raise ValueError("No keyword file or keyword list provided and default sample file not found.")

        return {
            "raw_keywords": raw_records,
            "total_keywords_read": len(raw_records),
            "summary": f"Read {len(raw_records)} keyword record(s).",
        }


class KeywordDeduplicatorTool(BaseTool):
    """Step 2 Tool: remove duplicates."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="keyword_deduplicator",
            description="Normalize keyword casing and remove duplicate entries.",
        )

    def execute(
        self,
        raw_keywords: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        records = raw_keywords or []
        dedup_map: Dict[str, Dict[str, Any]] = {}
        duplicates_removed = 0

        for r in records:
            kw_raw = r.get("keyword", "")
            norm_key = re.sub(r"\s+", " ", kw_raw).strip().lower()
            if not norm_key:
                continue

            if norm_key in dedup_map:
                duplicates_removed += 1
                # Preserve the higher search volume or cpc
                existing = dedup_map[norm_key]
                if r.get("search_volume", 0) > existing.get("search_volume", 0):
                    existing["search_volume"] = r.get("search_volume", 0)
                if r.get("cpc", 0.0) > existing.get("cpc", 0.0):
                    existing["cpc"] = r.get("cpc", 0.0)
            else:
                dedup_map[norm_key] = {
                    "keyword": norm_key,
                    "search_volume": r.get("search_volume", 0),
                    "cpc": r.get("cpc", 0.0),
                    "competition": r.get("competition", "Medium"),
                }

        unique_records = list(dedup_map.values())
        return {
            "deduplicated_keywords": unique_records,
            "duplicates_removed": duplicates_removed,
            "total_unique_keywords": len(unique_records),
            "summary": f"Deduplicated keyword list: {len(unique_records)} unique keywords ({duplicates_removed} duplicates removed).",
        }


class IntentClassifierTool(BaseTool):
    """Step 3 Tool: classify search intent."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="intent_classifier",
            description="Classify keywords into informational, commercial, transactional, or navigational intent.",
        )

    def execute(
        self,
        deduplicated_keywords: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        records = deduplicated_keywords or []
        classified: List[Dict[str, Any]] = []

        transactional_patterns = [
            r"\b(buy|order|purchase|cheap|price|discount|coupon|deal|sale|shop|store)\b"
        ]
        commercial_patterns = [
            r"\b(best|top|vs|versus|review|reviews|compare|comparison|alternative|recommended)\b"
        ]
        navigational_patterns = [
            r"\b(official|website|login|portal|support|account|homepage|app)\b"
        ]
        informational_patterns = [
            r"\b(how|what|why|where|guide|tutorial|tips|learn|setup|fix|definition|meaning)\b"
        ]

        intent_counts = {
            "transactional": 0,
            "commercial": 0,
            "navigational": 0,
            "informational": 0,
        }

        for r in records:
            kw = r["keyword"].lower()
            intent = "informational"  # default fallback

            if any(re.search(p, kw) for p in transactional_patterns):
                intent = "transactional"
            elif any(re.search(p, kw) for p in commercial_patterns):
                intent = "commercial"
            elif any(re.search(p, kw) for p in navigational_patterns):
                intent = "navigational"
            elif any(re.search(p, kw) for p in informational_patterns):
                intent = "informational"
            else:
                # Secondary heuristic: if contains specific brand and product words with intent to acquire
                if "wireless" in kw or "keyboard" in kw or "mouse" in kw or "headphones" in kw:
                    intent = "commercial"
                else:
                    intent = "informational"

            intent_counts[intent] = intent_counts.get(intent, 0) + 1
            rec_copy = dict(r)
            rec_copy["intent"] = intent
            classified.append(rec_copy)

        return {
            "classified_keywords": classified,
            "intent_counts": intent_counts,
            "summary": (
                f"Classified {len(classified)} keyword(s): "
                f"{intent_counts.get('transactional', 0)} transactional, "
                f"{intent_counts.get('commercial', 0)} commercial, "
                f"{intent_counts.get('informational', 0)} informational, "
                f"{intent_counts.get('navigational', 0)} navigational."
            ),
        }


class CategoryMapperTool(BaseTool):
    """Step 4 Tool: map keywords to categories."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="category_mapper",
            description="Map keywords to product categories and recommended target page URLs.",
        )

    def execute(
        self,
        classified_keywords: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        records = classified_keywords or []
        mapped: List[Dict[str, Any]] = []
        category_counts: Dict[str, int] = {}

        for r in records:
            kw = r["keyword"].lower()
            intent = r.get("intent", "informational")

            # Determine category
            if any(w in kw for w in ["keyboard", "typing", "keychron"]):
                category = "Keyboards & Input"
                base_slug = "keyboards"
            elif any(w in kw for w in ["mouse", "mice", "mx master", "vertical mouse"]):
                category = "Mice & Ergonomics"
                base_slug = "mice"
            elif any(w in kw for w in ["headphone", "audio", "sony", "wh-1000xm5", "bose"]):
                category = "Audio & Headphones"
                base_slug = "audio"
            elif any(w in kw for w in ["chair", "desk", "office"]):
                category = "Office Furniture & Ergonomics"
                base_slug = "furniture"
            elif any(w in kw for w in ["docking", "dock", "usb-c", "hub"]):
                category = "Docks & Connectivity"
                base_slug = "accessories"
            else:
                category = "General Tech"
                base_slug = "products"

            category_counts[category] = category_counts.get(category, 0) + 1

            # Determine recommended target page based on intent and category
            if intent == "transactional":
                target_page = f"/products/{base_slug}"
            elif intent == "commercial":
                target_page = f"/collections/{base_slug}"
            elif intent == "navigational":
                target_page = f"/brand/{base_slug}" if "official" in kw else "/support"
            else:  # informational
                kw_slug = re.sub(r"[^a-z0-9]+", "-", kw).strip("-")
                target_page = f"/guides/{kw_slug}"

            rec_copy = dict(r)
            rec_copy["category"] = category
            rec_copy["target_page"] = target_page
            mapped.append(rec_copy)

        return {
            "mapped_keywords": mapped,
            "category_counts": category_counts,
            "summary": f"Mapped {len(mapped)} keyword(s) across {len(category_counts)} product category/categories.",
        }


class PriorityIdentifierTool(BaseTool):
    """Step 5 Tool: identify high-priority keywords."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="priority_identifier",
            description="Identify keyword priorities (High, Medium, Low) based on commercial intent and volume.",
        )

    def execute(
        self,
        mapped_keywords: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        records = mapped_keywords or []
        prioritized: List[Dict[str, Any]] = []

        high_count = 0
        med_count = 0
        low_count = 0

        for r in records:
            intent = r.get("intent", "informational")
            vol = r.get("search_volume", 0)

            # Explainable priority logic
            if intent == "transactional" or (intent == "commercial" and vol >= 15000):
                priority = "HIGH"
                reasoning = "High commercial conversion intent or high search volume."
                high_count += 1
            elif intent == "commercial" or (intent == "informational" and vol >= 8000):
                priority = "MEDIUM"
                reasoning = "Moderate consideration intent or substantial informational discovery volume."
                med_count += 1
            else:
                priority = "LOW"
                reasoning = "Navigational or lower-volume informational discovery."
                low_count += 1

            rec_copy = dict(r)
            rec_copy["priority"] = priority
            rec_copy["priority_reasoning"] = reasoning
            prioritized.append(rec_copy)

        return {
            "prioritized_keywords": prioritized,
            "high_priority_count": high_count,
            "medium_priority_count": med_count,
            "low_priority_count": low_count,
            "summary": f"Assigned priorities: {high_count} HIGH, {med_count} MEDIUM, {low_count} LOW.",
        }


class ResultsExporterTool(BaseTool):
    """Step 6 Tool: export results."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="results_exporter",
            description="Compile and export structured keyword classification report.",
        )

    def execute(
        self,
        prioritized_keywords: Optional[List[Dict[str, Any]]] = None,
        intent_counts: Optional[Dict[str, int]] = None,
        category_counts: Optional[Dict[str, int]] = None,
        high_priority_count: int = 0,
        medium_priority_count: int = 0,
        low_priority_count: int = 0,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        records = prioritized_keywords or []

        # Top keywords by priority
        high_priority_list = [r for r in records if r.get("priority") == "HIGH"]

        summary_msg = (
            f"Successfully processed and classified {len(records)} keyword(s). "
            f"Found {len(high_priority_list)} high-priority keyword(s) for immediate content/landing page optimization."
        )

        return {
            "total_keywords": len(records),
            "high_priority_count": high_priority_count,
            "medium_priority_count": medium_priority_count,
            "low_priority_count": low_priority_count,
            "intent_counts": intent_counts or {},
            "category_counts": category_counts or {},
            "keyword_records": records,
            "high_priority_recommendations": high_priority_list[:5],
            "is_simulated": True,
            "summary": summary_msg,
        }

"""Unit and step-by-step tests for WF008 — SEO Keyword Classification."""

from pathlib import Path
import pytest

from app.tools.seo_keywords import (
    CategoryMapperTool,
    IntentClassifierTool,
    KeywordDeduplicatorTool,
    KeywordReaderTool,
    PriorityIdentifierTool,
    ResultsExporterTool,
    _load_keywords_csv,
)


def test_load_sample_keywords_csv():
    """Verify loading sample keywords CSV."""
    records = _load_keywords_csv(Path("data/sample_keywords.csv"))
    assert len(records) >= 10
    kws = [r["keyword"] for r in records]
    assert "how to clean mechanical keyboard" in kws
    assert "buy keychron k2 wireless" in kws


def test_deduplication_removes_duplicate_keywords():
    """Verify deduplication ignores case and whitespace differences."""
    reader = KeywordReaderTool()
    dedup = KeywordDeduplicatorTool()

    raw = reader.execute(keyword_file_path="data/sample_keywords.csv")["raw_keywords"]
    res = dedup.execute(raw_keywords=raw)

    assert res["duplicates_removed"] >= 1
    assert res["total_unique_keywords"] < len(raw)

    unique_kws = [r["keyword"] for r in res["deduplicated_keywords"]]
    # Should only appear once in unique list
    assert unique_kws.count("buy keychron k2 wireless") == 1


def test_intent_classification_all_intents():
    """Verify classification of informational, commercial, transactional, navigational intents."""
    classifier = IntentClassifierTool()

    sample_items = [
        {"keyword": "how to clean mechanical keyboard", "search_volume": 8000, "cpc": 0.5},
        {"keyword": "best mechanical keyboard for coding", "search_volume": 20000, "cpc": 1.8},
        {"keyword": "buy keychron k2 wireless", "search_volume": 14000, "cpc": 2.2},
        {"keyword": "logitech official website login", "search_volume": 9000, "cpc": 0.8},
    ]

    res = classifier.execute(deduplicated_keywords=sample_items)
    classified = res["classified_keywords"]

    intent_map = {r["keyword"]: r["intent"] for r in classified}
    assert intent_map["how to clean mechanical keyboard"] == "informational"
    assert intent_map["best mechanical keyboard for coding"] == "commercial"
    assert intent_map["buy keychron k2 wireless"] == "transactional"
    assert intent_map["logitech official website login"] == "navigational"


def test_category_and_target_page_mapping():
    """Verify keyword mapping to product categories and URLs."""
    mapper = CategoryMapperTool()

    items = [
        {"keyword": "buy keychron k2 wireless", "intent": "transactional"},
        {"keyword": "best wireless mouse review", "intent": "commercial"},
        {"keyword": "how to clean mechanical keyboard", "intent": "informational"},
    ]

    res = mapper.execute(classified_keywords=items)
    mapped = res["mapped_keywords"]

    m_map = {r["keyword"]: r for r in mapped}
    assert m_map["buy keychron k2 wireless"]["category"] == "Keyboards & Input"
    assert m_map["buy keychron k2 wireless"]["target_page"] == "/products/keyboards"

    assert m_map["best wireless mouse review"]["category"] == "Mice & Ergonomics"
    assert m_map["best wireless mouse review"]["target_page"] == "/collections/mice"

    assert m_map["how to clean mechanical keyboard"]["category"] == "Keyboards & Input"
    assert "/guides/" in m_map["how to clean mechanical keyboard"]["target_page"]


def test_priority_assignment_logic():
    """Verify priority assignment based on intent and volume."""
    prioritizer = PriorityIdentifierTool()

    items = [
        {"keyword": "buy keychron k2", "intent": "transactional", "search_volume": 12000},
        {"keyword": "top noise cancelling headphones 2026", "intent": "commercial", "search_volume": 25000},
        {"keyword": "logitech support portal", "intent": "navigational", "search_volume": 2000},
    ]

    res = prioritizer.execute(mapped_keywords=items)
    prioritized = res["prioritized_keywords"]

    p_map = {r["keyword"]: r["priority"] for r in prioritized}
    assert p_map["buy keychron k2"] == "HIGH"
    assert p_map["top noise cancelling headphones 2026"] == "HIGH"
    assert p_map["logitech support portal"] == "LOW"


def test_missing_keyword_file_handling():
    """Verify error raised when keyword file does not exist."""
    reader = KeywordReaderTool()
    with pytest.raises(FileNotFoundError):
        reader.execute(keyword_file_path="data/nonexistent_keywords.csv")


def test_step_by_step_wf008_cascading():
    """Verify step-by-step tool cascading for WF008."""
    step1 = KeywordReaderTool().execute(keyword_file_path="data/sample_keywords.csv")
    assert step1["total_keywords_read"] > 0

    step2 = KeywordDeduplicatorTool().execute(raw_keywords=step1["raw_keywords"])
    assert step2["total_unique_keywords"] > 0

    step3 = IntentClassifierTool().execute(deduplicated_keywords=step2["deduplicated_keywords"])
    assert len(step3["classified_keywords"]) == step2["total_unique_keywords"]

    step4 = CategoryMapperTool().execute(classified_keywords=step3["classified_keywords"])
    assert len(step4["mapped_keywords"]) == len(step3["classified_keywords"])

    step5 = PriorityIdentifierTool().execute(mapped_keywords=step4["mapped_keywords"])
    assert len(step5["prioritized_keywords"]) == len(step4["mapped_keywords"])

    step6 = ResultsExporterTool().execute(
        prioritized_keywords=step5["prioritized_keywords"],
        intent_counts=step3["intent_counts"],
        category_counts=step4["category_counts"],
        high_priority_count=step5["high_priority_count"],
        medium_priority_count=step5["medium_priority_count"],
        low_priority_count=step5["low_priority_count"],
    )
    assert step6["total_keywords"] == len(step5["prioritized_keywords"])
    assert step6["is_simulated"] is True
    assert len(step6["high_priority_recommendations"]) > 0

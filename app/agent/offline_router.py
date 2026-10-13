"""Deterministic offline workflow router matching requests against workbook metadata."""

import re
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from app.agent.router import RoutingDecision, WorkflowRouter
from app.models.workflow import WorkflowDefinition

STOPWORDS: Set[str] = {
    "a", "an", "the", "in", "on", "at", "for", "to", "of", "and", "or", "is",
    "are", "was", "were", "be", "been", "this", "that", "it", "with", "from",
    "by", "as", "into", "through", "about", "above", "after", "all", "any",
    "both", "each", "few", "more", "most", "other", "some", "such", "no",
    "nor", "not", "only", "own", "same", "so", "than", "too", "very", "can",
    "will", "just", "should", "now", "d", "ll", "m", "o", "re", "ve", "y",
    "user", "users", "asks", "ask", "manager", "agent", "provides", "provide",
    "uploads", "upload", "check", "please", "want", "need", "like", "get",
    "help", "show", "tell", "me", "our", "we", "us", "these", "those", "where",
    "which", "what", "how", "when", "who", "why", "run", "execute", "new",
}

SYNONYMS: Dict[str, str] = {
    "failing": "fail",
    "failure": "fail",
    "failures": "fail",
    "failed": "fail",
    "fails": "fail",
    "successes": "success",
    "successful": "success",
    "restocking": "restock",
    "restocks": "restock",
    "reorder": "restock",
    "reorders": "restock",
    "stock": "inventory",
    "stocks": "inventory",
    "pricing": "price",
    "prices": "price",
    "priced": "price",
    "cost": "price",
    "costs": "price",
    "costing": "price",
    "supplier": "vendor",
    "suppliers": "vendor",
    "vendors": "vendor",
    "spreadsheet": "csv",
    "spreadsheets": "csv",
    "files": "file",
    "orders": "order",
    "ordered": "order",
    "ordering": "order",
    "shipments": "shipment",
    "shipping": "shipment",
    "shipped": "shipment",
    "tracking": "track",
    "tracked": "track",
    "tracks": "track",
    "duplicates": "duplicate",
    "duplication": "duplicate",
    "duplicated": "duplicate",
    "campaigns": "campaign",
    "briefs": "brief",
    "briefing": "brief",
    "keywords": "keyword",
    "keyword": "keyword",
    "search": "seo",
    "searches": "seo",
    "tasks": "task",
    "employee": "employee",
    "employees": "employee",
    "developer": "employee",
    "developers": "employee",
    "engineer": "employee",
    "engineers": "employee",
    "worker": "employee",
    "workers": "employee",
    "assigning": "assign",
    "assignment": "assign",
    "assignments": "assign",
    "assigned": "assign",
    "allocating": "assign",
    "allocation": "assign",
    "descriptions": "description",
    "desc": "description",
    "pipeline": "workflow",
    "pipelines": "workflow",
    "execution": "perform",
    "performance": "perform",
    "performing": "perform",
    "health": "perform",
    "logs": "log",
    "logging": "log",
}


def normalize_token(token: str) -> str:
    """Normalize a word token via lowercasing, stemming, and synonym mapping."""
    t = token.lower().strip()
    if not t:
        return ""
    if t in SYNONYMS:
        return SYNONYMS[t]
    if t.endswith("ies") and len(t) > 4:
        t = t[:-3] + "y"
    elif t.endswith("es") and len(t) > 3:
        t = t[:-2]
    elif t.endswith("s") and not t.endswith("ss") and len(t) > 2:
        t = t[:-1]
    elif t.endswith("ing") and len(t) > 4:
        t = t[:-3]
    elif t.endswith("ed") and len(t) > 3:
        t = t[:-2]
    return SYNONYMS.get(t, t)


def tokenize(text: str) -> List[str]:
    """Extract clean, normalized, non-stopword tokens from arbitrary text."""
    raw_tokens = re.findall(r"[a-zA-Z0-9_-]+", text or "")
    normalized: List[str] = []
    for raw in raw_tokens:
        norm = normalize_token(raw)
        if norm and norm not in STOPWORDS and len(norm) > 1:
            normalized.append(norm)
    return normalized


def extract_inputs_from_query(query: str, workflow_id: Optional[str] = None) -> Dict[str, Any]:
    """Extract explicit identifiers (order ID, email, csv path) from query text."""
    extracted: Dict[str, Any] = {}
    if not query:
        return extracted

    # Extract Order ID (e.g. ORD-1001, ORD-999)
    order_match = re.search(r"\b(ORD-\d+)\b", query, re.IGNORECASE)
    if order_match:
        extracted["order_id"] = order_match.group(1).upper()

    # Extract Email address
    email_match = re.search(
        r"\b([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\b", query
    )
    if email_match:
        extracted["customer_email"] = email_match.group(1)

    # Extract CSV file path if explicitly mentioned
    csv_match = re.search(r"\b([a-zA-Z0-9_./\\-]+\.csv)\b", query, re.IGNORECASE)
    if csv_match:
        extracted["file_path"] = csv_match.group(1)

    return extracted


class OfflineWorkflowRouter(WorkflowRouter):
    """Deterministic, workbook-driven offline workflow router.

    Uses explainable weighted token matching against workflow triggers,
    names, parsed steps, and required tools when no live LLM API key
    is configured.
    """

    def __init__(self, match_threshold: float = 3.0) -> None:
        self.match_threshold: float = match_threshold

    def score_workflows(
        self,
        query: str,
        available_workflows: Sequence[WorkflowDefinition],
    ) -> List[Tuple[WorkflowDefinition, float, Set[str]]]:
        """Score each workflow against query tokens.

        Returns a list of tuples (workflow, score, matched_tokens) sorted by score descending.
        """
        q_tokens = set(tokenize(query))
        if not q_tokens:
            return [(wf, 0.0, set()) for wf in available_workflows]

        results: List[Tuple[WorkflowDefinition, float, Set[str]]] = []
        for wf in available_workflows:
            trig_tokens = set(tokenize(wf.trigger))
            name_tokens = set(tokenize(wf.workflow_name))
            step_tokens = set(tokenize(" ".join(wf.parsed_steps)))
            tools_tokens = set(tokenize(wf.tools_required))

            matched: Set[str] = set()
            score = 0.0
            for tok in q_tokens:
                w = 0.0
                if tok in trig_tokens:
                    w = max(w, 3.5)
                if tok in name_tokens:
                    w = max(w, 2.5)
                if tok in step_tokens:
                    w = max(w, 1.5)
                if tok in tools_tokens:
                    w = max(w, 1.0)
                if w > 0:
                    score += w
                    matched.add(tok)
            results.append((wf, score, matched))

        results.sort(key=lambda item: item[1], reverse=True)
        return results

    def route(
        self,
        query: str,
        available_workflows: Sequence[WorkflowDefinition],
    ) -> RoutingDecision:
        """Route a user request to the best matching workflow definition offline."""
        clean_query = (query or "").strip()

        if not clean_query:
            return RoutingDecision(
                workflow_id=None,
                confidence=0.0,
                reasoning="Empty query provided. Offline routing requires input text.",
                requires_clarification=True,
                routing_mode="offline",
            )

        if not available_workflows:
            return RoutingDecision(
                workflow_id=None,
                confidence=0.0,
                reasoning="No registered workflows available in the system catalog.",
                requires_clarification=True,
                routing_mode="offline",
            )

        ranked = self.score_workflows(clean_query, available_workflows)
        top_wf, top_score, top_matched = ranked[0]
        second_score = ranked[1][1] if len(ranked) > 1 else 0.0

        # Confident match: score meets threshold and strictly beats any competitor
        if top_score >= self.match_threshold and top_score > second_score:
            confidence = min(0.99, max(0.70, 0.65 + 0.05 * len(top_matched)))
            matched_terms_str = ", ".join(sorted(top_matched))
            reasoning = (
                f"Offline keyword match against trigger/metadata for {top_wf.workflow_id} "
                f"({top_wf.workflow_name}): matched terms [{matched_terms_str}]."
            )
            extracted = extract_inputs_from_query(clean_query, top_wf.workflow_id)
            return RoutingDecision(
                workflow_id=top_wf.workflow_id,
                confidence=round(confidence, 2),
                reasoning=reasoning,
                extracted_inputs=extracted,
                requires_clarification=False,
                routing_mode="offline",
            )

        # Ambiguous, low-confidence, or unrelated query: require clarification
        close_candidates = [
            f"{wf.workflow_id} ({wf.workflow_name})"
            for wf, s, _ in ranked[:2]
            if s > 0
        ]
        if close_candidates:
            reasoning = (
                f"Query could not be confidently matched to any workflow via offline routing "
                f"(top score: {top_score:.1f}, threshold: {self.match_threshold:.1f}). "
                f"Close candidate(s): {', '.join(close_candidates)}. Clarification required."
            )
        else:
            reasoning = (
                "Query could not be matched to any registered workflow via offline routing. "
                "Clarification required."
            )

        return RoutingDecision(
            workflow_id=None,
            confidence=0.0,
            reasoning=reasoning,
            extracted_inputs={},
            requires_clarification=True,
            routing_mode="offline",
        )

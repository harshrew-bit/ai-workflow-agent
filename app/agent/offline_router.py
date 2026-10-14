"""Deterministic offline workflow router matching requests against workbook metadata."""

import re
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from app.agent.normalization import (
    detect_query_ambiguity,
    extract_deterministic_inputs,
)
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
    "discrepancy": "difference",
    "discrepancies": "difference",
    "variance": "difference",
    "variances": "difference",
    "deviations": "difference",
    "deviation": "difference",
    "audit": "audit",
    "auditing": "audit",
    "audits": "audit",
}

DELIVERY_DOMAIN_TOKENS: Set[str] = {
    "delivery", "deliver", "delay", "delays", "late", "lateness", "risk", "shipment", "shipments", "transit", "ontime", "on-time",
}

PRICING_DOMAIN_TOKENS: Set[str] = {
    "price", "prices", "pricing", "cost", "costs", "difference", "discrepancy", "variance", "deviation",
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
    """Extract explicit identifiers, thresholds, and comparison parameters from query text."""
    return extract_deterministic_inputs(query, workflow_id)


def detect_multi_workflow_intents(
    query: str,
    available_workflows: Sequence[WorkflowDefinition],
    scorer: Optional["OfflineWorkflowRouter"] = None,
) -> List[Tuple[WorkflowDefinition, str]]:
    """Detect whether a query requests multiple distinct workflow objectives.

    Distinguishes multiple distinct business workflows from multiple steps
    within a single workflow (e.g. 'compare prices and flag exceptions' is a single WF002).

    Returns a list of (WorkflowDefinition, sub_clause) pairs if >= 2 distinct workflows
    are confidently requested; otherwise returns empty list.
    """
    clean_query = (query or "").strip()
    if not clean_query:
        return []

    router = scorer or OfflineWorkflowRouter()

    # Split on explicit sequence markers or strong sentence/conjunction boundaries
    clauses: List[str] = []
    seq_match = re.match(
        r"^\s*first\s+(.*?)\s+(?:then|next|after\s+that)\s+(.*)",
        clean_query,
        re.IGNORECASE | re.DOTALL,
    )
    if seq_match:
        part1 = seq_match.group(1).strip()
        part2 = seq_match.group(2).strip()
        part2 = re.sub(
            r"\b(?:return\s+both\s+reports.*|give\s+me\s+both.*|both\s+reports.*)$",
            "",
            part2,
            flags=re.IGNORECASE,
        ).strip()
        clauses = [part1, part2]
    else:
        sentence_parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+|\n+|;\s*", clean_query) if p.strip()]
        content_parts = []
        has_both_indicator = False
        for sp in sentence_parts:
            if re.search(r"\b(?:give\s+me\s+both\s+results|return\s+both\s+reports|both\s+reports\s+separately)\b", sp, re.IGNORECASE):
                has_both_indicator = True
                continue
            content_parts.append(sp)

        if len(content_parts) >= 2:
            clauses = content_parts
        elif len(content_parts) == 1 and (" and " in content_parts[0] or " as well as " in content_parts[0]):
            single_text = content_parts[0]
            # Match conjunctions only when followed by an action verb indicating a separate objective
            action_verb_pat = (
                r"\s+(?:and|as\s+well\s+as)\s+(?:then\s+|also\s+)?"
                r"(?=(?:run|execute|check|verify|assess|identify|find|audit|compare|calculate|generate|alert|monitor|evaluate|review|determine|process|inspect|list|show|detect)\b)"
            )
            conj_split = re.split(action_verb_pat, single_text, flags=re.IGNORECASE)
            if len(conj_split) == 2 and (has_both_indicator or (len(conj_split[0]) > 10 and len(conj_split[1]) > 10)):
                clauses = [conj_split[0].strip(), conj_split[1].strip()]

    if len(clauses) < 2:
        return []

    matched_wfs: List[Tuple[WorkflowDefinition, str]] = []
    seen_ids: Set[str] = set()

    for clause in clauses:
        ranked = router.score_workflows(clause, available_workflows)
        if not ranked:
            continue
        top_wf, top_score, _ = ranked[0]
        second_score = ranked[1][1] if len(ranked) > 1 else 0.0

        if top_score >= 3.0 and top_score > second_score and top_wf.workflow_id not in seen_ids:
            seen_ids.add(top_wf.workflow_id)
            matched_wfs.append((top_wf, clause))

    if len(matched_wfs) >= 2:
        return matched_wfs

    return []


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

            # Domain-aware negative discrimination:
            # If query is specifically about pricing/cost/discrepancies and contains no delivery/delay concepts,
            # WF011 (Delivery Risk) must not outscore WF002 based on generic words like 'audit' or 'vendor'.
            if wf.workflow_id == "WF011":
                has_pricing = any(t in q_tokens for t in PRICING_DOMAIN_TOKENS)
                has_delivery = any(t in q_tokens for t in DELIVERY_DOMAIN_TOKENS)
                if has_pricing and not has_delivery:
                    score = 0.0
                    matched = set()

            # Conversely, if query is specifically about delivery/delays and contains no pricing concepts,
            # WF002 should not match.
            if wf.workflow_id == "WF002":
                has_pricing = any(t in q_tokens for t in PRICING_DOMAIN_TOKENS)
                has_delivery = any(t in q_tokens for t in DELIVERY_DOMAIN_TOKENS)
                if has_delivery and not has_pricing:
                    score = 0.0
                    matched = set()

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
            is_ambiguous, ambiguity_reason = detect_query_ambiguity(clean_query, top_wf.workflow_id)
            if is_ambiguous:
                return RoutingDecision(
                    workflow_id=top_wf.workflow_id,
                    confidence=round(confidence, 2),
                    reasoning=ambiguity_reason or reasoning,
                    extracted_inputs={},
                    requires_clarification=True,
                    routing_mode="offline",
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

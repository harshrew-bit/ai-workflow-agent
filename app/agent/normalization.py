"""Parameter contract, query ambiguity detection, extraction, and normalization."""

from decimal import Decimal
import math
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union

# Operator mapping
VALID_OPERATORS: Dict[str, str] = {
    ">": "EXCEEDS",
    "<": "LESS_THAN",
    ">=": "AT_LEAST",
    "<=": "AT_MOST",
    "==": "EQUALS",
}

OPERATOR_SYNONYMS: Dict[str, str] = {
    ">": ">",
    "gt": ">",
    "greater": ">",
    "greater than": ">",
    "exceeds": ">",
    "exceeding": ">",
    "above": ">",
    "more than": ">",
    "<": "<",
    "lt": "<",
    "less": "<",
    "less than": "<",
    "under": "<",
    "below": "<",
    ">=": ">=",
    "gte": ">=",
    "at least": ">=",
    "greater than or equal to": ">=",
    "minimum": ">=",
    "minimum of": ">=",
    "no less than": ">=",
    "<=": "<=",
    "lte": "<=",
    "at most": "<=",
    "less than or equal to": "<=",
    "up to": "<=",
    "no more than": "<=",
    "==": "==",
    "eq": "==",
    "equals": "==",
    "equal to": "==",
    "exactly": "==",
}

DIRECTIONAL_PATTERNS: List[re.Pattern] = [
    re.compile(r"within\s+\d+(?:\.\d+)?\s*(?:%|percent)?\s*(?:below|above|under|over)", re.IGNORECASE),
    re.compile(r"(?:below|under|cheaper\s+than|lower\s+than)\s+(?:their\s+)?internal", re.IGNORECASE),
    re.compile(r"(?:above|over|higher\s+than|more\s+expensive\s+than)\s+(?:their\s+)?internal", re.IGNORECASE),
    re.compile(r"within\s+\d+(?:\.\d+)?\s*(?:%|percent)?\s*(?:of\s+)?(?:below|above|lower|higher)", re.IGNORECASE),
    re.compile(r"\b(?:below|lower\s+than|cheaper\s+than|above|higher\s+than)\s+internal\b", re.IGNORECASE),
]

HISTORICAL_PRICE_PATTERNS: List[re.Pattern] = [
    re.compile(r"\bthis\s+month(?:'s)?\s*(?:vendor\s*)?prices?\s*(?:against|versus|vs|compared\s*to)\s*last\s+month", re.IGNORECASE),
    re.compile(r"\b(?:last|prior|previous)\s+month(?:'s)?\s*(?:vendor\s*)?prices?\b", re.IGNORECASE),
    re.compile(r"\bmonth-over-month\s+(?:price|pricing|vendor)", re.IGNORECASE),
    re.compile(r"\bhistorical\s+(?:vendor\s+)?prices?\b", re.IGNORECASE),
    re.compile(r"\bprices?\s+(?:from|in)\s+(?:last|prior|previous)\s+(?:month|quarter|period)\b", re.IGNORECASE),
    re.compile(r"\bcompare\s+(?:current\s+)?prices?\s+(?:with|to|against)\s+historical\b", re.IGNORECASE),
    re.compile(r"\bvendor\s+prices?\s+(?:changes?|trends?|history)\b", re.IGNORECASE),
]


def detect_pricing_directional_ambiguity(query: str) -> Optional[str]:
    """Detect if a pricing query specifies directional/signed price differences.

    WF002 strictly evaluates symmetric absolute percentage deviation:
    abs(vendor - internal) / internal * 100.
    Phrasings like 'within 5 percent below their internal prices' or 'cheaper than internal by 10%'
    specify signed or directional tolerance bands rather than absolute deviation.
    Because evaluating them as symmetric variance would incorrectly flag opposite-direction items,
    such requests must prompt for clarification.
    """
    if not query:
        return None
    for pattern in DIRECTIONAL_PATTERNS:
        match = pattern.search(query)
        if match:
            matched_phrase = match.group(0)
            return (
                f"The request specifies a directional price comparison ('{matched_phrase}'), "
                f"whereas WF002 evaluates symmetric absolute percentage deviation. "
                f"Clarification is required."
            )
    return None


def detect_historical_pricing_ambiguity(query: str, has_historical_data: bool = False) -> Optional[str]:
    """Detect if a pricing query requests historical / month-over-month price comparison.

    WF002 compares internal catalog prices against a current vendor price list.
    When a request asks to compare against 'last month's prices' or historical vendor prices,
    substituting the internal price catalog would be a silent semantic corruption.
    Unless an explicit historical vendor price data file is provided, this must prompt
    for clarification.
    """
    if not query or has_historical_data:
        return None
    for pattern in HISTORICAL_PRICE_PATTERNS:
        match = pattern.search(query)
        if match:
            matched_phrase = match.group(0)
            return (
                f"The request asks for a historical price comparison ('{matched_phrase}'), "
                f"whereas WF002 evaluates internal catalog prices against current vendor prices. "
                f"Historical vendor price data is not available in the default dataset. "
                f"Please supply the historical/prior-period vendor pricing CSV to perform this comparison."
            )
    return None


def detect_supplier_audit_ambiguity(query: str, workflow_id: Optional[str] = None) -> Optional[str]:
    """Detect ambiguous supplier audit requests that do not specify delivery vs pricing."""
    if not query:
        return None
    # If the workflow is already known and is neither WF002 nor WF011, there is no ambiguity
    if workflow_id and workflow_id not in ("WF002", "WF011"):
        return None
    q_lower = query.lower()
    # Catalog queries belong to vendor catalog management (WF003)
    if "catalog" in q_lower:
        return None
    # Check for bare supplier/vendor audit without domain qualifiers
    if re.search(r"\b(?:supplier|vendor)\s+audit\b|\baudit\s+(?:the\s+)?(?:suppliers?|vendors?)\b", q_lower):
        has_pricing = any(w in q_lower for w in ("price", "pricing", "cost", "discrepanc", "rate", "charg"))
        has_delivery = any(w in q_lower for w in ("deliver", "delay", "late", "shipment", "risk", "transit", "on-time", "ontime"))
        if not has_pricing and not has_delivery:
            return (
                "The request asks for a supplier audit without specifying whether it concerns "
                "delivery performance (WF011) or vendor price validation (WF002). "
                "Please clarify your objective."
            )
    return None


def detect_query_ambiguity(
    query: str,
    workflow_id: Optional[str] = None,
    has_historical_data: bool = False,
) -> Tuple[bool, Optional[str]]:
    """Determine whether a user query contains semantic ambiguities for the target workflow.

    Returns (is_ambiguous, reason).
    """
    if not query:
        return False, None

    # Check for bare/ambiguous supplier audit query
    supplier_reason = detect_supplier_audit_ambiguity(query, workflow_id=workflow_id)
    if supplier_reason:
        return True, supplier_reason

    q_lower = query.lower()
    is_pricing = workflow_id == "WF002" or any(
        term in q_lower for term in ("price", "pricing", "vendor", "diff", "difference", "sku")
    )
    if is_pricing:
        hist_reason = detect_historical_pricing_ambiguity(query, has_historical_data=has_historical_data)
        if hist_reason:
            return True, hist_reason

        dir_reason = detect_pricing_directional_ambiguity(query)
        if dir_reason:
            return True, dir_reason

    return False, None


def detect_operator_from_text(text: str) -> Optional[str]:
    """Extract comparison operator symbol (<, <=, >, >=, ==) from text."""
    if not text:
        return None
    t_lower = text.lower()
    # Check compound symbols and multi-word phrases first
    if re.search(r"(?:less\s+than\s+or\s+equal\s+to|at\s+most|up\s+to|no\s+more\s+than|(?<!<)<=(?!=))", t_lower):
        return "<="
    elif re.search(r"(?:greater\s+than\s+or\s+equal\s+to|at\s+least|minimum\s+of|no\s+less\s+than|(?<!>)>=)(?!=)", t_lower):
        return ">="
    elif re.search(r"(?:equal\s+to|equals|exactly|==)", t_lower):
        return "=="
    elif re.search(r"(?:strictly\s+less\s+than|strictly\s+below|less\s+than|below|under|(?<!<)<(?![=<]))", t_lower):
        return "<"
    elif re.search(r"(?:strictly\s+greater\s+than|strictly\s+exceeding|greater\s+than|exceeding|exceeds|more\s+than|above|(?<!>)>(?![=>]))", t_lower):
        return ">"
    return None


def extract_deterministic_inputs(query: str, workflow_id: Optional[str] = None) -> Dict[str, Any]:
    """Extract explicit identifiers, thresholds, and comparison parameters from query text."""
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

    q_lower = query.lower()

    # Price Validation (WF002) parameters: threshold and comparison operator
    is_pricing_query = workflow_id == "WF002" or any(
        term in q_lower for term in ("price", "pricing", "vendor", "diff", "difference", "sku", "deviation")
    )
    if is_pricing_query:
        op = detect_operator_from_text(query)

        # Detect threshold percentage:
        # e.g., "20%", "20 percent", "deviation of 20%", "at least 20%"
        thresh_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:%|percent)", query, re.IGNORECASE)
        if not thresh_match and op:
            thresh_match = re.search(
                r"(?:>=|<=|==|>|<|less\s+than|greater\s+than|at\s+least|at\s+most|exceeding|above|below|under|deviation\s+of|threshold\s+of)\s+(\d+(?:\.\d+)?)",
                query,
                re.IGNORECASE,
            )

        if thresh_match:
            try:
                val = float(thresh_match.group(1))
                if math.isfinite(val) and val >= 0:
                    extracted["threshold"] = val
                    extracted["price_threshold"] = val
            except ValueError:
                pass

        if op:
            extracted["comparison_operator"] = op
            extracted["operator"] = op

    # Workflow Performance (WF010) parameters: failure_threshold and time_threshold_seconds
    is_perf_query = workflow_id == "WF010" or any(
        term in q_lower for term in ("performance", "latency", "failure rate", "failure threshold", "execution time")
    )
    if is_perf_query:
        fail_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:%|percent)\s*(?:failure|fail)", query, re.IGNORECASE)
        if not fail_match:
            fail_match = re.search(
                r"(?:failure\s+rate|failure\s+threshold|exceeding\s+failure).*?(\d+(?:\.\d+)?)\s*(?:%|percent)?",
                query,
                re.IGNORECASE,
            )
        if fail_match:
            try:
                val = float(fail_match.group(1))
                if math.isfinite(val) and val >= 0:
                    extracted["failure_threshold"] = val
            except ValueError:
                pass

        time_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:seconds?|sec|s)\b", query, re.IGNORECASE)
        if time_match:
            try:
                val = float(time_match.group(1))
                if math.isfinite(val) and val >= 0:
                    extracted["time_threshold_seconds"] = val
            except ValueError:
                pass

    # Inventory restock (WF001) parameters: threshold_override
    is_inventory_query = workflow_id == "WF001" or any(
        term in q_lower for term in ("inventory", "restock", "stock")
    )
    if is_inventory_query:
        stock_thresh = re.search(
            r"(?:stock\s+threshold|minimum\s+stock(?:\s+threshold)?|threshold\s+override|stock\s+limit|minimum\s+units?)\s*(?:of|:|=)?\s*(\d+)(?!\s*(?:%|percent))\b",
            query,
            re.IGNORECASE,
        )
        if not stock_thresh and workflow_id == "WF001" and not any(p in q_lower for p in ("price", "vendor", "diff", "deviation")):
            stock_thresh = re.search(
                r"(?:threshold)\s*(?:of|:|=)?\s*(\d+)(?!\s*(?:%|percent))\b",
                query,
                re.IGNORECASE,
            )
        if stock_thresh:
            try:
                extracted["threshold_override"] = int(stock_thresh.group(1))
            except ValueError:
                pass

    return extracted


def parse_percentage_threshold(val: Any, param_name: str = "Price validation threshold") -> float:
    """Parse percentage threshold, supporting '%', 'percent', and numeric types.

    Rejects negative numbers, non-finite values (NaN, inf), booleans, and malformed strings.
    """
    if val is None or isinstance(val, bool):
        raise ValueError(f"{param_name} must be a finite non-negative number, got '{val}'.")

    if isinstance(val, (int, float, Decimal)):
        if isinstance(val, Decimal):
            if not val.is_finite() or val < Decimal("0"):
                raise ValueError(f"{param_name} must be a finite non-negative number, got '{val}'.")
            return float(val)
        if not math.isfinite(val) or val < 0:
            raise ValueError(f"{param_name} must be a finite non-negative number, got '{val}'.")
        return float(val)

    if isinstance(val, str):
        cleaned = val.strip()
        if cleaned.endswith("%"):
            cleaned = cleaned[:-1].strip()
        if cleaned.lower().endswith("percent"):
            cleaned = cleaned[:-7].strip()
        if cleaned.lower() in ("nan", "inf", "-inf", "+inf"):
            raise ValueError(f"{param_name} must be a finite non-negative number, got '{val}'.")
        try:
            f_val = float(cleaned)
        except ValueError:
            raise ValueError(f"{param_name} must be a finite non-negative number, got '{val}'.")
        if not math.isfinite(f_val) or f_val < 0:
            raise ValueError(f"{param_name} must be a finite non-negative number, got '{val}'.")
        return f_val

    raise ValueError(f"{param_name} must be a finite non-negative number, got '{val}'.")


def parse_comparison_operator(val: Any) -> str:
    """Validate and canonicalize comparison operator string (<, <=, >, >=, ==).

    Rejects non-string values and unsupported operators.
    """
    if not isinstance(val, str):
        raise ValueError(
            f"Unsupported comparison operator '{val}'. Supported operators: {', '.join(VALID_OPERATORS.keys())}."
        )
    cleaned = val.strip().lower()
    op_norm = OPERATOR_SYNONYMS.get(cleaned, val.strip())
    if op_norm in VALID_OPERATORS:
        return op_norm
    raise ValueError(
        f"Unsupported comparison operator '{val}'. Supported operators: {', '.join(VALID_OPERATORS.keys())}."
    )


def parse_integer_threshold(val: Any, param_name: str = "Stock threshold override") -> int:
    """Parse non-negative integer threshold.

    Rejects booleans, negative numbers, non-integers, and malformed strings.
    """
    if val is None or isinstance(val, bool):
        raise ValueError(f"{param_name} must be a non-negative integer, got '{val}'.")

    if isinstance(val, int):
        if val < 0:
            raise ValueError(f"{param_name} must be a non-negative integer, got '{val}'.")
        return val

    if isinstance(val, float):
        if not math.isfinite(val) or val < 0 or not val.is_integer():
            raise ValueError(f"{param_name} must be a non-negative integer, got '{val}'.")
        return int(val)

    if isinstance(val, Decimal):
        if not val.is_finite() or val < 0 or val != val.to_integral():
            raise ValueError(f"{param_name} must be a non-negative integer, got '{val}'.")
        return int(val)

    if isinstance(val, str):
        cleaned = val.strip()
        if not re.match(r"^\d+$", cleaned):
            raise ValueError(f"{param_name} must be a non-negative integer, got '{val}'.")
        return int(cleaned)

    raise ValueError(f"{param_name} must be a non-negative integer, got '{val}'.")


def parse_time_threshold_seconds(val: Any) -> float:
    """Parse time threshold in seconds, supporting units ('10', '10s', '10 sec', '10 seconds').

    Rejects negative numbers, non-finite values (NaN, inf), booleans, and malformed strings.
    """
    if val is None or isinstance(val, bool):
        raise ValueError(f"Execution time threshold must be a finite non-negative number, got '{val}'.")

    if isinstance(val, (int, float, Decimal)):
        if isinstance(val, Decimal):
            if not val.is_finite() or val < Decimal("0"):
                raise ValueError(f"Execution time threshold must be a finite non-negative number, got '{val}'.")
            return float(val)
        if not math.isfinite(val) or val < 0:
            raise ValueError(f"Execution time threshold must be a finite non-negative number, got '{val}'.")
        return float(val)

    if isinstance(val, str):
        cleaned = val.strip()
        match = re.match(r"^([+-]?\d+(?:\.\d+)?)\s*(seconds?|secs?|s)?$", cleaned, re.IGNORECASE)
        if not match:
            raise ValueError(f"Execution time threshold must be a finite non-negative number, got '{val}'.")
        try:
            num = float(match.group(1))
        except ValueError:
            raise ValueError(f"Execution time threshold must be a finite non-negative number, got '{val}'.")
        if not math.isfinite(num) or num < 0:
            raise ValueError(f"Execution time threshold must be a finite non-negative number, got '{val}'.")
        return num

    raise ValueError(f"Execution time threshold must be a finite non-negative number, got '{val}'.")


def normalize_workflow_inputs(inputs: Dict[str, Any], workflow_id: Optional[str] = None) -> Dict[str, Any]:
    """Normalize input aliases to canonical parameter contracts.

    Canonical contracts:
    - WF002: threshold (float), comparison_operator (str).
    - WF001: threshold_override (int).
    - WF010: failure_threshold (float), time_threshold_seconds (float).
    """
    normalized = dict(inputs)

    # WF002 normalization
    raw_thresh = None
    for k in ("threshold", "price_threshold", "threshold_percentage"):
        if k in normalized and normalized[k] is not None:
            raw_thresh = normalized[k]
            break
    if raw_thresh is not None:
        try:
            t_val = parse_percentage_threshold(raw_thresh, "Price validation threshold")
            normalized["threshold"] = t_val
            normalized["price_threshold"] = t_val
            normalized["threshold_percentage"] = t_val
        except ValueError:
            normalized["threshold"] = raw_thresh
            normalized["price_threshold"] = raw_thresh
            normalized["threshold_percentage"] = raw_thresh

    raw_op = None
    for k in ("comparison_operator", "operator"):
        if k in normalized and normalized[k] is not None:
            raw_op = normalized[k]
            break
    if raw_op is not None:
        try:
            op_norm = parse_comparison_operator(raw_op)
            normalized["comparison_operator"] = op_norm
            normalized["operator"] = op_norm
        except ValueError:
            normalized["comparison_operator"] = raw_op
            normalized["operator"] = raw_op

    # WF001 normalization: threshold_override > minimum_stock > minimum_threshold
    raw_override = None
    for k in (
        "threshold_override",
        "minimum_stock",
        "minimum_threshold",
        "stock_threshold",
        "stock_threshold_override",
        "minimum_stock_override",
    ):
        if k in normalized and normalized[k] is not None:
            raw_override = normalized[k]
            break
    if raw_override is not None:
        try:
            o_val = parse_integer_threshold(raw_override, "Stock threshold override")
            normalized["threshold_override"] = o_val
            normalized["minimum_stock"] = o_val
            normalized["minimum_threshold"] = o_val
            normalized["stock_threshold"] = o_val
            normalized["stock_threshold_override"] = o_val
            normalized["minimum_stock_override"] = o_val
        except ValueError:
            normalized["threshold_override"] = raw_override
            normalized["minimum_stock"] = raw_override
            normalized["minimum_threshold"] = raw_override
            normalized["stock_threshold"] = raw_override
            normalized["stock_threshold_override"] = raw_override
            normalized["minimum_stock_override"] = raw_override

    # WF010 normalization
    raw_fail = None
    for k in ("failure_threshold", "failure_rate_threshold"):
        if k in normalized and normalized[k] is not None:
            raw_fail = normalized[k]
            break
    if raw_fail is not None:
        try:
            f_val = parse_percentage_threshold(raw_fail, "Failure rate threshold")
            normalized["failure_threshold"] = f_val
            normalized["failure_rate_threshold"] = f_val
        except ValueError:
            normalized["failure_threshold"] = raw_fail
            normalized["failure_rate_threshold"] = raw_fail

    raw_time = None
    for k in ("time_threshold_seconds", "time_threshold", "latency_threshold"):
        if k in normalized and normalized[k] is not None:
            raw_time = normalized[k]
            break
    if raw_time is not None:
        try:
            sec_val = parse_time_threshold_seconds(raw_time)
            normalized["time_threshold_seconds"] = sec_val
            normalized["time_threshold"] = sec_val
            normalized["latency_threshold"] = sec_val
        except ValueError:
            normalized["time_threshold_seconds"] = raw_time
            normalized["time_threshold"] = raw_time
            normalized["latency_threshold"] = raw_time

    return normalized


def is_path_like_key(key: str) -> bool:
    """True for input names that point at the filesystem (e.g. vendor_csv_path, file_path)."""
    lowered = key.lower()
    return any(token in lowered for token in ("path", "file", "csv"))


def merge_execution_inputs(
    default_inputs: Dict[str, Any],
    router_extracted: Dict[str, Any],
    query_extracted: Dict[str, Any],
    runtime_inputs: Dict[str, Any],
    workflow_id: Optional[str] = None,
) -> Tuple[Dict[str, Any], List[str]]:
    """Merge execution inputs with authoritative precedence contract.

    Precedence order:
      1. Explicit runtime inputs (CLI / API parameters)
      2. Deterministic user query extraction (direct from request text)
      3. Router-extracted inputs (model output, normalized)
      4. Default workflow inputs (configured catalog defaults)

    Security rule:
      Path-like parameters extracted by the router or query text are discarded to prevent
      arbitrary file path injection. File paths MUST come from explicit runtime inputs
      or configured defaults.
    """
    norm_defaults = normalize_workflow_inputs(default_inputs, workflow_id)
    norm_router = normalize_workflow_inputs(router_extracted, workflow_id)
    norm_query = normalize_workflow_inputs(query_extracted, workflow_id)
    norm_runtime = normalize_workflow_inputs(runtime_inputs, workflow_id)

    ignored_path_inputs: List[str] = []
    sanitized_router: Dict[str, Any] = {}
    for k, v in norm_router.items():
        if is_path_like_key(k):
            ignored_path_inputs.append(k)
        else:
            sanitized_router[k] = v

    sanitized_query: Dict[str, Any] = {}
    for k, v in norm_query.items():
        if is_path_like_key(k):
            if k not in ignored_path_inputs:
                ignored_path_inputs.append(k)
        else:
            sanitized_query[k] = v

    merged = dict(norm_defaults)
    merged.update(sanitized_router)
    merged.update(sanitized_query)
    merged.update(norm_runtime)

    return merged, sorted(set(ignored_path_inputs))

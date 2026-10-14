// Default workflow catalog extracted directly from Excel workbook and WF011 extension
import { WorkflowDefinition } from "../types/workflow";

export const DEFAULT_WORKFLOWS: WorkflowDefinition[] = [
  {
    "workflow_id": "WF001",
    "workflow_name": "Inventory Restock Check",
    "trigger": "User asks which products need restocking",
    "inputs": "Product inventory CSV; minimum stock threshold",
    "steps": "Load inventory \u2192 compare current stock with minimum threshold \u2192 identify low-stock products \u2192 calculate reorder quantity \u2192 generate restock list",
    "parsed_steps": [
      "Load inventory",
      "compare current stock with minimum threshold",
      "identify low-stock products",
      "calculate reorder quantity",
      "generate restock list"
    ],
    "decision_logic": "If current_stock < minimum_stock, mark product for restock",
    "tools_required": "CSV reader; calculator",
    "parsed_tools": [
      "CSV reader",
      "calculator"
    ],
    "expected_output": "List of products requiring restock with current stock, threshold, and suggested reorder quantity"
  },
  {
    "workflow_id": "WF002",
    "workflow_name": "Product Price Validation",
    "trigger": "User asks to validate product prices",
    "inputs": "Product CSV; vendor price list",
    "steps": "Load product prices \u2192 match products by SKU \u2192 compare internal and vendor prices \u2192 calculate percentage difference \u2192 flag exceptions",
    "parsed_steps": [
      "Load product prices",
      "match products by SKU",
      "compare internal and vendor prices",
      "calculate percentage difference",
      "flag exceptions"
    ],
    "decision_logic": "Flag when price difference exceeds 10%",
    "tools_required": "CSV reader; calculator",
    "parsed_tools": [
      "CSV reader",
      "calculator"
    ],
    "expected_output": "Validation report showing matched products, price differences, and exceptions"
  },
  {
    "workflow_id": "WF003",
    "workflow_name": "Vendor File Processing",
    "trigger": "User provides a vendor file for processing",
    "inputs": "CSV/XLSX file containing vendor product data",
    "steps": "Read file \u2192 detect columns \u2192 normalize column names \u2192 validate required fields \u2192 identify invalid rows \u2192 produce cleaned dataset",
    "parsed_steps": [
      "Read file",
      "detect columns",
      "normalize column names",
      "validate required fields",
      "identify invalid rows",
      "produce cleaned dataset"
    ],
    "decision_logic": "Rows missing SKU or product name are invalid",
    "tools_required": "Excel/CSV parser; data validation",
    "parsed_tools": [
      "Excel/CSV parser",
      "data validation"
    ],
    "expected_output": "Cleaned file plus validation summary and invalid-row report"
  },
  {
    "workflow_id": "WF004",
    "workflow_name": "Product Description Generator",
    "trigger": "User asks to generate product content",
    "inputs": "Product name; category; attributes; material; color; target audience",
    "steps": "Validate required attributes \u2192 create product description \u2192 generate short description \u2192 generate SEO title \u2192 generate meta description",
    "parsed_steps": [
      "Validate required attributes",
      "create product description",
      "generate short description",
      "generate SEO title",
      "generate meta description"
    ],
    "decision_logic": "Do not invent missing product attributes; explicitly mark missing information",
    "tools_required": "LLM; text validation",
    "parsed_tools": [
      "LLM",
      "text validation"
    ],
    "expected_output": "Product description, short description, SEO title, and meta description"
  },
  {
    "workflow_id": "WF005",
    "workflow_name": "Customer Order Status",
    "trigger": "User asks for an order status",
    "inputs": "Order ID or customer email",
    "steps": "Validate identifier \u2192 search order data \u2192 retrieve order status \u2192 retrieve shipment information \u2192 summarize current status",
    "parsed_steps": [
      "Validate identifier",
      "search order data",
      "retrieve order status",
      "retrieve shipment information",
      "summarize current status"
    ],
    "decision_logic": "If no order is found, ask for another identifier",
    "tools_required": "Order database/API; shipment lookup",
    "parsed_tools": [
      "Order database/API",
      "shipment lookup"
    ],
    "expected_output": "Order status, items, shipment status, and tracking information when available"
  },
  {
    "workflow_id": "WF006",
    "workflow_name": "Duplicate Product Detection",
    "trigger": "User asks to find duplicate products",
    "inputs": "Product catalog",
    "steps": "Load products \u2192 normalize names/SKUs \u2192 compare identifiers \u2192 compare product attributes \u2192 group likely duplicates \u2192 assign confidence",
    "parsed_steps": [
      "Load products",
      "normalize names/SKUs",
      "compare identifiers",
      "compare product attributes",
      "group likely duplicates",
      "assign confidence"
    ],
    "decision_logic": "Exact SKU match is a definite duplicate; high attribute similarity is a possible duplicate",
    "tools_required": "CSV/database reader; text similarity",
    "parsed_tools": [
      "CSV/database reader",
      "text similarity"
    ],
    "expected_output": "Duplicate groups with matching fields and confidence level"
  },
  {
    "workflow_id": "WF007",
    "workflow_name": "Marketing Campaign Brief",
    "trigger": "User asks to create a campaign brief",
    "inputs": "Campaign goal; product list; target audience; promotion; dates",
    "steps": "Validate inputs \u2192 identify campaign objective \u2192 summarize products \u2192 create messaging \u2192 create channel recommendations \u2192 create campaign checklist",
    "parsed_steps": [
      "Validate inputs",
      "identify campaign objective",
      "summarize products",
      "create messaging",
      "create channel recommendations",
      "create campaign checklist"
    ],
    "decision_logic": "If campaign goal or dates are missing, request them before generating the brief",
    "tools_required": "LLM; product data reader",
    "parsed_tools": [
      "LLM",
      "product data reader"
    ],
    "expected_output": "Structured campaign brief with objective, audience, messaging, channels, timeline, and checklist"
  },
  {
    "workflow_id": "WF008",
    "workflow_name": "SEO Keyword Classification",
    "trigger": "User uploads or provides a keyword list",
    "inputs": "Keyword CSV; product/category information",
    "steps": "Read keywords \u2192 remove duplicates \u2192 classify search intent \u2192 map keywords to categories \u2192 identify high-priority keywords \u2192 export results",
    "parsed_steps": [
      "Read keywords",
      "remove duplicates",
      "classify search intent",
      "map keywords to categories",
      "identify high-priority keywords",
      "export results"
    ],
    "decision_logic": "Classify each keyword as informational, commercial, transactional, or navigational",
    "tools_required": "CSV reader; LLM/classifier",
    "parsed_tools": [
      "CSV reader",
      "LLM/classifier"
    ],
    "expected_output": "Keyword report with intent, category, priority, and recommended target page"
  },
  {
    "workflow_id": "WF009",
    "workflow_name": "Employee Task Assignment",
    "trigger": "Manager asks the agent to assign a task",
    "inputs": "Task description; employee list; skills; workload; priority; deadline",
    "steps": "Understand task requirements \u2192 compare employee skills \u2192 check current workload \u2192 rank candidates \u2192 select employee \u2192 generate assignment summary",
    "parsed_steps": [
      "Understand task requirements",
      "compare employee skills",
      "check current workload",
      "rank candidates",
      "select employee",
      "generate assignment summary"
    ],
    "decision_logic": "Prefer employees with required skills and available capacity; escalate if no suitable employee exists",
    "tools_required": "Employee/task database; ranking logic",
    "parsed_tools": [
      "Employee/task database",
      "ranking logic"
    ],
    "expected_output": "Recommended employee, reasoning, priority, deadline, and task summary"
  },
  {
    "workflow_id": "WF010",
    "workflow_name": "Workflow Performance Report",
    "trigger": "User asks for a performance report",
    "inputs": "Workflow execution logs",
    "steps": "Load execution logs \u2192 calculate success/failure rate \u2192 calculate average execution time \u2192 identify frequent errors \u2192 identify slow steps \u2192 generate recommendations",
    "parsed_steps": [
      "Load execution logs",
      "calculate success/failure rate",
      "calculate average execution time",
      "identify frequent errors",
      "identify slow steps",
      "generate recommendations"
    ],
    "decision_logic": "Flag workflows with failure rate above 10% or average execution time above defined threshold",
    "tools_required": "CSV/database reader; calculator; reporting",
    "parsed_tools": [
      "CSV/database reader",
      "calculator",
      "reporting"
    ],
    "expected_output": "Performance summary with metrics, problem areas, and improvement recommendations"
  },
  {
    "workflow_id": "WF011",
    "workflow_name": "Supplier Delivery Risk Assessment",
    "trigger": "Periodic supplier audit, purchase order review, or vendor delivery risk evaluation",
    "inputs": "Supplier delivery records or CSV file; optional delivery risk thresholds",
    "steps": "Load supplier delivery records -> Validate delivery records -> Calculate supplier delivery metrics -> Evaluate supplier risk levels -> Generate supplier risk report",
    "parsed_steps": [
      "Load supplier delivery records",
      "Validate delivery records",
      "Calculate supplier delivery metrics",
      "Evaluate supplier risk levels",
      "Generate supplier risk report"
    ],
    "decision_logic": "Calculate late delivery rate and average delay days. Flag HIGH risk if risk score >= 50.0, late rate >= 35%, or average delay >= 7.0 days; MEDIUM risk if risk score >= 25.0, late rate >= 15%, or average delay >= 3.0 days; LOW risk otherwise.",
    "tools_required": "supplier_delivery_loader, delivery_record_validator, delivery_metrics_calculator, supplier_risk_evaluator, supplier_risk_reporter",
    "parsed_tools": [
      "supplier_delivery_loader, delivery_record_validator, delivery_metrics_calculator, supplier_risk_evaluator, supplier_risk_reporter"
    ],
    "expected_output": "Structured supplier delivery risk assessment report with supplier evaluations, risk scores, late rates, average delay days, and recommended mitigation actions."
  }
];

# Live LLM Routing — Verification Guide & Status

## Current Status: NOT VERIFIED

In this local evaluation environment, neither `GEMINI_API_KEY` nor `OPENAI_API_KEY` is configured in the environment variables.

In accordance with strict verification honesty standards:
- **No live API completions were performed.**
- **No synthetic, simulated, or fabricated outputs have been placed in this directory.**
- All workflow routing and tool execution demonstrated by default in this repository rely on the **deterministic offline router** (`app/agent/offline_router.py`) or explicit mock routing (`--mock-route`).

---

## Instructions for Live LLM Verification

To verify live natural language workflow routing with an LLM provider:

### 1. Configure API Credentials

Set your API key for Google Gemini or an OpenAI-compatible endpoint:

```bash
# Option A: Google Gemini
export LLM_PROVIDER="gemini"
export GEMINI_API_KEY="your-gemini-api-key"
export GEMINI_MODEL="gemini-1.5-flash"

# Option B: OpenAI
export LLM_PROVIDER="openai"
export OPENAI_API_KEY="your-openai-api-key"
export OPENAI_MODEL="gpt-4o-mini"
```

### 2. Run Test Queries with Live Routing

Execute queries through `app.main` without unsetting API keys:

```bash
# 1. Inventory Restock Check (WF001)
python -m app.main "Check today's inventory and identify products that need restocking."

# 2. Price Validation (WF002)
python -m app.main "Find products where vendor price differs by more than 10%."

# 3. Vendor File Processing (WF003)
python -m app.main "Process this vendor spreadsheet and show invalid rows."

# 4. Product Description Generator (WF004)
python -m app.main "Generate SEO content for this product." --product-name "TrailPro Tent" --category "Camping"

# 5. Customer Order Status (WF005)
python -m app.main "Where is order ORD-1001?"

# 6. Duplicate Product Detection (WF006)
python -m app.main "Find likely duplicate products in the catalog."

# 7. Marketing Campaign Brief (WF007)
python -m app.main "Create a campaign brief for the new collection." --campaign-goal "Spring Launch" --dates "May 1-15"

# 8. SEO Keyword Classification (WF008)
python -m app.main "Classify these keywords and map them to pages."

# 9. Employee Task Assignment (WF009)
python -m app.main "Assign this urgent task to the best available developer." --task-desc "Payment Gateway Integration" --skills "Python, Stripe"

# 10. Workflow Performance Report (WF010)
python -m app.main "Which workflows are failing most often?"

# 11. Unrelated Rejection (Expects NEEDS_CLARIFICATION, exit code 4)
python -m app.main "What is the weather in Paris?"
```

### 3. Expected Live Behavior

When a live provider is active:
- `Routing Mode:` will display `LLM` in terminal output and `"routing_mode": "llm"` in JSON reports.
- `Routing Confidence:` will reflect the model's reported confidence score.
- Queries that cannot be matched with sufficient confidence ($\ge 0.70$) will return `status: needs_clarification` (exit code 4) without executing domain tools.

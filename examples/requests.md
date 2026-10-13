# Example Workflow Execution Requests

This document catalogs the suite of benchmark requests used to verify the AI Workflow Agent offline and online routing pipelines.

The suite contains **22 benchmark requests**:
- **10 Primary Requests**: Extracted directly from the `Test_Questions` sheet in `data/workflows.xlsx`.
- **10 Custom Paraphrases**: Independent domain-specific variations testing intent generalization and token normalization.
- **2 Unrelated Rejection Queries**: Off-topic queries designed to ensure the system strictly avoids hallucinating workflows and cleanly exits with status `needs_clarification` (exit code 4).

---

## Benchmark Catalog

| Slug | Workflow ID | Category | Request Text |
| :--- | :---: | :--- | :--- |
| `wf001_restock_check` | `WF001` | Workbook Test_Question | `Which products need restocking?` |
| `wf001_paraphrase` | `WF001` | Custom Paraphrase | `Check inventory and tell me which products require restocking.` |
| `wf002_price_validation` | `WF002` | Workbook Test_Question | `Find products where vendor price differs by more than 10%.` |
| `wf002_paraphrase` | `WF002` | Custom Paraphrase | `Compare our internal catalog prices with supplier costs and flag large differences.` |
| `wf003_vendor_processing` | `WF003` | Workbook Test_Question | `Process this vendor spreadsheet and show invalid rows.` |
| `wf003_paraphrase` | `WF003` | Custom Paraphrase | `Clean the supplier CSV file, detect columns, and filter out invalid rows.` |
| `wf004_product_description` | `WF004` | Workbook Test_Question | `Generate SEO content for this product.` |
| `wf004_paraphrase` | `WF004` | Custom Paraphrase | `Write product descriptions, bullet points, and SEO metadata for our latest product.` |
| `wf005_order_status` | `WF005` | Workbook Test_Question | `Where is order ORD-1001?` |
| `wf005_paraphrase` | `WF005` | Custom Paraphrase | `Can you check tracking and shipping status for customer order ORD-1002?` |
| `wf006_duplicate_detection` | `WF006` | Workbook Test_Question | `Find likely duplicate products in the catalog.` |
| `wf006_paraphrase` | `WF006` | Custom Paraphrase | `Detect duplicate catalog listings that have matching titles or identical SKUs.` |
| `wf007_campaign_brief` | `WF007` | Workbook Test_Question | `Create a campaign brief for the new collection.` |
| `wf007_paraphrase` | `WF007` | Custom Paraphrase | `Draft a comprehensive marketing brief including audience messaging and channel checklist.` |
| `wf008_seo_keywords` | `WF008` | Workbook Test_Question | `Classify these keywords and map them to pages.` |
| `wf008_paraphrase` | `WF008` | Custom Paraphrase | `Group SEO search queries by user intent and assign keyword priorities.` |
| `wf009_task_assignment` | `WF009` | Workbook Test_Question | `Assign this urgent task to the best available developer.` |
| `wf009_paraphrase` | `WF009` | Custom Paraphrase | `Match this new task to an engineer based on skills and current capacity.` |
| `wf010_performance_report` | `WF010` | Workbook Test_Question | `Which workflows are failing most often?` |
| `wf010_paraphrase` | `WF010` | Custom Paraphrase | `Show execution health report, error rates, and slowest steps across automated pipelines.` |
| `unrelated_weather` | `null` | Unrelated Query | `What is the weather in Paris?` |
| `unrelated_poem` | `null` | Unrelated Query | `Write me a poem about cats.` |

---

## Running the Suite

Run all benchmark requests offline and verify generated outputs against `examples/expected.json`:

```bash
# On macOS / Linux:
bash scripts/run_examples.sh

# On Windows (PowerShell):
.\scripts\run_examples.ps1
```

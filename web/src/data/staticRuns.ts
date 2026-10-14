// Genuine pre-computed benchmark outputs from examples/output/
import { ExecutionReport } from "../types/workflow";

export const STATIC_RUNS: Record<string, ExecutionReport> = {
  "unrelated_poem": {
    "request": "Write me a poem about cats.",
    "selected_workflow_id": null,
    "selected_workflow_name": null,
    "routing_confidence": 0.0,
    "routing_reasoning": "Query could not be matched to any registered workflow via offline routing. Clarification required.",
    "status": "needs_clarification",
    "steps": [],
    "final_output": null,
    "errors": [
      "Query could not be matched to any registered workflow via offline routing. Clarification required."
    ],
    "clarification_required": true,
    "routing_mode": "offline",
    "warnings": []
  },
  "unrelated_weather": {
    "request": "What is the weather in Paris?",
    "selected_workflow_id": null,
    "selected_workflow_name": null,
    "routing_confidence": 0.0,
    "routing_reasoning": "Query could not be matched to any registered workflow via offline routing. Clarification required.",
    "status": "needs_clarification",
    "steps": [],
    "final_output": null,
    "errors": [
      "Query could not be matched to any registered workflow via offline routing. Clarification required."
    ],
    "clarification_required": true,
    "routing_mode": "offline",
    "warnings": []
  },
  "wf001_paraphrase": {
    "request": "Check inventory and tell me which products require restocking.",
    "selected_workflow_id": "WF001",
    "selected_workflow_name": "Inventory Restock Check",
    "routing_confidence": 0.8,
    "routing_reasoning": "Offline keyword match against trigger/metadata for WF001 (Inventory Restock Check): matched terms [inventory, product, restock].",
    "status": "success",
    "steps": [
      {
        "step_number": 1,
        "step_name": "Load inventory",
        "status": "completed",
        "output_summary": "Loaded 7 inventory item(s) from 'data/sample_inventory.csv'.",
        "output": {
          "inventory_items": [
            {
              "product_id": "PRD-001",
              "product_name": "Wireless Ergonomic Mouse",
              "current_stock": 5,
              "minimum_stock": 20,
              "unit_cost": 29.99,
              "supplier": "TechSupply Direct"
            },
            {
              "product_id": "PRD-002",
              "product_name": "Mechanical Gaming Keyboard",
              "current_stock": 25,
              "minimum_stock": 15,
              "unit_cost": 79.5,
              "supplier": "KeyCraft Labs"
            },
            {
              "product_id": "PRD-003",
              "product_name": "USB-C Multiport Hub",
              "current_stock": 0,
              "minimum_stock": 30,
              "unit_cost": 45.0,
              "supplier": "ConnectPro Inc"
            },
            {
              "product_id": "PRD-004",
              "product_name": "27-inch 4K Monitor",
              "current_stock": 10,
              "minimum_stock": 10,
              "unit_cost": 299.99,
              "supplier": "VisionTech Displays"
            },
            {
              "product_id": "PRD-005",
              "product_name": "Noise-Canceling Headphones",
              "current_stock": 3,
              "minimum_stock": 12,
              "unit_cost": 149.0,
              "supplier": "AudioWave Systems"
            },
            {
              "product_id": "PRD-006",
              "product_name": "Braided HDMI Cable 2m",
              "current_stock": 50,
              "minimum_stock": 25,
              "unit_cost": 8.99,
              "supplier": "CableLine Ltd"
            },
            {
              "product_id": "PRD-007",
              "product_name": "Aluminum Laptop Stand",
              "current_stock": 8,
              "minimum_stock": 15,
              "unit_cost": 34.5,
              "supplier": "ErgoDesk Co"
            }
          ],
          "total_loaded": 7,
          "csv_path": "data/sample_inventory.csv",
          "summary": "Loaded 7 inventory item(s) from 'data/sample_inventory.csv'."
        },
        "error": null
      },
      {
        "step_number": 2,
        "step_name": "compare current stock with minimum threshold",
        "status": "completed",
        "output_summary": "Compared 7 product(s) against minimum stock; 4 below threshold.",
        "output": {
          "compared_items": [
            {
              "product_id": "PRD-001",
              "product_name": "Wireless Ergonomic Mouse",
              "current_stock": 5,
              "minimum_stock": 20,
              "unit_cost": 29.99,
              "supplier": "TechSupply Direct",
              "is_low_stock": true,
              "effective_threshold": 20
            },
            {
              "product_id": "PRD-002",
              "product_name": "Mechanical Gaming Keyboard",
              "current_stock": 25,
              "minimum_stock": 15,
              "unit_cost": 79.5,
              "supplier": "KeyCraft Labs",
              "is_low_stock": false,
              "effective_threshold": 15
            },
            {
              "product_id": "PRD-003",
              "product_name": "USB-C Multiport Hub",
              "current_stock": 0,
              "minimum_stock": 30,
              "unit_cost": 45.0,
              "supplier": "ConnectPro Inc",
              "is_low_stock": true,
              "effective_threshold": 30
            },
            {
              "product_id": "PRD-004",
              "product_name": "27-inch 4K Monitor",
              "current_stock": 10,
              "minimum_stock": 10,
              "unit_cost": 299.99,
              "supplier": "VisionTech Displays",
              "is_low_stock": false,
              "effective_threshold": 10
            },
            {
              "product_id": "PRD-005",
              "product_name": "Noise-Canceling Headphones",
              "current_stock": 3,
              "minimum_stock": 12,
              "unit_cost": 149.0,
              "supplier": "AudioWave Systems",
              "is_low_stock": true,
              "effective_threshold": 12
            },
            {
              "product_id": "PRD-006",
              "product_name": "Braided HDMI Cable 2m",
              "current_stock": 50,
              "minimum_stock": 25,
              "unit_cost": 8.99,
              "supplier": "CableLine Ltd",
              "is_low_stock": false,
              "effective_threshold": 25
            },
            {
              "product_id": "PRD-007",
              "product_name": "Aluminum Laptop Stand",
              "current_stock": 8,
              "minimum_stock": 15,
              "unit_cost": 34.5,
              "supplier": "ErgoDesk Co",
              "is_low_stock": true,
              "effective_threshold": 15
            }
          ],
          "summary": "Compared 7 product(s) against minimum stock; 4 below threshold."
        },
        "error": null
      },
      {
        "step_number": 3,
        "step_name": "identify low-stock products",
        "status": "completed",
        "output_summary": "Identified 4 product(s) requiring restock.",
        "output": {
          "low_stock_items": [
            {
              "product_id": "PRD-001",
              "product_name": "Wireless Ergonomic Mouse",
              "current_stock": 5,
              "minimum_stock": 20,
              "unit_cost": 29.99,
              "supplier": "TechSupply Direct",
              "is_low_stock": true,
              "effective_threshold": 20
            },
            {
              "product_id": "PRD-003",
              "product_name": "USB-C Multiport Hub",
              "current_stock": 0,
              "minimum_stock": 30,
              "unit_cost": 45.0,
              "supplier": "ConnectPro Inc",
              "is_low_stock": true,
              "effective_threshold": 30
            },
            {
              "product_id": "PRD-005",
              "product_name": "Noise-Canceling Headphones",
              "current_stock": 3,
              "minimum_stock": 12,
              "unit_cost": 149.0,
              "supplier": "AudioWave Systems",
              "is_low_stock": true,
              "effective_threshold": 12
            },
            {
              "product_id": "PRD-007",
              "product_name": "Aluminum Laptop Stand",
              "current_stock": 8,
              "minimum_stock": 15,
              "unit_cost": 34.5,
              "supplier": "ErgoDesk Co",
              "is_low_stock": true,
              "effective_threshold": 15
            }
          ],
          "low_stock_count": 4,
          "summary": "Identified 4 product(s) requiring restock."
        },
        "error": null
      },
      {
        "step_number": 4,
        "step_name": "calculate reorder quantity",
        "status": "completed",
        "output_summary": "Calculated reorder quantities for 4 product(s) (61 total units).",
        "output": {
          "restock_items": [
            {
              "product_id": "PRD-001",
              "product_name": "Wireless Ergonomic Mouse",
              "current_stock": 5,
              "minimum_stock": 20,
              "reorder_quantity": 15,
              "unit_cost": 29.99,
              "supplier": "TechSupply Direct"
            },
            {
              "product_id": "PRD-003",
              "product_name": "USB-C Multiport Hub",
              "current_stock": 0,
              "minimum_stock": 30,
              "reorder_quantity": 30,
              "unit_cost": 45.0,
              "supplier": "ConnectPro Inc"
            },
            {
              "product_id": "PRD-005",
              "product_name": "Noise-Canceling Headphones",
              "current_stock": 3,
              "minimum_stock": 12,
              "reorder_quantity": 9,
              "unit_cost": 149.0,
              "supplier": "AudioWave Systems"
            },
            {
              "product_id": "PRD-007",
              "product_name": "Aluminum Laptop Stand",
              "current_stock": 8,
              "minimum_stock": 15,
              "reorder_quantity": 7,
              "unit_cost": 34.5,
              "supplier": "ErgoDesk Co"
            }
          ],
          "summary": "Calculated reorder quantities for 4 product(s) (61 total units)."
        },
        "error": null
      },
      {
        "step_number": 5,
        "step_name": "generate restock list",
        "status": "completed",
        "output_summary": "4 of 7 product(s) require restocking.",
        "output": {
          "products_requiring_restock": [
            {
              "product_id": "PRD-001",
              "product_name": "Wireless Ergonomic Mouse",
              "current_stock": 5,
              "minimum_stock": 20,
              "reorder_quantity": 15,
              "unit_cost": 29.99,
              "supplier": "TechSupply Direct"
            },
            {
              "product_id": "PRD-003",
              "product_name": "USB-C Multiport Hub",
              "current_stock": 0,
              "minimum_stock": 30,
              "reorder_quantity": 30,
              "unit_cost": 45.0,
              "supplier": "ConnectPro Inc"
            },
            {
              "product_id": "PRD-005",
              "product_name": "Noise-Canceling Headphones",
              "current_stock": 3,
              "minimum_stock": 12,
              "reorder_quantity": 9,
              "unit_cost": 149.0,
              "supplier": "AudioWave Systems"
            },
            {
              "product_id": "PRD-007",
              "product_name": "Aluminum Laptop Stand",
              "current_stock": 8,
              "minimum_stock": 15,
              "reorder_quantity": 7,
              "unit_cost": 34.5,
              "supplier": "ErgoDesk Co"
            }
          ],
          "total_products_checked": 7,
          "restock_required_count": 4,
          "summary": "4 of 7 product(s) require restocking."
        },
        "error": null
      }
    ],
    "final_output": {
      "products_requiring_restock": [
        {
          "product_id": "PRD-001",
          "product_name": "Wireless Ergonomic Mouse",
          "current_stock": 5,
          "minimum_stock": 20,
          "reorder_quantity": 15,
          "unit_cost": 29.99,
          "supplier": "TechSupply Direct"
        },
        {
          "product_id": "PRD-003",
          "product_name": "USB-C Multiport Hub",
          "current_stock": 0,
          "minimum_stock": 30,
          "reorder_quantity": 30,
          "unit_cost": 45.0,
          "supplier": "ConnectPro Inc"
        },
        {
          "product_id": "PRD-005",
          "product_name": "Noise-Canceling Headphones",
          "current_stock": 3,
          "minimum_stock": 12,
          "reorder_quantity": 9,
          "unit_cost": 149.0,
          "supplier": "AudioWave Systems"
        },
        {
          "product_id": "PRD-007",
          "product_name": "Aluminum Laptop Stand",
          "current_stock": 8,
          "minimum_stock": 15,
          "reorder_quantity": 7,
          "unit_cost": 34.5,
          "supplier": "ErgoDesk Co"
        }
      ],
      "total_products_checked": 7,
      "restock_required_count": 4,
      "summary": "4 of 7 product(s) require restocking."
    },
    "errors": [],
    "clarification_required": false,
    "routing_mode": "offline",
    "warnings": []
  },
  "wf001_restock_check": {
    "request": "Which products need restocking?",
    "selected_workflow_id": "WF001",
    "selected_workflow_name": "Inventory Restock Check",
    "routing_confidence": 0.8,
    "routing_reasoning": "Offline keyword match against trigger/metadata for WF001 (Inventory Restock Check): matched terms [ne, product, restock].",
    "status": "success",
    "steps": [
      {
        "step_number": 1,
        "step_name": "Load inventory",
        "status": "completed",
        "output_summary": "Loaded 7 inventory item(s) from 'data/sample_inventory.csv'.",
        "output": {
          "inventory_items": [
            {
              "product_id": "PRD-001",
              "product_name": "Wireless Ergonomic Mouse",
              "current_stock": 5,
              "minimum_stock": 20,
              "unit_cost": 29.99,
              "supplier": "TechSupply Direct"
            },
            {
              "product_id": "PRD-002",
              "product_name": "Mechanical Gaming Keyboard",
              "current_stock": 25,
              "minimum_stock": 15,
              "unit_cost": 79.5,
              "supplier": "KeyCraft Labs"
            },
            {
              "product_id": "PRD-003",
              "product_name": "USB-C Multiport Hub",
              "current_stock": 0,
              "minimum_stock": 30,
              "unit_cost": 45.0,
              "supplier": "ConnectPro Inc"
            },
            {
              "product_id": "PRD-004",
              "product_name": "27-inch 4K Monitor",
              "current_stock": 10,
              "minimum_stock": 10,
              "unit_cost": 299.99,
              "supplier": "VisionTech Displays"
            },
            {
              "product_id": "PRD-005",
              "product_name": "Noise-Canceling Headphones",
              "current_stock": 3,
              "minimum_stock": 12,
              "unit_cost": 149.0,
              "supplier": "AudioWave Systems"
            },
            {
              "product_id": "PRD-006",
              "product_name": "Braided HDMI Cable 2m",
              "current_stock": 50,
              "minimum_stock": 25,
              "unit_cost": 8.99,
              "supplier": "CableLine Ltd"
            },
            {
              "product_id": "PRD-007",
              "product_name": "Aluminum Laptop Stand",
              "current_stock": 8,
              "minimum_stock": 15,
              "unit_cost": 34.5,
              "supplier": "ErgoDesk Co"
            }
          ],
          "total_loaded": 7,
          "csv_path": "data/sample_inventory.csv",
          "summary": "Loaded 7 inventory item(s) from 'data/sample_inventory.csv'."
        },
        "error": null
      },
      {
        "step_number": 2,
        "step_name": "compare current stock with minimum threshold",
        "status": "completed",
        "output_summary": "Compared 7 product(s) against minimum stock; 4 below threshold.",
        "output": {
          "compared_items": [
            {
              "product_id": "PRD-001",
              "product_name": "Wireless Ergonomic Mouse",
              "current_stock": 5,
              "minimum_stock": 20,
              "unit_cost": 29.99,
              "supplier": "TechSupply Direct",
              "is_low_stock": true,
              "effective_threshold": 20
            },
            {
              "product_id": "PRD-002",
              "product_name": "Mechanical Gaming Keyboard",
              "current_stock": 25,
              "minimum_stock": 15,
              "unit_cost": 79.5,
              "supplier": "KeyCraft Labs",
              "is_low_stock": false,
              "effective_threshold": 15
            },
            {
              "product_id": "PRD-003",
              "product_name": "USB-C Multiport Hub",
              "current_stock": 0,
              "minimum_stock": 30,
              "unit_cost": 45.0,
              "supplier": "ConnectPro Inc",
              "is_low_stock": true,
              "effective_threshold": 30
            },
            {
              "product_id": "PRD-004",
              "product_name": "27-inch 4K Monitor",
              "current_stock": 10,
              "minimum_stock": 10,
              "unit_cost": 299.99,
              "supplier": "VisionTech Displays",
              "is_low_stock": false,
              "effective_threshold": 10
            },
            {
              "product_id": "PRD-005",
              "product_name": "Noise-Canceling Headphones",
              "current_stock": 3,
              "minimum_stock": 12,
              "unit_cost": 149.0,
              "supplier": "AudioWave Systems",
              "is_low_stock": true,
              "effective_threshold": 12
            },
            {
              "product_id": "PRD-006",
              "product_name": "Braided HDMI Cable 2m",
              "current_stock": 50,
              "minimum_stock": 25,
              "unit_cost": 8.99,
              "supplier": "CableLine Ltd",
              "is_low_stock": false,
              "effective_threshold": 25
            },
            {
              "product_id": "PRD-007",
              "product_name": "Aluminum Laptop Stand",
              "current_stock": 8,
              "minimum_stock": 15,
              "unit_cost": 34.5,
              "supplier": "ErgoDesk Co",
              "is_low_stock": true,
              "effective_threshold": 15
            }
          ],
          "summary": "Compared 7 product(s) against minimum stock; 4 below threshold."
        },
        "error": null
      },
      {
        "step_number": 3,
        "step_name": "identify low-stock products",
        "status": "completed",
        "output_summary": "Identified 4 product(s) requiring restock.",
        "output": {
          "low_stock_items": [
            {
              "product_id": "PRD-001",
              "product_name": "Wireless Ergonomic Mouse",
              "current_stock": 5,
              "minimum_stock": 20,
              "unit_cost": 29.99,
              "supplier": "TechSupply Direct",
              "is_low_stock": true,
              "effective_threshold": 20
            },
            {
              "product_id": "PRD-003",
              "product_name": "USB-C Multiport Hub",
              "current_stock": 0,
              "minimum_stock": 30,
              "unit_cost": 45.0,
              "supplier": "ConnectPro Inc",
              "is_low_stock": true,
              "effective_threshold": 30
            },
            {
              "product_id": "PRD-005",
              "product_name": "Noise-Canceling Headphones",
              "current_stock": 3,
              "minimum_stock": 12,
              "unit_cost": 149.0,
              "supplier": "AudioWave Systems",
              "is_low_stock": true,
              "effective_threshold": 12
            },
            {
              "product_id": "PRD-007",
              "product_name": "Aluminum Laptop Stand",
              "current_stock": 8,
              "minimum_stock": 15,
              "unit_cost": 34.5,
              "supplier": "ErgoDesk Co",
              "is_low_stock": true,
              "effective_threshold": 15
            }
          ],
          "low_stock_count": 4,
          "summary": "Identified 4 product(s) requiring restock."
        },
        "error": null
      },
      {
        "step_number": 4,
        "step_name": "calculate reorder quantity",
        "status": "completed",
        "output_summary": "Calculated reorder quantities for 4 product(s) (61 total units).",
        "output": {
          "restock_items": [
            {
              "product_id": "PRD-001",
              "product_name": "Wireless Ergonomic Mouse",
              "current_stock": 5,
              "minimum_stock": 20,
              "reorder_quantity": 15,
              "unit_cost": 29.99,
              "supplier": "TechSupply Direct"
            },
            {
              "product_id": "PRD-003",
              "product_name": "USB-C Multiport Hub",
              "current_stock": 0,
              "minimum_stock": 30,
              "reorder_quantity": 30,
              "unit_cost": 45.0,
              "supplier": "ConnectPro Inc"
            },
            {
              "product_id": "PRD-005",
              "product_name": "Noise-Canceling Headphones",
              "current_stock": 3,
              "minimum_stock": 12,
              "reorder_quantity": 9,
              "unit_cost": 149.0,
              "supplier": "AudioWave Systems"
            },
            {
              "product_id": "PRD-007",
              "product_name": "Aluminum Laptop Stand",
              "current_stock": 8,
              "minimum_stock": 15,
              "reorder_quantity": 7,
              "unit_cost": 34.5,
              "supplier": "ErgoDesk Co"
            }
          ],
          "summary": "Calculated reorder quantities for 4 product(s) (61 total units)."
        },
        "error": null
      },
      {
        "step_number": 5,
        "step_name": "generate restock list",
        "status": "completed",
        "output_summary": "4 of 7 product(s) require restocking.",
        "output": {
          "products_requiring_restock": [
            {
              "product_id": "PRD-001",
              "product_name": "Wireless Ergonomic Mouse",
              "current_stock": 5,
              "minimum_stock": 20,
              "reorder_quantity": 15,
              "unit_cost": 29.99,
              "supplier": "TechSupply Direct"
            },
            {
              "product_id": "PRD-003",
              "product_name": "USB-C Multiport Hub",
              "current_stock": 0,
              "minimum_stock": 30,
              "reorder_quantity": 30,
              "unit_cost": 45.0,
              "supplier": "ConnectPro Inc"
            },
            {
              "product_id": "PRD-005",
              "product_name": "Noise-Canceling Headphones",
              "current_stock": 3,
              "minimum_stock": 12,
              "reorder_quantity": 9,
              "unit_cost": 149.0,
              "supplier": "AudioWave Systems"
            },
            {
              "product_id": "PRD-007",
              "product_name": "Aluminum Laptop Stand",
              "current_stock": 8,
              "minimum_stock": 15,
              "reorder_quantity": 7,
              "unit_cost": 34.5,
              "supplier": "ErgoDesk Co"
            }
          ],
          "total_products_checked": 7,
          "restock_required_count": 4,
          "summary": "4 of 7 product(s) require restocking."
        },
        "error": null
      }
    ],
    "final_output": {
      "products_requiring_restock": [
        {
          "product_id": "PRD-001",
          "product_name": "Wireless Ergonomic Mouse",
          "current_stock": 5,
          "minimum_stock": 20,
          "reorder_quantity": 15,
          "unit_cost": 29.99,
          "supplier": "TechSupply Direct"
        },
        {
          "product_id": "PRD-003",
          "product_name": "USB-C Multiport Hub",
          "current_stock": 0,
          "minimum_stock": 30,
          "reorder_quantity": 30,
          "unit_cost": 45.0,
          "supplier": "ConnectPro Inc"
        },
        {
          "product_id": "PRD-005",
          "product_name": "Noise-Canceling Headphones",
          "current_stock": 3,
          "minimum_stock": 12,
          "reorder_quantity": 9,
          "unit_cost": 149.0,
          "supplier": "AudioWave Systems"
        },
        {
          "product_id": "PRD-007",
          "product_name": "Aluminum Laptop Stand",
          "current_stock": 8,
          "minimum_stock": 15,
          "reorder_quantity": 7,
          "unit_cost": 34.5,
          "supplier": "ErgoDesk Co"
        }
      ],
      "total_products_checked": 7,
      "restock_required_count": 4,
      "summary": "4 of 7 product(s) require restocking."
    },
    "errors": [],
    "clarification_required": false,
    "routing_mode": "offline",
    "warnings": []
  },
  "wf002_paraphrase": {
    "request": "Compare our internal catalog prices with supplier costs and flag large differences.",
    "selected_workflow_id": "WF002",
    "selected_workflow_name": "Product Price Validation",
    "routing_confidence": 0.9,
    "routing_reasoning": "Offline keyword match against trigger/metadata for WF002 (Product Price Validation): matched terms [compare, flag, internal, price, vendor].",
    "status": "success",
    "steps": [
      {
        "step_number": 1,
        "step_name": "Load product prices",
        "status": "completed",
        "output_summary": "Loaded 8 internal product(s) and 8 vendor record(s).",
        "output": {
          "internal_prices": [
            {
              "sku": "SKU-001",
              "product_name": "Wireless Ergonomic Mouse",
              "internal_price": "25.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-002",
              "product_name": "Mechanical Gaming Keyboard",
              "internal_price": "80.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-003",
              "product_name": "USB-C Multiport Hub",
              "internal_price": "40.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-004",
              "product_name": "27-inch 4K Monitor",
              "internal_price": "300.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-005",
              "product_name": "Noise-Canceling Headphones",
              "internal_price": "150.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-006",
              "product_name": "Braided HDMI Cable 2m",
              "internal_price": "10.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-007",
              "product_name": "Aluminum Laptop Stand",
              "internal_price": "35.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-008",
              "product_name": "1080p HD Pro Webcam",
              "internal_price": "50.00",
              "currency": "USD"
            }
          ],
          "vendor_prices": [
            {
              "sku": "SKU-001",
              "vendor_name": "Alpha Suppliers",
              "vendor_price": "26.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-002",
              "vendor_name": "KeyCraft Wholesale",
              "vendor_price": "92.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-003",
              "vendor_name": "ConnectPro Direct",
              "vendor_price": "44.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-004",
              "vendor_name": "VisionTech Displays",
              "vendor_price": "255.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-005",
              "vendor_name": "AudioWave Systems",
              "vendor_price": "145.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-006",
              "vendor_name": "CableLine Global",
              "vendor_price": "12.50",
              "currency": "USD"
            },
            {
              "sku": "SKU-007",
              "vendor_name": "ErgoDesk Co",
              "vendor_price": "38.50",
              "currency": "USD"
            },
            {
              "sku": "SKU-099",
              "vendor_name": "NewVendor Imports",
              "vendor_price": "19.99",
              "currency": "USD"
            }
          ],
          "total_internal": 8,
          "total_vendor": 8,
          "summary": "Loaded 8 internal product(s) and 8 vendor record(s)."
        },
        "error": null
      },
      {
        "step_number": 2,
        "step_name": "match products by SKU",
        "status": "completed",
        "output_summary": "Matched 7 product(s) by SKU. 1 vendor record(s) unmatched.",
        "output": {
          "matched_pairs": [
            {
              "sku": "SKU-001",
              "product_name": "Wireless Ergonomic Mouse",
              "vendor_name": "Alpha Suppliers",
              "internal_price": "25.00",
              "vendor_price": "26.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-002",
              "product_name": "Mechanical Gaming Keyboard",
              "vendor_name": "KeyCraft Wholesale",
              "internal_price": "80.00",
              "vendor_price": "92.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-003",
              "product_name": "USB-C Multiport Hub",
              "vendor_name": "ConnectPro Direct",
              "internal_price": "40.00",
              "vendor_price": "44.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-004",
              "product_name": "27-inch 4K Monitor",
              "vendor_name": "VisionTech Displays",
              "internal_price": "300.00",
              "vendor_price": "255.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-005",
              "product_name": "Noise-Canceling Headphones",
              "vendor_name": "AudioWave Systems",
              "internal_price": "150.00",
              "vendor_price": "145.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-006",
              "product_name": "Braided HDMI Cable 2m",
              "vendor_name": "CableLine Global",
              "internal_price": "10.00",
              "vendor_price": "12.50",
              "currency": "USD"
            },
            {
              "sku": "SKU-007",
              "product_name": "Aluminum Laptop Stand",
              "vendor_name": "ErgoDesk Co",
              "internal_price": "35.00",
              "vendor_price": "38.50",
              "currency": "USD"
            }
          ],
          "unmatched_vendor": [
            {
              "sku": "SKU-099",
              "vendor_name": "NewVendor Imports",
              "vendor_price": "19.99",
              "reason": "SKU not found in internal product catalog"
            }
          ],
          "unmatched_internal": [
            {
              "sku": "SKU-008",
              "product_name": "1080p HD Pro Webcam",
              "internal_price": "50.00",
              "reason": "SKU not found in vendor price list"
            }
          ],
          "match_count": 7,
          "summary": "Matched 7 product(s) by SKU. 1 vendor record(s) unmatched."
        },
        "error": null
      },
      {
        "step_number": 3,
        "step_name": "compare internal and vendor prices",
        "status": "completed",
        "output_summary": "Compared prices for 7 matched product(s).",
        "output": {
          "compared_products": [
            {
              "sku": "SKU-001",
              "product_name": "Wireless Ergonomic Mouse",
              "vendor_name": "Alpha Suppliers",
              "internal_price": "25.00",
              "vendor_price": "26.00",
              "currency": "USD",
              "price_difference": 1.0
            },
            {
              "sku": "SKU-002",
              "product_name": "Mechanical Gaming Keyboard",
              "vendor_name": "KeyCraft Wholesale",
              "internal_price": "80.00",
              "vendor_price": "92.00",
              "currency": "USD",
              "price_difference": 12.0
            },
            {
              "sku": "SKU-003",
              "product_name": "USB-C Multiport Hub",
              "vendor_name": "ConnectPro Direct",
              "internal_price": "40.00",
              "vendor_price": "44.00",
              "currency": "USD",
              "price_difference": 4.0
            },
            {
              "sku": "SKU-004",
              "product_name": "27-inch 4K Monitor",
              "vendor_name": "VisionTech Displays",
              "internal_price": "300.00",
              "vendor_price": "255.00",
              "currency": "USD",
              "price_difference": -45.0
            },
            {
              "sku": "SKU-005",
              "product_name": "Noise-Canceling Headphones",
              "vendor_name": "AudioWave Systems",
              "internal_price": "150.00",
              "vendor_price": "145.00",
              "currency": "USD",
              "price_difference": -5.0
            },
            {
              "sku": "SKU-006",
              "product_name": "Braided HDMI Cable 2m",
              "vendor_name": "CableLine Global",
              "internal_price": "10.00",
              "vendor_price": "12.50",
              "currency": "USD",
              "price_difference": 2.5
            },
            {
              "sku": "SKU-007",
              "product_name": "Aluminum Laptop Stand",
              "vendor_name": "ErgoDesk Co",
              "internal_price": "35.00",
              "vendor_price": "38.50",
              "currency": "USD",
              "price_difference": 3.5
            }
          ],
          "summary": "Compared prices for 7 matched product(s)."
        },
        "error": null
      },
      {
        "step_number": 4,
        "step_name": "calculate percentage difference",
        "status": "completed",
        "output_summary": "Calculated percentage differences for 7 product(s).",
        "output": {
          "price_evaluations": [
            {
              "sku": "SKU-001",
              "product_name": "Wireless Ergonomic Mouse",
              "vendor_name": "Alpha Suppliers",
              "internal_price": "25.00",
              "vendor_price": "26.00",
              "currency": "USD",
              "price_difference": 1.0,
              "percentage_difference": 4.0
            },
            {
              "sku": "SKU-002",
              "product_name": "Mechanical Gaming Keyboard",
              "vendor_name": "KeyCraft Wholesale",
              "internal_price": "80.00",
              "vendor_price": "92.00",
              "currency": "USD",
              "price_difference": 12.0,
              "percentage_difference": 15.0
            },
            {
              "sku": "SKU-003",
              "product_name": "USB-C Multiport Hub",
              "vendor_name": "ConnectPro Direct",
              "internal_price": "40.00",
              "vendor_price": "44.00",
              "currency": "USD",
              "price_difference": 4.0,
              "percentage_difference": 10.0
            },
            {
              "sku": "SKU-004",
              "product_name": "27-inch 4K Monitor",
              "vendor_name": "VisionTech Displays",
              "internal_price": "300.00",
              "vendor_price": "255.00",
              "currency": "USD",
              "price_difference": -45.0,
              "percentage_difference": 15.0
            },
            {
              "sku": "SKU-005",
              "product_name": "Noise-Canceling Headphones",
              "vendor_name": "AudioWave Systems",
              "internal_price": "150.00",
              "vendor_price": "145.00",
              "currency": "USD",
              "price_difference": -5.0,
              "percentage_difference": 3.33
            },
            {
              "sku": "SKU-006",
              "product_name": "Braided HDMI Cable 2m",
              "vendor_name": "CableLine Global",
              "internal_price": "10.00",
              "vendor_price": "12.50",
              "currency": "USD",
              "price_difference": 2.5,
              "percentage_difference": 25.0
            },
            {
              "sku": "SKU-007",
              "product_name": "Aluminum Laptop Stand",
              "vendor_name": "ErgoDesk Co",
              "internal_price": "35.00",
              "vendor_price": "38.50",
              "currency": "USD",
              "price_difference": 3.5,
              "percentage_difference": 10.0
            }
          ],
          "summary": "Calculated percentage differences for 7 product(s)."
        },
        "error": null
      },
      {
        "step_number": 5,
        "step_name": "flag exceptions",
        "status": "completed",
        "output_summary": "Validated 7 products: 3 exception(s) exceeding 10.0% threshold.",
        "output": {
          "matched_products": [
            {
              "sku": "SKU-001",
              "product_name": "Wireless Ergonomic Mouse",
              "vendor_name": "Alpha Suppliers",
              "internal_price": "25.00",
              "vendor_price": "26.00",
              "currency": "USD",
              "price_difference": 1.0,
              "percentage_difference": 4.0,
              "is_exception": false,
              "validation_status": "COMPLIANT"
            },
            {
              "sku": "SKU-002",
              "product_name": "Mechanical Gaming Keyboard",
              "vendor_name": "KeyCraft Wholesale",
              "internal_price": "80.00",
              "vendor_price": "92.00",
              "currency": "USD",
              "price_difference": 12.0,
              "percentage_difference": 15.0,
              "is_exception": true,
              "validation_status": "EXCEPTION_EXCEEDS_10_PERCENT"
            },
            {
              "sku": "SKU-003",
              "product_name": "USB-C Multiport Hub",
              "vendor_name": "ConnectPro Direct",
              "internal_price": "40.00",
              "vendor_price": "44.00",
              "currency": "USD",
              "price_difference": 4.0,
              "percentage_difference": 10.0,
              "is_exception": false,
              "validation_status": "COMPLIANT"
            },
            {
              "sku": "SKU-004",
              "product_name": "27-inch 4K Monitor",
              "vendor_name": "VisionTech Displays",
              "internal_price": "300.00",
              "vendor_price": "255.00",
              "currency": "USD",
              "price_difference": -45.0,
              "percentage_difference": 15.0,
              "is_exception": true,
              "validation_status": "EXCEPTION_EXCEEDS_10_PERCENT"
            },
            {
              "sku": "SKU-005",
              "product_name": "Noise-Canceling Headphones",
              "vendor_name": "AudioWave Systems",
              "internal_price": "150.00",
              "vendor_price": "145.00",
              "currency": "USD",
              "price_difference": -5.0,
              "percentage_difference": 3.33,
              "is_exception": false,
              "validation_status": "COMPLIANT"
            },
            {
              "sku": "SKU-006",
              "product_name": "Braided HDMI Cable 2m",
              "vendor_name": "CableLine Global",
              "internal_price": "10.00",
              "vendor_price": "12.50",
              "currency": "USD",
              "price_difference": 2.5,
              "percentage_difference": 25.0,
              "is_exception": true,
              "validation_status": "EXCEPTION_EXCEEDS_10_PERCENT"
            },
            {
              "sku": "SKU-007",
              "product_name": "Aluminum Laptop Stand",
              "vendor_name": "ErgoDesk Co",
              "internal_price": "35.00",
              "vendor_price": "38.50",
              "currency": "USD",
              "price_difference": 3.5,
              "percentage_difference": 10.0,
              "is_exception": false,
              "validation_status": "COMPLIANT"
            }
          ],
          "exceptions": [
            {
              "sku": "SKU-002",
              "product_name": "Mechanical Gaming Keyboard",
              "vendor_name": "KeyCraft Wholesale",
              "internal_price": "80.00",
              "vendor_price": "92.00",
              "currency": "USD",
              "price_difference": 12.0,
              "percentage_difference": 15.0,
              "is_exception": true,
              "validation_status": "EXCEPTION_EXCEEDS_10_PERCENT"
            },
            {
              "sku": "SKU-004",
              "product_name": "27-inch 4K Monitor",
              "vendor_name": "VisionTech Displays",
              "internal_price": "300.00",
              "vendor_price": "255.00",
              "currency": "USD",
              "price_difference": -45.0,
              "percentage_difference": 15.0,
              "is_exception": true,
              "validation_status": "EXCEPTION_EXCEEDS_10_PERCENT"
            },
            {
              "sku": "SKU-006",
              "product_name": "Braided HDMI Cable 2m",
              "vendor_name": "CableLine Global",
              "internal_price": "10.00",
              "vendor_price": "12.50",
              "currency": "USD",
              "price_difference": 2.5,
              "percentage_difference": 25.0,
              "is_exception": true,
              "validation_status": "EXCEPTION_EXCEEDS_10_PERCENT"
            }
          ],
          "exception_count": 3,
          "total_matched": 7,
          "unmatched_vendor_records": [
            {
              "sku": "SKU-099",
              "vendor_name": "NewVendor Imports",
              "vendor_price": "19.99",
              "reason": "SKU not found in internal product catalog"
            }
          ],
          "unmatched_internal_records": [
            {
              "sku": "SKU-008",
              "product_name": "1080p HD Pro Webcam",
              "internal_price": "50.00",
              "reason": "SKU not found in vendor price list"
            }
          ],
          "summary": "Validated 7 products: 3 exception(s) exceeding 10.0% threshold."
        },
        "error": null
      }
    ],
    "final_output": {
      "matched_products": [
        {
          "sku": "SKU-001",
          "product_name": "Wireless Ergonomic Mouse",
          "vendor_name": "Alpha Suppliers",
          "internal_price": "25.00",
          "vendor_price": "26.00",
          "currency": "USD",
          "price_difference": 1.0,
          "percentage_difference": 4.0,
          "is_exception": false,
          "validation_status": "COMPLIANT"
        },
        {
          "sku": "SKU-002",
          "product_name": "Mechanical Gaming Keyboard",
          "vendor_name": "KeyCraft Wholesale",
          "internal_price": "80.00",
          "vendor_price": "92.00",
          "currency": "USD",
          "price_difference": 12.0,
          "percentage_difference": 15.0,
          "is_exception": true,
          "validation_status": "EXCEPTION_EXCEEDS_10_PERCENT"
        },
        {
          "sku": "SKU-003",
          "product_name": "USB-C Multiport Hub",
          "vendor_name": "ConnectPro Direct",
          "internal_price": "40.00",
          "vendor_price": "44.00",
          "currency": "USD",
          "price_difference": 4.0,
          "percentage_difference": 10.0,
          "is_exception": false,
          "validation_status": "COMPLIANT"
        },
        {
          "sku": "SKU-004",
          "product_name": "27-inch 4K Monitor",
          "vendor_name": "VisionTech Displays",
          "internal_price": "300.00",
          "vendor_price": "255.00",
          "currency": "USD",
          "price_difference": -45.0,
          "percentage_difference": 15.0,
          "is_exception": true,
          "validation_status": "EXCEPTION_EXCEEDS_10_PERCENT"
        },
        {
          "sku": "SKU-005",
          "product_name": "Noise-Canceling Headphones",
          "vendor_name": "AudioWave Systems",
          "internal_price": "150.00",
          "vendor_price": "145.00",
          "currency": "USD",
          "price_difference": -5.0,
          "percentage_difference": 3.33,
          "is_exception": false,
          "validation_status": "COMPLIANT"
        },
        {
          "sku": "SKU-006",
          "product_name": "Braided HDMI Cable 2m",
          "vendor_name": "CableLine Global",
          "internal_price": "10.00",
          "vendor_price": "12.50",
          "currency": "USD",
          "price_difference": 2.5,
          "percentage_difference": 25.0,
          "is_exception": true,
          "validation_status": "EXCEPTION_EXCEEDS_10_PERCENT"
        },
        {
          "sku": "SKU-007",
          "product_name": "Aluminum Laptop Stand",
          "vendor_name": "ErgoDesk Co",
          "internal_price": "35.00",
          "vendor_price": "38.50",
          "currency": "USD",
          "price_difference": 3.5,
          "percentage_difference": 10.0,
          "is_exception": false,
          "validation_status": "COMPLIANT"
        }
      ],
      "exceptions": [
        {
          "sku": "SKU-002",
          "product_name": "Mechanical Gaming Keyboard",
          "vendor_name": "KeyCraft Wholesale",
          "internal_price": "80.00",
          "vendor_price": "92.00",
          "currency": "USD",
          "price_difference": 12.0,
          "percentage_difference": 15.0,
          "is_exception": true,
          "validation_status": "EXCEPTION_EXCEEDS_10_PERCENT"
        },
        {
          "sku": "SKU-004",
          "product_name": "27-inch 4K Monitor",
          "vendor_name": "VisionTech Displays",
          "internal_price": "300.00",
          "vendor_price": "255.00",
          "currency": "USD",
          "price_difference": -45.0,
          "percentage_difference": 15.0,
          "is_exception": true,
          "validation_status": "EXCEPTION_EXCEEDS_10_PERCENT"
        },
        {
          "sku": "SKU-006",
          "product_name": "Braided HDMI Cable 2m",
          "vendor_name": "CableLine Global",
          "internal_price": "10.00",
          "vendor_price": "12.50",
          "currency": "USD",
          "price_difference": 2.5,
          "percentage_difference": 25.0,
          "is_exception": true,
          "validation_status": "EXCEPTION_EXCEEDS_10_PERCENT"
        }
      ],
      "exception_count": 3,
      "total_matched": 7,
      "unmatched_vendor_records": [
        {
          "sku": "SKU-099",
          "vendor_name": "NewVendor Imports",
          "vendor_price": "19.99",
          "reason": "SKU not found in internal product catalog"
        }
      ],
      "unmatched_internal_records": [
        {
          "sku": "SKU-008",
          "product_name": "1080p HD Pro Webcam",
          "internal_price": "50.00",
          "reason": "SKU not found in vendor price list"
        }
      ],
      "summary": "Validated 7 products: 3 exception(s) exceeding 10.0% threshold."
    },
    "errors": [],
    "clarification_required": false,
    "routing_mode": "offline",
    "warnings": []
  },
  "wf002_price_validation": {
    "request": "Find products where vendor price differs by more than 10%.",
    "selected_workflow_id": "WF002",
    "selected_workflow_name": "Product Price Validation",
    "routing_confidence": 0.8,
    "routing_reasoning": "Offline keyword match against trigger/metadata for WF002 (Product Price Validation): matched terms [price, product, vendor].",
    "status": "success",
    "steps": [
      {
        "step_number": 1,
        "step_name": "Load product prices",
        "status": "completed",
        "output_summary": "Loaded 8 internal product(s) and 8 vendor record(s).",
        "output": {
          "internal_prices": [
            {
              "sku": "SKU-001",
              "product_name": "Wireless Ergonomic Mouse",
              "internal_price": "25.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-002",
              "product_name": "Mechanical Gaming Keyboard",
              "internal_price": "80.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-003",
              "product_name": "USB-C Multiport Hub",
              "internal_price": "40.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-004",
              "product_name": "27-inch 4K Monitor",
              "internal_price": "300.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-005",
              "product_name": "Noise-Canceling Headphones",
              "internal_price": "150.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-006",
              "product_name": "Braided HDMI Cable 2m",
              "internal_price": "10.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-007",
              "product_name": "Aluminum Laptop Stand",
              "internal_price": "35.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-008",
              "product_name": "1080p HD Pro Webcam",
              "internal_price": "50.00",
              "currency": "USD"
            }
          ],
          "vendor_prices": [
            {
              "sku": "SKU-001",
              "vendor_name": "Alpha Suppliers",
              "vendor_price": "26.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-002",
              "vendor_name": "KeyCraft Wholesale",
              "vendor_price": "92.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-003",
              "vendor_name": "ConnectPro Direct",
              "vendor_price": "44.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-004",
              "vendor_name": "VisionTech Displays",
              "vendor_price": "255.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-005",
              "vendor_name": "AudioWave Systems",
              "vendor_price": "145.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-006",
              "vendor_name": "CableLine Global",
              "vendor_price": "12.50",
              "currency": "USD"
            },
            {
              "sku": "SKU-007",
              "vendor_name": "ErgoDesk Co",
              "vendor_price": "38.50",
              "currency": "USD"
            },
            {
              "sku": "SKU-099",
              "vendor_name": "NewVendor Imports",
              "vendor_price": "19.99",
              "currency": "USD"
            }
          ],
          "total_internal": 8,
          "total_vendor": 8,
          "summary": "Loaded 8 internal product(s) and 8 vendor record(s)."
        },
        "error": null
      },
      {
        "step_number": 2,
        "step_name": "match products by SKU",
        "status": "completed",
        "output_summary": "Matched 7 product(s) by SKU. 1 vendor record(s) unmatched.",
        "output": {
          "matched_pairs": [
            {
              "sku": "SKU-001",
              "product_name": "Wireless Ergonomic Mouse",
              "vendor_name": "Alpha Suppliers",
              "internal_price": "25.00",
              "vendor_price": "26.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-002",
              "product_name": "Mechanical Gaming Keyboard",
              "vendor_name": "KeyCraft Wholesale",
              "internal_price": "80.00",
              "vendor_price": "92.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-003",
              "product_name": "USB-C Multiport Hub",
              "vendor_name": "ConnectPro Direct",
              "internal_price": "40.00",
              "vendor_price": "44.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-004",
              "product_name": "27-inch 4K Monitor",
              "vendor_name": "VisionTech Displays",
              "internal_price": "300.00",
              "vendor_price": "255.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-005",
              "product_name": "Noise-Canceling Headphones",
              "vendor_name": "AudioWave Systems",
              "internal_price": "150.00",
              "vendor_price": "145.00",
              "currency": "USD"
            },
            {
              "sku": "SKU-006",
              "product_name": "Braided HDMI Cable 2m",
              "vendor_name": "CableLine Global",
              "internal_price": "10.00",
              "vendor_price": "12.50",
              "currency": "USD"
            },
            {
              "sku": "SKU-007",
              "product_name": "Aluminum Laptop Stand",
              "vendor_name": "ErgoDesk Co",
              "internal_price": "35.00",
              "vendor_price": "38.50",
              "currency": "USD"
            }
          ],
          "unmatched_vendor": [
            {
              "sku": "SKU-099",
              "vendor_name": "NewVendor Imports",
              "vendor_price": "19.99",
              "reason": "SKU not found in internal product catalog"
            }
          ],
          "unmatched_internal": [
            {
              "sku": "SKU-008",
              "product_name": "1080p HD Pro Webcam",
              "internal_price": "50.00",
              "reason": "SKU not found in vendor price list"
            }
          ],
          "match_count": 7,
          "summary": "Matched 7 product(s) by SKU. 1 vendor record(s) unmatched."
        },
        "error": null
      },
      {
        "step_number": 3,
        "step_name": "compare internal and vendor prices",
        "status": "completed",
        "output_summary": "Compared prices for 7 matched product(s).",
        "output": {
          "compared_products": [
            {
              "sku": "SKU-001",
              "product_name": "Wireless Ergonomic Mouse",
              "vendor_name": "Alpha Suppliers",
              "internal_price": "25.00",
              "vendor_price": "26.00",
              "currency": "USD",
              "price_difference": 1.0
            },
            {
              "sku": "SKU-002",
              "product_name": "Mechanical Gaming Keyboard",
              "vendor_name": "KeyCraft Wholesale",
              "internal_price": "80.00",
              "vendor_price": "92.00",
              "currency": "USD",
              "price_difference": 12.0
            },
            {
              "sku": "SKU-003",
              "product_name": "USB-C Multiport Hub",
              "vendor_name": "ConnectPro Direct",
              "internal_price": "40.00",
              "vendor_price": "44.00",
              "currency": "USD",
              "price_difference": 4.0
            },
            {
              "sku": "SKU-004",
              "product_name": "27-inch 4K Monitor",
              "vendor_name": "VisionTech Displays",
              "internal_price": "300.00",
              "vendor_price": "255.00",
              "currency": "USD",
              "price_difference": -45.0
            },
            {
              "sku": "SKU-005",
              "product_name": "Noise-Canceling Headphones",
              "vendor_name": "AudioWave Systems",
              "internal_price": "150.00",
              "vendor_price": "145.00",
              "currency": "USD",
              "price_difference": -5.0
            },
            {
              "sku": "SKU-006",
              "product_name": "Braided HDMI Cable 2m",
              "vendor_name": "CableLine Global",
              "internal_price": "10.00",
              "vendor_price": "12.50",
              "currency": "USD",
              "price_difference": 2.5
            },
            {
              "sku": "SKU-007",
              "product_name": "Aluminum Laptop Stand",
              "vendor_name": "ErgoDesk Co",
              "internal_price": "35.00",
              "vendor_price": "38.50",
              "currency": "USD",
              "price_difference": 3.5
            }
          ],
          "summary": "Compared prices for 7 matched product(s)."
        },
        "error": null
      },
      {
        "step_number": 4,
        "step_name": "calculate percentage difference",
        "status": "completed",
        "output_summary": "Calculated percentage differences for 7 product(s).",
        "output": {
          "price_evaluations": [
            {
              "sku": "SKU-001",
              "product_name": "Wireless Ergonomic Mouse",
              "vendor_name": "Alpha Suppliers",
              "internal_price": "25.00",
              "vendor_price": "26.00",
              "currency": "USD",
              "price_difference": 1.0,
              "percentage_difference": 4.0
            },
            {
              "sku": "SKU-002",
              "product_name": "Mechanical Gaming Keyboard",
              "vendor_name": "KeyCraft Wholesale",
              "internal_price": "80.00",
              "vendor_price": "92.00",
              "currency": "USD",
              "price_difference": 12.0,
              "percentage_difference": 15.0
            },
            {
              "sku": "SKU-003",
              "product_name": "USB-C Multiport Hub",
              "vendor_name": "ConnectPro Direct",
              "internal_price": "40.00",
              "vendor_price": "44.00",
              "currency": "USD",
              "price_difference": 4.0,
              "percentage_difference": 10.0
            },
            {
              "sku": "SKU-004",
              "product_name": "27-inch 4K Monitor",
              "vendor_name": "VisionTech Displays",
              "internal_price": "300.00",
              "vendor_price": "255.00",
              "currency": "USD",
              "price_difference": -45.0,
              "percentage_difference": 15.0
            },
            {
              "sku": "SKU-005",
              "product_name": "Noise-Canceling Headphones",
              "vendor_name": "AudioWave Systems",
              "internal_price": "150.00",
              "vendor_price": "145.00",
              "currency": "USD",
              "price_difference": -5.0,
              "percentage_difference": 3.33
            },
            {
              "sku": "SKU-006",
              "product_name": "Braided HDMI Cable 2m",
              "vendor_name": "CableLine Global",
              "internal_price": "10.00",
              "vendor_price": "12.50",
              "currency": "USD",
              "price_difference": 2.5,
              "percentage_difference": 25.0
            },
            {
              "sku": "SKU-007",
              "product_name": "Aluminum Laptop Stand",
              "vendor_name": "ErgoDesk Co",
              "internal_price": "35.00",
              "vendor_price": "38.50",
              "currency": "USD",
              "price_difference": 3.5,
              "percentage_difference": 10.0
            }
          ],
          "summary": "Calculated percentage differences for 7 product(s)."
        },
        "error": null
      },
      {
        "step_number": 5,
        "step_name": "flag exceptions",
        "status": "completed",
        "output_summary": "Validated 7 products: 3 exception(s) exceeding 10.0% threshold.",
        "output": {
          "matched_products": [
            {
              "sku": "SKU-001",
              "product_name": "Wireless Ergonomic Mouse",
              "vendor_name": "Alpha Suppliers",
              "internal_price": "25.00",
              "vendor_price": "26.00",
              "currency": "USD",
              "price_difference": 1.0,
              "percentage_difference": 4.0,
              "is_exception": false,
              "validation_status": "COMPLIANT"
            },
            {
              "sku": "SKU-002",
              "product_name": "Mechanical Gaming Keyboard",
              "vendor_name": "KeyCraft Wholesale",
              "internal_price": "80.00",
              "vendor_price": "92.00",
              "currency": "USD",
              "price_difference": 12.0,
              "percentage_difference": 15.0,
              "is_exception": true,
              "validation_status": "EXCEPTION_EXCEEDS_10_PERCENT"
            },
            {
              "sku": "SKU-003",
              "product_name": "USB-C Multiport Hub",
              "vendor_name": "ConnectPro Direct",
              "internal_price": "40.00",
              "vendor_price": "44.00",
              "currency": "USD",
              "price_difference": 4.0,
              "percentage_difference": 10.0,
              "is_exception": false,
              "validation_status": "COMPLIANT"
            },
            {
              "sku": "SKU-004",
              "product_name": "27-inch 4K Monitor",
              "vendor_name": "VisionTech Displays",
              "internal_price": "300.00",
              "vendor_price": "255.00",
              "currency": "USD",
              "price_difference": -45.0,
              "percentage_difference": 15.0,
              "is_exception": true,
              "validation_status": "EXCEPTION_EXCEEDS_10_PERCENT"
            },
            {
              "sku": "SKU-005",
              "product_name": "Noise-Canceling Headphones",
              "vendor_name": "AudioWave Systems",
              "internal_price": "150.00",
              "vendor_price": "145.00",
              "currency": "USD",
              "price_difference": -5.0,
              "percentage_difference": 3.33,
              "is_exception": false,
              "validation_status": "COMPLIANT"
            },
            {
              "sku": "SKU-006",
              "product_name": "Braided HDMI Cable 2m",
              "vendor_name": "CableLine Global",
              "internal_price": "10.00",
              "vendor_price": "12.50",
              "currency": "USD",
              "price_difference": 2.5,
              "percentage_difference": 25.0,
              "is_exception": true,
              "validation_status": "EXCEPTION_EXCEEDS_10_PERCENT"
            },
            {
              "sku": "SKU-007",
              "product_name": "Aluminum Laptop Stand",
              "vendor_name": "ErgoDesk Co",
              "internal_price": "35.00",
              "vendor_price": "38.50",
              "currency": "USD",
              "price_difference": 3.5,
              "percentage_difference": 10.0,
              "is_exception": false,
              "validation_status": "COMPLIANT"
            }
          ],
          "exceptions": [
            {
              "sku": "SKU-002",
              "product_name": "Mechanical Gaming Keyboard",
              "vendor_name": "KeyCraft Wholesale",
              "internal_price": "80.00",
              "vendor_price": "92.00",
              "currency": "USD",
              "price_difference": 12.0,
              "percentage_difference": 15.0,
              "is_exception": true,
              "validation_status": "EXCEPTION_EXCEEDS_10_PERCENT"
            },
            {
              "sku": "SKU-004",
              "product_name": "27-inch 4K Monitor",
              "vendor_name": "VisionTech Displays",
              "internal_price": "300.00",
              "vendor_price": "255.00",
              "currency": "USD",
              "price_difference": -45.0,
              "percentage_difference": 15.0,
              "is_exception": true,
              "validation_status": "EXCEPTION_EXCEEDS_10_PERCENT"
            },
            {
              "sku": "SKU-006",
              "product_name": "Braided HDMI Cable 2m",
              "vendor_name": "CableLine Global",
              "internal_price": "10.00",
              "vendor_price": "12.50",
              "currency": "USD",
              "price_difference": 2.5,
              "percentage_difference": 25.0,
              "is_exception": true,
              "validation_status": "EXCEPTION_EXCEEDS_10_PERCENT"
            }
          ],
          "exception_count": 3,
          "total_matched": 7,
          "unmatched_vendor_records": [
            {
              "sku": "SKU-099",
              "vendor_name": "NewVendor Imports",
              "vendor_price": "19.99",
              "reason": "SKU not found in internal product catalog"
            }
          ],
          "unmatched_internal_records": [
            {
              "sku": "SKU-008",
              "product_name": "1080p HD Pro Webcam",
              "internal_price": "50.00",
              "reason": "SKU not found in vendor price list"
            }
          ],
          "summary": "Validated 7 products: 3 exception(s) exceeding 10.0% threshold."
        },
        "error": null
      }
    ],
    "final_output": {
      "matched_products": [
        {
          "sku": "SKU-001",
          "product_name": "Wireless Ergonomic Mouse",
          "vendor_name": "Alpha Suppliers",
          "internal_price": "25.00",
          "vendor_price": "26.00",
          "currency": "USD",
          "price_difference": 1.0,
          "percentage_difference": 4.0,
          "is_exception": false,
          "validation_status": "COMPLIANT"
        },
        {
          "sku": "SKU-002",
          "product_name": "Mechanical Gaming Keyboard",
          "vendor_name": "KeyCraft Wholesale",
          "internal_price": "80.00",
          "vendor_price": "92.00",
          "currency": "USD",
          "price_difference": 12.0,
          "percentage_difference": 15.0,
          "is_exception": true,
          "validation_status": "EXCEPTION_EXCEEDS_10_PERCENT"
        },
        {
          "sku": "SKU-003",
          "product_name": "USB-C Multiport Hub",
          "vendor_name": "ConnectPro Direct",
          "internal_price": "40.00",
          "vendor_price": "44.00",
          "currency": "USD",
          "price_difference": 4.0,
          "percentage_difference": 10.0,
          "is_exception": false,
          "validation_status": "COMPLIANT"
        },
        {
          "sku": "SKU-004",
          "product_name": "27-inch 4K Monitor",
          "vendor_name": "VisionTech Displays",
          "internal_price": "300.00",
          "vendor_price": "255.00",
          "currency": "USD",
          "price_difference": -45.0,
          "percentage_difference": 15.0,
          "is_exception": true,
          "validation_status": "EXCEPTION_EXCEEDS_10_PERCENT"
        },
        {
          "sku": "SKU-005",
          "product_name": "Noise-Canceling Headphones",
          "vendor_name": "AudioWave Systems",
          "internal_price": "150.00",
          "vendor_price": "145.00",
          "currency": "USD",
          "price_difference": -5.0,
          "percentage_difference": 3.33,
          "is_exception": false,
          "validation_status": "COMPLIANT"
        },
        {
          "sku": "SKU-006",
          "product_name": "Braided HDMI Cable 2m",
          "vendor_name": "CableLine Global",
          "internal_price": "10.00",
          "vendor_price": "12.50",
          "currency": "USD",
          "price_difference": 2.5,
          "percentage_difference": 25.0,
          "is_exception": true,
          "validation_status": "EXCEPTION_EXCEEDS_10_PERCENT"
        },
        {
          "sku": "SKU-007",
          "product_name": "Aluminum Laptop Stand",
          "vendor_name": "ErgoDesk Co",
          "internal_price": "35.00",
          "vendor_price": "38.50",
          "currency": "USD",
          "price_difference": 3.5,
          "percentage_difference": 10.0,
          "is_exception": false,
          "validation_status": "COMPLIANT"
        }
      ],
      "exceptions": [
        {
          "sku": "SKU-002",
          "product_name": "Mechanical Gaming Keyboard",
          "vendor_name": "KeyCraft Wholesale",
          "internal_price": "80.00",
          "vendor_price": "92.00",
          "currency": "USD",
          "price_difference": 12.0,
          "percentage_difference": 15.0,
          "is_exception": true,
          "validation_status": "EXCEPTION_EXCEEDS_10_PERCENT"
        },
        {
          "sku": "SKU-004",
          "product_name": "27-inch 4K Monitor",
          "vendor_name": "VisionTech Displays",
          "internal_price": "300.00",
          "vendor_price": "255.00",
          "currency": "USD",
          "price_difference": -45.0,
          "percentage_difference": 15.0,
          "is_exception": true,
          "validation_status": "EXCEPTION_EXCEEDS_10_PERCENT"
        },
        {
          "sku": "SKU-006",
          "product_name": "Braided HDMI Cable 2m",
          "vendor_name": "CableLine Global",
          "internal_price": "10.00",
          "vendor_price": "12.50",
          "currency": "USD",
          "price_difference": 2.5,
          "percentage_difference": 25.0,
          "is_exception": true,
          "validation_status": "EXCEPTION_EXCEEDS_10_PERCENT"
        }
      ],
      "exception_count": 3,
      "total_matched": 7,
      "unmatched_vendor_records": [
        {
          "sku": "SKU-099",
          "vendor_name": "NewVendor Imports",
          "vendor_price": "19.99",
          "reason": "SKU not found in internal product catalog"
        }
      ],
      "unmatched_internal_records": [
        {
          "sku": "SKU-008",
          "product_name": "1080p HD Pro Webcam",
          "internal_price": "50.00",
          "reason": "SKU not found in vendor price list"
        }
      ],
      "summary": "Validated 7 products: 3 exception(s) exceeding 10.0% threshold."
    },
    "errors": [],
    "clarification_required": false,
    "routing_mode": "offline",
    "warnings": []
  },
  "wf003_paraphrase": {
    "request": "Clean the supplier CSV file, detect columns, and filter out invalid rows.",
    "selected_workflow_id": "WF003",
    "selected_workflow_name": "Vendor File Processing",
    "routing_confidence": 0.99,
    "routing_reasoning": "Offline keyword match against trigger/metadata for WF003 (Vendor File Processing): matched terms [clean, column, csv, detect, file, invalid, row, vendor].",
    "status": "success",
    "steps": [
      {
        "step_number": 1,
        "step_name": "Read file",
        "status": "completed",
        "output_summary": "Read 8 raw record(s) from 'sample_vendor_catalog.csv'.",
        "output": {
          "raw_headers": [
            "Item_SKU",
            "Item_Title",
            "Category",
            "Unit_Price",
            "Quantity_Available"
          ],
          "raw_rows": [
            {
              "Item_SKU": "VND-101",
              "Item_Title": "Wireless Keyboard",
              "Category": "Electronics",
              "Unit_Price": "45.99",
              "Quantity_Available": "150"
            },
            {
              "Item_SKU": "",
              "Item_Title": "Ergonomic Mouse",
              "Category": "Electronics",
              "Unit_Price": "24.50",
              "Quantity_Available": "80"
            },
            {
              "Item_SKU": "VND-103",
              "Item_Title": "",
              "Category": "Office Supplies",
              "Unit_Price": "12.00",
              "Quantity_Available": "200"
            },
            {
              "Item_SKU": "VND-104",
              "Item_Title": "Monitor Riser Stand",
              "Category": "Office Furniture",
              "Unit_Price": "34.00",
              "Quantity_Available": "45"
            },
            {
              "Item_SKU": "",
              "Item_Title": "",
              "Category": "Accessories",
              "Unit_Price": "15.00",
              "Quantity_Available": "10"
            },
            {
              "Item_SKU": "VND-106",
              "Item_Title": "USB-C Charging Hub",
              "Category": "Electronics",
              "Unit_Price": "39.95",
              "Quantity_Available": "120"
            },
            {
              "Item_SKU": "VND-107",
              "Item_Title": "Desk Mat Extended",
              "Category": "Accessories",
              "Unit_Price": "-5.00",
              "Quantity_Available": "50"
            },
            {
              "Item_SKU": "VND-108",
              "Item_Title": "Noise Canceling Earbuds",
              "Category": "Audio",
              "Unit_Price": "89.00",
              "Quantity_Available": "35"
            }
          ],
          "file_path": "data/sample_vendor_catalog.csv",
          "total_rows_read": 8,
          "summary": "Read 8 raw record(s) from 'sample_vendor_catalog.csv'."
        },
        "error": null
      },
      {
        "step_number": 2,
        "step_name": "detect columns",
        "status": "completed",
        "output_summary": "Detected 5 column(s): Item_SKU, Item_Title, Category, Unit_Price, Quantity_Available.",
        "output": {
          "raw_headers": [
            "Item_SKU",
            "Item_Title",
            "Category",
            "Unit_Price",
            "Quantity_Available"
          ],
          "detected_columns": [
            "sku",
            "product_name",
            "category",
            "price",
            "stock"
          ],
          "summary": "Detected 5 column(s): Item_SKU, Item_Title, Category, Unit_Price, Quantity_Available."
        },
        "error": null
      },
      {
        "step_number": 3,
        "step_name": "normalize column names",
        "status": "completed",
        "output_summary": "Normalized 5 column(s) across 8 row(s).",
        "output": {
          "normalized_rows": [
            {
              "sku": "VND-101",
              "product_name": "Wireless Keyboard",
              "category": "Electronics",
              "price": "45.99",
              "stock": "150"
            },
            {
              "sku": "",
              "product_name": "Ergonomic Mouse",
              "category": "Electronics",
              "price": "24.50",
              "stock": "80"
            },
            {
              "sku": "VND-103",
              "product_name": "",
              "category": "Office Supplies",
              "price": "12.00",
              "stock": "200"
            },
            {
              "sku": "VND-104",
              "product_name": "Monitor Riser Stand",
              "category": "Office Furniture",
              "price": "34.00",
              "stock": "45"
            },
            {
              "sku": "",
              "product_name": "",
              "category": "Accessories",
              "price": "15.00",
              "stock": "10"
            },
            {
              "sku": "VND-106",
              "product_name": "USB-C Charging Hub",
              "category": "Electronics",
              "price": "39.95",
              "stock": "120"
            },
            {
              "sku": "VND-107",
              "product_name": "Desk Mat Extended",
              "category": "Accessories",
              "price": "-5.00",
              "stock": "50"
            },
            {
              "sku": "VND-108",
              "product_name": "Noise Canceling Earbuds",
              "category": "Audio",
              "price": "89.00",
              "stock": "35"
            }
          ],
          "column_mapping": {
            "Item_SKU": "sku",
            "Item_Title": "product_name",
            "Category": "category",
            "Unit_Price": "price",
            "Quantity_Available": "stock"
          },
          "normalized_headers": [
            "category",
            "price",
            "product_name",
            "sku",
            "stock"
          ],
          "summary": "Normalized 5 column(s) across 8 row(s)."
        },
        "error": null
      },
      {
        "step_number": 4,
        "step_name": "validate required fields",
        "status": "completed",
        "output_summary": "Validated required fields: 4 passed, 4 failed.",
        "output": {
          "preliminary_valid": [
            {
              "sku": "VND-101",
              "product_name": "Wireless Keyboard",
              "price": 45.99,
              "category": "Electronics",
              "stock": 150,
              "extra_fields": {}
            },
            {
              "sku": "VND-104",
              "product_name": "Monitor Riser Stand",
              "price": 34.0,
              "category": "Office Furniture",
              "stock": 45,
              "extra_fields": {}
            },
            {
              "sku": "VND-106",
              "product_name": "USB-C Charging Hub",
              "price": 39.95,
              "category": "Electronics",
              "stock": 120,
              "extra_fields": {}
            },
            {
              "sku": "VND-108",
              "product_name": "Noise Canceling Earbuds",
              "price": 89.0,
              "category": "Audio",
              "stock": 35,
              "extra_fields": {}
            }
          ],
          "preliminary_invalid": [
            {
              "row_number": 2,
              "raw_data": {
                "sku": "",
                "product_name": "Ergonomic Mouse",
                "category": "Electronics",
                "price": "24.50",
                "stock": "80"
              },
              "errors": [
                "Missing required field: SKU is blank or missing."
              ]
            },
            {
              "row_number": 3,
              "raw_data": {
                "sku": "VND-103",
                "product_name": "",
                "category": "Office Supplies",
                "price": "12.00",
                "stock": "200"
              },
              "errors": [
                "Missing required field: product_name is blank or missing."
              ]
            },
            {
              "row_number": 5,
              "raw_data": {
                "sku": "",
                "product_name": "",
                "category": "Accessories",
                "price": "15.00",
                "stock": "10"
              },
              "errors": [
                "Missing required field: SKU is blank or missing.",
                "Missing required field: product_name is blank or missing."
              ]
            },
            {
              "row_number": 7,
              "raw_data": {
                "sku": "VND-107",
                "product_name": "Desk Mat Extended",
                "category": "Accessories",
                "price": "-5.00",
                "stock": "50"
              },
              "errors": [
                "Invalid price '-5.00': price must be non-negative."
              ]
            }
          ],
          "valid_count": 4,
          "invalid_count": 4,
          "summary": "Validated required fields: 4 passed, 4 failed."
        },
        "error": null
      },
      {
        "step_number": 5,
        "step_name": "identify invalid rows",
        "status": "completed",
        "output_summary": "Identified 4 invalid row(s) requiring remediation.",
        "output": {
          "valid_rows": [
            {
              "sku": "VND-101",
              "product_name": "Wireless Keyboard",
              "price": 45.99,
              "category": "Electronics",
              "stock": 150,
              "extra_fields": {}
            },
            {
              "sku": "VND-104",
              "product_name": "Monitor Riser Stand",
              "price": 34.0,
              "category": "Office Furniture",
              "stock": 45,
              "extra_fields": {}
            },
            {
              "sku": "VND-106",
              "product_name": "USB-C Charging Hub",
              "price": 39.95,
              "category": "Electronics",
              "stock": 120,
              "extra_fields": {}
            },
            {
              "sku": "VND-108",
              "product_name": "Noise Canceling Earbuds",
              "price": 89.0,
              "category": "Audio",
              "stock": 35,
              "extra_fields": {}
            }
          ],
          "invalid_rows": [
            {
              "row_number": 2,
              "raw_data": {
                "sku": "",
                "product_name": "Ergonomic Mouse",
                "category": "Electronics",
                "price": "24.50",
                "stock": "80"
              },
              "errors": [
                "Missing required field: SKU is blank or missing."
              ]
            },
            {
              "row_number": 3,
              "raw_data": {
                "sku": "VND-103",
                "product_name": "",
                "category": "Office Supplies",
                "price": "12.00",
                "stock": "200"
              },
              "errors": [
                "Missing required field: product_name is blank or missing."
              ]
            },
            {
              "row_number": 5,
              "raw_data": {
                "sku": "",
                "product_name": "",
                "category": "Accessories",
                "price": "15.00",
                "stock": "10"
              },
              "errors": [
                "Missing required field: SKU is blank or missing.",
                "Missing required field: product_name is blank or missing."
              ]
            },
            {
              "row_number": 7,
              "raw_data": {
                "sku": "VND-107",
                "product_name": "Desk Mat Extended",
                "category": "Accessories",
                "price": "-5.00",
                "stock": "50"
              },
              "errors": [
                "Invalid price '-5.00': price must be non-negative."
              ]
            }
          ],
          "valid_count": 4,
          "invalid_count": 4,
          "summary": "Identified 4 invalid row(s) requiring remediation."
        },
        "error": null
      },
      {
        "step_number": 6,
        "step_name": "produce cleaned dataset",
        "status": "completed",
        "output_summary": "Processed vendor file: 4 valid record(s) cleaned, 4 invalid row(s) flagged. Wrote /Users/harshkumar/Desktop/ai-workflow-agent/outputs/cleaned_sample_vendor_catalog.csv, /Users/harshkumar/Desktop/ai-workflow-agent/outputs/invalid_rows_sample_vendor_catalog.csv and /Users/harshkumar/Desktop/ai-workflow-agent/outputs/validation_summary_sample_vendor_catalog.json.",
        "output": {
          "cleaned_records": [
            {
              "sku": "VND-101",
              "product_name": "Wireless Keyboard",
              "price": 45.99,
              "category": "Electronics",
              "stock": 150,
              "extra_fields": {}
            },
            {
              "sku": "VND-104",
              "product_name": "Monitor Riser Stand",
              "price": 34.0,
              "category": "Office Furniture",
              "stock": 45,
              "extra_fields": {}
            },
            {
              "sku": "VND-106",
              "product_name": "USB-C Charging Hub",
              "price": 39.95,
              "category": "Electronics",
              "stock": 120,
              "extra_fields": {}
            },
            {
              "sku": "VND-108",
              "product_name": "Noise Canceling Earbuds",
              "price": 89.0,
              "category": "Audio",
              "stock": 35,
              "extra_fields": {}
            }
          ],
          "invalid_records": [
            {
              "row_number": 2,
              "raw_data": {
                "sku": "",
                "product_name": "Ergonomic Mouse",
                "category": "Electronics",
                "price": "24.50",
                "stock": "80"
              },
              "errors": [
                "Missing required field: SKU is blank or missing."
              ]
            },
            {
              "row_number": 3,
              "raw_data": {
                "sku": "VND-103",
                "product_name": "",
                "category": "Office Supplies",
                "price": "12.00",
                "stock": "200"
              },
              "errors": [
                "Missing required field: product_name is blank or missing."
              ]
            },
            {
              "row_number": 5,
              "raw_data": {
                "sku": "",
                "product_name": "",
                "category": "Accessories",
                "price": "15.00",
                "stock": "10"
              },
              "errors": [
                "Missing required field: SKU is blank or missing.",
                "Missing required field: product_name is blank or missing."
              ]
            },
            {
              "row_number": 7,
              "raw_data": {
                "sku": "VND-107",
                "product_name": "Desk Mat Extended",
                "category": "Accessories",
                "price": "-5.00",
                "stock": "50"
              },
              "errors": [
                "Invalid price '-5.00': price must be non-negative."
              ]
            }
          ],
          "total_processed": 8,
          "valid_count": 4,
          "invalid_count": 4,
          "output_files": {
            "cleaned_csv": "/Users/harshkumar/Desktop/ai-workflow-agent/outputs/cleaned_sample_vendor_catalog.csv",
            "invalid_rows_csv": "/Users/harshkumar/Desktop/ai-workflow-agent/outputs/invalid_rows_sample_vendor_catalog.csv",
            "validation_summary_json": "/Users/harshkumar/Desktop/ai-workflow-agent/outputs/validation_summary_sample_vendor_catalog.json"
          },
          "summary": "Processed vendor file: 4 valid record(s) cleaned, 4 invalid row(s) flagged. Wrote /Users/harshkumar/Desktop/ai-workflow-agent/outputs/cleaned_sample_vendor_catalog.csv, /Users/harshkumar/Desktop/ai-workflow-agent/outputs/invalid_rows_sample_vendor_catalog.csv and /Users/harshkumar/Desktop/ai-workflow-agent/outputs/validation_summary_sample_vendor_catalog.json."
        },
        "error": null
      }
    ],
    "final_output": {
      "cleaned_records": [
        {
          "sku": "VND-101",
          "product_name": "Wireless Keyboard",
          "price": 45.99,
          "category": "Electronics",
          "stock": 150,
          "extra_fields": {}
        },
        {
          "sku": "VND-104",
          "product_name": "Monitor Riser Stand",
          "price": 34.0,
          "category": "Office Furniture",
          "stock": 45,
          "extra_fields": {}
        },
        {
          "sku": "VND-106",
          "product_name": "USB-C Charging Hub",
          "price": 39.95,
          "category": "Electronics",
          "stock": 120,
          "extra_fields": {}
        },
        {
          "sku": "VND-108",
          "product_name": "Noise Canceling Earbuds",
          "price": 89.0,
          "category": "Audio",
          "stock": 35,
          "extra_fields": {}
        }
      ],
      "invalid_records": [
        {
          "row_number": 2,
          "raw_data": {
            "sku": "",
            "product_name": "Ergonomic Mouse",
            "category": "Electronics",
            "price": "24.50",
            "stock": "80"
          },
          "errors": [
            "Missing required field: SKU is blank or missing."
          ]
        },
        {
          "row_number": 3,
          "raw_data": {
            "sku": "VND-103",
            "product_name": "",
            "category": "Office Supplies",
            "price": "12.00",
            "stock": "200"
          },
          "errors": [
            "Missing required field: product_name is blank or missing."
          ]
        },
        {
          "row_number": 5,
          "raw_data": {
            "sku": "",
            "product_name": "",
            "category": "Accessories",
            "price": "15.00",
            "stock": "10"
          },
          "errors": [
            "Missing required field: SKU is blank or missing.",
            "Missing required field: product_name is blank or missing."
          ]
        },
        {
          "row_number": 7,
          "raw_data": {
            "sku": "VND-107",
            "product_name": "Desk Mat Extended",
            "category": "Accessories",
            "price": "-5.00",
            "stock": "50"
          },
          "errors": [
            "Invalid price '-5.00': price must be non-negative."
          ]
        }
      ],
      "total_processed": 8,
      "valid_count": 4,
      "invalid_count": 4,
      "output_files": {
        "cleaned_csv": "/Users/harshkumar/Desktop/ai-workflow-agent/outputs/cleaned_sample_vendor_catalog.csv",
        "invalid_rows_csv": "/Users/harshkumar/Desktop/ai-workflow-agent/outputs/invalid_rows_sample_vendor_catalog.csv",
        "validation_summary_json": "/Users/harshkumar/Desktop/ai-workflow-agent/outputs/validation_summary_sample_vendor_catalog.json"
      },
      "summary": "Processed vendor file: 4 valid record(s) cleaned, 4 invalid row(s) flagged. Wrote /Users/harshkumar/Desktop/ai-workflow-agent/outputs/cleaned_sample_vendor_catalog.csv, /Users/harshkumar/Desktop/ai-workflow-agent/outputs/invalid_rows_sample_vendor_catalog.csv and /Users/harshkumar/Desktop/ai-workflow-agent/outputs/validation_summary_sample_vendor_catalog.json."
    },
    "errors": [],
    "clarification_required": false,
    "routing_mode": "offline",
    "warnings": []
  },
  "wf003_vendor_processing": {
    "request": "Process this vendor spreadsheet and show invalid rows.",
    "selected_workflow_id": "WF003",
    "selected_workflow_name": "Vendor File Processing",
    "routing_confidence": 0.9,
    "routing_reasoning": "Offline keyword match against trigger/metadata for WF003 (Vendor File Processing): matched terms [csv, invalid, process, row, vendor].",
    "status": "success",
    "steps": [
      {
        "step_number": 1,
        "step_name": "Read file",
        "status": "completed",
        "output_summary": "Read 8 raw record(s) from 'sample_vendor_catalog.csv'.",
        "output": {
          "raw_headers": [
            "Item_SKU",
            "Item_Title",
            "Category",
            "Unit_Price",
            "Quantity_Available"
          ],
          "raw_rows": [
            {
              "Item_SKU": "VND-101",
              "Item_Title": "Wireless Keyboard",
              "Category": "Electronics",
              "Unit_Price": "45.99",
              "Quantity_Available": "150"
            },
            {
              "Item_SKU": "",
              "Item_Title": "Ergonomic Mouse",
              "Category": "Electronics",
              "Unit_Price": "24.50",
              "Quantity_Available": "80"
            },
            {
              "Item_SKU": "VND-103",
              "Item_Title": "",
              "Category": "Office Supplies",
              "Unit_Price": "12.00",
              "Quantity_Available": "200"
            },
            {
              "Item_SKU": "VND-104",
              "Item_Title": "Monitor Riser Stand",
              "Category": "Office Furniture",
              "Unit_Price": "34.00",
              "Quantity_Available": "45"
            },
            {
              "Item_SKU": "",
              "Item_Title": "",
              "Category": "Accessories",
              "Unit_Price": "15.00",
              "Quantity_Available": "10"
            },
            {
              "Item_SKU": "VND-106",
              "Item_Title": "USB-C Charging Hub",
              "Category": "Electronics",
              "Unit_Price": "39.95",
              "Quantity_Available": "120"
            },
            {
              "Item_SKU": "VND-107",
              "Item_Title": "Desk Mat Extended",
              "Category": "Accessories",
              "Unit_Price": "-5.00",
              "Quantity_Available": "50"
            },
            {
              "Item_SKU": "VND-108",
              "Item_Title": "Noise Canceling Earbuds",
              "Category": "Audio",
              "Unit_Price": "89.00",
              "Quantity_Available": "35"
            }
          ],
          "file_path": "data/sample_vendor_catalog.csv",
          "total_rows_read": 8,
          "summary": "Read 8 raw record(s) from 'sample_vendor_catalog.csv'."
        },
        "error": null
      },
      {
        "step_number": 2,
        "step_name": "detect columns",
        "status": "completed",
        "output_summary": "Detected 5 column(s): Item_SKU, Item_Title, Category, Unit_Price, Quantity_Available.",
        "output": {
          "raw_headers": [
            "Item_SKU",
            "Item_Title",
            "Category",
            "Unit_Price",
            "Quantity_Available"
          ],
          "detected_columns": [
            "sku",
            "product_name",
            "category",
            "price",
            "stock"
          ],
          "summary": "Detected 5 column(s): Item_SKU, Item_Title, Category, Unit_Price, Quantity_Available."
        },
        "error": null
      },
      {
        "step_number": 3,
        "step_name": "normalize column names",
        "status": "completed",
        "output_summary": "Normalized 5 column(s) across 8 row(s).",
        "output": {
          "normalized_rows": [
            {
              "sku": "VND-101",
              "product_name": "Wireless Keyboard",
              "category": "Electronics",
              "price": "45.99",
              "stock": "150"
            },
            {
              "sku": "",
              "product_name": "Ergonomic Mouse",
              "category": "Electronics",
              "price": "24.50",
              "stock": "80"
            },
            {
              "sku": "VND-103",
              "product_name": "",
              "category": "Office Supplies",
              "price": "12.00",
              "stock": "200"
            },
            {
              "sku": "VND-104",
              "product_name": "Monitor Riser Stand",
              "category": "Office Furniture",
              "price": "34.00",
              "stock": "45"
            },
            {
              "sku": "",
              "product_name": "",
              "category": "Accessories",
              "price": "15.00",
              "stock": "10"
            },
            {
              "sku": "VND-106",
              "product_name": "USB-C Charging Hub",
              "category": "Electronics",
              "price": "39.95",
              "stock": "120"
            },
            {
              "sku": "VND-107",
              "product_name": "Desk Mat Extended",
              "category": "Accessories",
              "price": "-5.00",
              "stock": "50"
            },
            {
              "sku": "VND-108",
              "product_name": "Noise Canceling Earbuds",
              "category": "Audio",
              "price": "89.00",
              "stock": "35"
            }
          ],
          "column_mapping": {
            "Item_SKU": "sku",
            "Item_Title": "product_name",
            "Category": "category",
            "Unit_Price": "price",
            "Quantity_Available": "stock"
          },
          "normalized_headers": [
            "category",
            "price",
            "product_name",
            "sku",
            "stock"
          ],
          "summary": "Normalized 5 column(s) across 8 row(s)."
        },
        "error": null
      },
      {
        "step_number": 4,
        "step_name": "validate required fields",
        "status": "completed",
        "output_summary": "Validated required fields: 4 passed, 4 failed.",
        "output": {
          "preliminary_valid": [
            {
              "sku": "VND-101",
              "product_name": "Wireless Keyboard",
              "price": 45.99,
              "category": "Electronics",
              "stock": 150,
              "extra_fields": {}
            },
            {
              "sku": "VND-104",
              "product_name": "Monitor Riser Stand",
              "price": 34.0,
              "category": "Office Furniture",
              "stock": 45,
              "extra_fields": {}
            },
            {
              "sku": "VND-106",
              "product_name": "USB-C Charging Hub",
              "price": 39.95,
              "category": "Electronics",
              "stock": 120,
              "extra_fields": {}
            },
            {
              "sku": "VND-108",
              "product_name": "Noise Canceling Earbuds",
              "price": 89.0,
              "category": "Audio",
              "stock": 35,
              "extra_fields": {}
            }
          ],
          "preliminary_invalid": [
            {
              "row_number": 2,
              "raw_data": {
                "sku": "",
                "product_name": "Ergonomic Mouse",
                "category": "Electronics",
                "price": "24.50",
                "stock": "80"
              },
              "errors": [
                "Missing required field: SKU is blank or missing."
              ]
            },
            {
              "row_number": 3,
              "raw_data": {
                "sku": "VND-103",
                "product_name": "",
                "category": "Office Supplies",
                "price": "12.00",
                "stock": "200"
              },
              "errors": [
                "Missing required field: product_name is blank or missing."
              ]
            },
            {
              "row_number": 5,
              "raw_data": {
                "sku": "",
                "product_name": "",
                "category": "Accessories",
                "price": "15.00",
                "stock": "10"
              },
              "errors": [
                "Missing required field: SKU is blank or missing.",
                "Missing required field: product_name is blank or missing."
              ]
            },
            {
              "row_number": 7,
              "raw_data": {
                "sku": "VND-107",
                "product_name": "Desk Mat Extended",
                "category": "Accessories",
                "price": "-5.00",
                "stock": "50"
              },
              "errors": [
                "Invalid price '-5.00': price must be non-negative."
              ]
            }
          ],
          "valid_count": 4,
          "invalid_count": 4,
          "summary": "Validated required fields: 4 passed, 4 failed."
        },
        "error": null
      },
      {
        "step_number": 5,
        "step_name": "identify invalid rows",
        "status": "completed",
        "output_summary": "Identified 4 invalid row(s) requiring remediation.",
        "output": {
          "valid_rows": [
            {
              "sku": "VND-101",
              "product_name": "Wireless Keyboard",
              "price": 45.99,
              "category": "Electronics",
              "stock": 150,
              "extra_fields": {}
            },
            {
              "sku": "VND-104",
              "product_name": "Monitor Riser Stand",
              "price": 34.0,
              "category": "Office Furniture",
              "stock": 45,
              "extra_fields": {}
            },
            {
              "sku": "VND-106",
              "product_name": "USB-C Charging Hub",
              "price": 39.95,
              "category": "Electronics",
              "stock": 120,
              "extra_fields": {}
            },
            {
              "sku": "VND-108",
              "product_name": "Noise Canceling Earbuds",
              "price": 89.0,
              "category": "Audio",
              "stock": 35,
              "extra_fields": {}
            }
          ],
          "invalid_rows": [
            {
              "row_number": 2,
              "raw_data": {
                "sku": "",
                "product_name": "Ergonomic Mouse",
                "category": "Electronics",
                "price": "24.50",
                "stock": "80"
              },
              "errors": [
                "Missing required field: SKU is blank or missing."
              ]
            },
            {
              "row_number": 3,
              "raw_data": {
                "sku": "VND-103",
                "product_name": "",
                "category": "Office Supplies",
                "price": "12.00",
                "stock": "200"
              },
              "errors": [
                "Missing required field: product_name is blank or missing."
              ]
            },
            {
              "row_number": 5,
              "raw_data": {
                "sku": "",
                "product_name": "",
                "category": "Accessories",
                "price": "15.00",
                "stock": "10"
              },
              "errors": [
                "Missing required field: SKU is blank or missing.",
                "Missing required field: product_name is blank or missing."
              ]
            },
            {
              "row_number": 7,
              "raw_data": {
                "sku": "VND-107",
                "product_name": "Desk Mat Extended",
                "category": "Accessories",
                "price": "-5.00",
                "stock": "50"
              },
              "errors": [
                "Invalid price '-5.00': price must be non-negative."
              ]
            }
          ],
          "valid_count": 4,
          "invalid_count": 4,
          "summary": "Identified 4 invalid row(s) requiring remediation."
        },
        "error": null
      },
      {
        "step_number": 6,
        "step_name": "produce cleaned dataset",
        "status": "completed",
        "output_summary": "Processed vendor file: 4 valid record(s) cleaned, 4 invalid row(s) flagged. Wrote /Users/harshkumar/Desktop/ai-workflow-agent/outputs/cleaned_sample_vendor_catalog.csv, /Users/harshkumar/Desktop/ai-workflow-agent/outputs/invalid_rows_sample_vendor_catalog.csv and /Users/harshkumar/Desktop/ai-workflow-agent/outputs/validation_summary_sample_vendor_catalog.json.",
        "output": {
          "cleaned_records": [
            {
              "sku": "VND-101",
              "product_name": "Wireless Keyboard",
              "price": 45.99,
              "category": "Electronics",
              "stock": 150,
              "extra_fields": {}
            },
            {
              "sku": "VND-104",
              "product_name": "Monitor Riser Stand",
              "price": 34.0,
              "category": "Office Furniture",
              "stock": 45,
              "extra_fields": {}
            },
            {
              "sku": "VND-106",
              "product_name": "USB-C Charging Hub",
              "price": 39.95,
              "category": "Electronics",
              "stock": 120,
              "extra_fields": {}
            },
            {
              "sku": "VND-108",
              "product_name": "Noise Canceling Earbuds",
              "price": 89.0,
              "category": "Audio",
              "stock": 35,
              "extra_fields": {}
            }
          ],
          "invalid_records": [
            {
              "row_number": 2,
              "raw_data": {
                "sku": "",
                "product_name": "Ergonomic Mouse",
                "category": "Electronics",
                "price": "24.50",
                "stock": "80"
              },
              "errors": [
                "Missing required field: SKU is blank or missing."
              ]
            },
            {
              "row_number": 3,
              "raw_data": {
                "sku": "VND-103",
                "product_name": "",
                "category": "Office Supplies",
                "price": "12.00",
                "stock": "200"
              },
              "errors": [
                "Missing required field: product_name is blank or missing."
              ]
            },
            {
              "row_number": 5,
              "raw_data": {
                "sku": "",
                "product_name": "",
                "category": "Accessories",
                "price": "15.00",
                "stock": "10"
              },
              "errors": [
                "Missing required field: SKU is blank or missing.",
                "Missing required field: product_name is blank or missing."
              ]
            },
            {
              "row_number": 7,
              "raw_data": {
                "sku": "VND-107",
                "product_name": "Desk Mat Extended",
                "category": "Accessories",
                "price": "-5.00",
                "stock": "50"
              },
              "errors": [
                "Invalid price '-5.00': price must be non-negative."
              ]
            }
          ],
          "total_processed": 8,
          "valid_count": 4,
          "invalid_count": 4,
          "output_files": {
            "cleaned_csv": "/Users/harshkumar/Desktop/ai-workflow-agent/outputs/cleaned_sample_vendor_catalog.csv",
            "invalid_rows_csv": "/Users/harshkumar/Desktop/ai-workflow-agent/outputs/invalid_rows_sample_vendor_catalog.csv",
            "validation_summary_json": "/Users/harshkumar/Desktop/ai-workflow-agent/outputs/validation_summary_sample_vendor_catalog.json"
          },
          "summary": "Processed vendor file: 4 valid record(s) cleaned, 4 invalid row(s) flagged. Wrote /Users/harshkumar/Desktop/ai-workflow-agent/outputs/cleaned_sample_vendor_catalog.csv, /Users/harshkumar/Desktop/ai-workflow-agent/outputs/invalid_rows_sample_vendor_catalog.csv and /Users/harshkumar/Desktop/ai-workflow-agent/outputs/validation_summary_sample_vendor_catalog.json."
        },
        "error": null
      }
    ],
    "final_output": {
      "cleaned_records": [
        {
          "sku": "VND-101",
          "product_name": "Wireless Keyboard",
          "price": 45.99,
          "category": "Electronics",
          "stock": 150,
          "extra_fields": {}
        },
        {
          "sku": "VND-104",
          "product_name": "Monitor Riser Stand",
          "price": 34.0,
          "category": "Office Furniture",
          "stock": 45,
          "extra_fields": {}
        },
        {
          "sku": "VND-106",
          "product_name": "USB-C Charging Hub",
          "price": 39.95,
          "category": "Electronics",
          "stock": 120,
          "extra_fields": {}
        },
        {
          "sku": "VND-108",
          "product_name": "Noise Canceling Earbuds",
          "price": 89.0,
          "category": "Audio",
          "stock": 35,
          "extra_fields": {}
        }
      ],
      "invalid_records": [
        {
          "row_number": 2,
          "raw_data": {
            "sku": "",
            "product_name": "Ergonomic Mouse",
            "category": "Electronics",
            "price": "24.50",
            "stock": "80"
          },
          "errors": [
            "Missing required field: SKU is blank or missing."
          ]
        },
        {
          "row_number": 3,
          "raw_data": {
            "sku": "VND-103",
            "product_name": "",
            "category": "Office Supplies",
            "price": "12.00",
            "stock": "200"
          },
          "errors": [
            "Missing required field: product_name is blank or missing."
          ]
        },
        {
          "row_number": 5,
          "raw_data": {
            "sku": "",
            "product_name": "",
            "category": "Accessories",
            "price": "15.00",
            "stock": "10"
          },
          "errors": [
            "Missing required field: SKU is blank or missing.",
            "Missing required field: product_name is blank or missing."
          ]
        },
        {
          "row_number": 7,
          "raw_data": {
            "sku": "VND-107",
            "product_name": "Desk Mat Extended",
            "category": "Accessories",
            "price": "-5.00",
            "stock": "50"
          },
          "errors": [
            "Invalid price '-5.00': price must be non-negative."
          ]
        }
      ],
      "total_processed": 8,
      "valid_count": 4,
      "invalid_count": 4,
      "output_files": {
        "cleaned_csv": "/Users/harshkumar/Desktop/ai-workflow-agent/outputs/cleaned_sample_vendor_catalog.csv",
        "invalid_rows_csv": "/Users/harshkumar/Desktop/ai-workflow-agent/outputs/invalid_rows_sample_vendor_catalog.csv",
        "validation_summary_json": "/Users/harshkumar/Desktop/ai-workflow-agent/outputs/validation_summary_sample_vendor_catalog.json"
      },
      "summary": "Processed vendor file: 4 valid record(s) cleaned, 4 invalid row(s) flagged. Wrote /Users/harshkumar/Desktop/ai-workflow-agent/outputs/cleaned_sample_vendor_catalog.csv, /Users/harshkumar/Desktop/ai-workflow-agent/outputs/invalid_rows_sample_vendor_catalog.csv and /Users/harshkumar/Desktop/ai-workflow-agent/outputs/validation_summary_sample_vendor_catalog.json."
    },
    "errors": [],
    "clarification_required": false,
    "routing_mode": "offline",
    "warnings": []
  },
  "wf004_paraphrase": {
    "request": "Write product descriptions, bullet points, and SEO metadata for our latest product.",
    "selected_workflow_id": "WF004",
    "selected_workflow_name": "Product Description Generator",
    "routing_confidence": 0.8,
    "routing_reasoning": "Offline keyword match against trigger/metadata for WF004 (Product Description Generator): matched terms [description, product, seo].",
    "status": "needs_clarification",
    "steps": [
      {
        "step_number": 1,
        "step_name": "Validate required attributes",
        "status": "needs_clarification",
        "output_summary": null,
        "output": null,
        "error": "Required attribute 'product_name' is missing or empty. A valid product name is required to generate descriptions."
      }
    ],
    "final_output": null,
    "errors": [
      "Required attribute 'product_name' is missing or empty. A valid product name is required to generate descriptions."
    ],
    "clarification_required": true,
    "routing_mode": "offline",
    "warnings": []
  },
  "wf004_product_description": {
    "request": "Generate SEO content for this product.",
    "selected_workflow_id": "WF004",
    "selected_workflow_name": "Product Description Generator",
    "routing_confidence": 0.85,
    "routing_reasoning": "Offline keyword match against trigger/metadata for WF004 (Product Description Generator): matched terms [content, generate, product, seo].",
    "status": "needs_clarification",
    "steps": [
      {
        "step_number": 1,
        "step_name": "Validate required attributes",
        "status": "needs_clarification",
        "output_summary": null,
        "output": null,
        "error": "Required attribute 'product_name' is missing or empty. A valid product name is required to generate descriptions."
      }
    ],
    "final_output": null,
    "errors": [
      "Required attribute 'product_name' is missing or empty. A valid product name is required to generate descriptions."
    ],
    "clarification_required": true,
    "routing_mode": "offline",
    "warnings": []
  },
  "wf005_order_status": {
    "request": "Where is order ORD-1001?",
    "selected_workflow_id": "WF005",
    "selected_workflow_name": "Customer Order Status",
    "routing_confidence": 0.7,
    "routing_reasoning": "Offline keyword match against trigger/metadata for WF005 (Customer Order Status): matched terms [order].",
    "status": "success",
    "steps": [
      {
        "step_number": 1,
        "step_name": "Validate identifier",
        "status": "completed",
        "output_summary": "Validated identifier 'ORD-1001' (type: order_id).",
        "output": {
          "identifier": "ORD-1001",
          "identifier_type": "order_id",
          "is_valid": true,
          "summary": "Validated identifier 'ORD-1001' (type: order_id)."
        },
        "error": null
      },
      {
        "step_number": 2,
        "step_name": "search order data",
        "status": "completed",
        "output_summary": "Found 1 order(s) for 'ORD-1001'.",
        "output": {
          "matching_orders": [
            {
              "order_id": "ORD-1001",
              "customer_email": "alice@example.com",
              "order_date": "2026-10-01",
              "status": "SHIPPED",
              "items": "Wireless Ergonomic Mouse (1); USB-C Hub (1)",
              "total_amount": 69.99,
              "currency": "USD"
            }
          ],
          "order_found": true,
          "identifier": "ORD-1001",
          "summary": "Found 1 order(s) for 'ORD-1001'."
        },
        "error": null
      },
      {
        "step_number": 3,
        "step_name": "retrieve order status",
        "status": "completed",
        "output_summary": "Retrieved status for 1 order(s).",
        "output": {
          "order_statuses": [
            {
              "order_id": "ORD-1001",
              "status": "SHIPPED",
              "order_date": "2026-10-01",
              "items": "Wireless Ergonomic Mouse (1); USB-C Hub (1)",
              "total_amount": 69.99,
              "currency": "USD"
            }
          ],
          "order_found": true,
          "summary": "Retrieved status for 1 order(s)."
        },
        "error": null
      },
      {
        "step_number": 4,
        "step_name": "retrieve shipment information",
        "status": "completed",
        "output_summary": "Retrieved 1 shipment record(s).",
        "output": {
          "shipment_details": [
            {
              "shipment_id": "SHP-5001",
              "order_id": "ORD-1001",
              "carrier": "FastShip Express",
              "tracking_number": "TRK-987654321",
              "estimated_delivery": "2026-10-15",
              "shipment_status": "IN_TRANSIT",
              "last_location": "Distribution Center - Chicago IL"
            }
          ],
          "has_shipment": true,
          "summary": "Retrieved 1 shipment record(s)."
        },
        "error": null
      },
      {
        "step_number": 5,
        "step_name": "summarize current status",
        "status": "completed",
        "output_summary": "Order ORD-1001 is currently SHIPPED (Shipment: IN_TRANSIT, Carrier: FastShip Express, Tracking: TRK-987654321). Items: Wireless Ergonomic Mouse (1); USB-C Hub (1).",
        "output": {
          "order_found": true,
          "order_id": "ORD-1001",
          "orders": [
            {
              "order_id": "ORD-1001",
              "order_status": "SHIPPED",
              "order_date": "2026-10-01",
              "items": "Wireless Ergonomic Mouse (1); USB-C Hub (1)",
              "total_amount": 69.99,
              "currency": "USD",
              "has_shipment": true,
              "carrier": "FastShip Express",
              "tracking_number": "TRK-987654321",
              "estimated_delivery": "2026-10-15",
              "shipment_status": "IN_TRANSIT",
              "last_location": "Distribution Center - Chicago IL"
            }
          ],
          "summary": "Order ORD-1001 is currently SHIPPED (Shipment: IN_TRANSIT, Carrier: FastShip Express, Tracking: TRK-987654321). Items: Wireless Ergonomic Mouse (1); USB-C Hub (1).",
          "request_another_identifier": false,
          "is_simulated": true
        },
        "error": null
      }
    ],
    "final_output": {
      "order_found": true,
      "order_id": "ORD-1001",
      "orders": [
        {
          "order_id": "ORD-1001",
          "order_status": "SHIPPED",
          "order_date": "2026-10-01",
          "items": "Wireless Ergonomic Mouse (1); USB-C Hub (1)",
          "total_amount": 69.99,
          "currency": "USD",
          "has_shipment": true,
          "carrier": "FastShip Express",
          "tracking_number": "TRK-987654321",
          "estimated_delivery": "2026-10-15",
          "shipment_status": "IN_TRANSIT",
          "last_location": "Distribution Center - Chicago IL"
        }
      ],
      "summary": "Order ORD-1001 is currently SHIPPED (Shipment: IN_TRANSIT, Carrier: FastShip Express, Tracking: TRK-987654321). Items: Wireless Ergonomic Mouse (1); USB-C Hub (1).",
      "request_another_identifier": false,
      "is_simulated": true
    },
    "errors": [],
    "clarification_required": false,
    "routing_mode": "offline",
    "warnings": []
  },
  "wf005_paraphrase": {
    "request": "Can you check tracking and shipping status for customer order ORD-1002?",
    "selected_workflow_id": "WF005",
    "selected_workflow_name": "Customer Order Status",
    "routing_confidence": 0.85,
    "routing_reasoning": "Offline keyword match against trigger/metadata for WF005 (Customer Order Status): matched terms [customer, order, shipment, statu].",
    "status": "success",
    "steps": [
      {
        "step_number": 1,
        "step_name": "Validate identifier",
        "status": "completed",
        "output_summary": "Validated identifier 'ORD-1002' (type: order_id).",
        "output": {
          "identifier": "ORD-1002",
          "identifier_type": "order_id",
          "is_valid": true,
          "summary": "Validated identifier 'ORD-1002' (type: order_id)."
        },
        "error": null
      },
      {
        "step_number": 2,
        "step_name": "search order data",
        "status": "completed",
        "output_summary": "Found 1 order(s) for 'ORD-1002'.",
        "output": {
          "matching_orders": [
            {
              "order_id": "ORD-1002",
              "customer_email": "bob@example.com",
              "order_date": "2026-10-05",
              "status": "DELIVERED",
              "items": "Mechanical Gaming Keyboard (1)",
              "total_amount": 79.5,
              "currency": "USD"
            }
          ],
          "order_found": true,
          "identifier": "ORD-1002",
          "summary": "Found 1 order(s) for 'ORD-1002'."
        },
        "error": null
      },
      {
        "step_number": 3,
        "step_name": "retrieve order status",
        "status": "completed",
        "output_summary": "Retrieved status for 1 order(s).",
        "output": {
          "order_statuses": [
            {
              "order_id": "ORD-1002",
              "status": "DELIVERED",
              "order_date": "2026-10-05",
              "items": "Mechanical Gaming Keyboard (1)",
              "total_amount": 79.5,
              "currency": "USD"
            }
          ],
          "order_found": true,
          "summary": "Retrieved status for 1 order(s)."
        },
        "error": null
      },
      {
        "step_number": 4,
        "step_name": "retrieve shipment information",
        "status": "completed",
        "output_summary": "Retrieved 1 shipment record(s).",
        "output": {
          "shipment_details": [
            {
              "shipment_id": "SHP-5002",
              "order_id": "ORD-1002",
              "carrier": "GlobalParcel",
              "tracking_number": "TRK-123456789",
              "estimated_delivery": "2026-10-07",
              "shipment_status": "DELIVERED",
              "last_location": "Front Porch - Seattle WA"
            }
          ],
          "has_shipment": true,
          "summary": "Retrieved 1 shipment record(s)."
        },
        "error": null
      },
      {
        "step_number": 5,
        "step_name": "summarize current status",
        "status": "completed",
        "output_summary": "Order ORD-1002 is currently DELIVERED (Shipment: DELIVERED, Carrier: GlobalParcel, Tracking: TRK-123456789). Items: Mechanical Gaming Keyboard (1).",
        "output": {
          "order_found": true,
          "order_id": "ORD-1002",
          "orders": [
            {
              "order_id": "ORD-1002",
              "order_status": "DELIVERED",
              "order_date": "2026-10-05",
              "items": "Mechanical Gaming Keyboard (1)",
              "total_amount": 79.5,
              "currency": "USD",
              "has_shipment": true,
              "carrier": "GlobalParcel",
              "tracking_number": "TRK-123456789",
              "estimated_delivery": "2026-10-07",
              "shipment_status": "DELIVERED",
              "last_location": "Front Porch - Seattle WA"
            }
          ],
          "summary": "Order ORD-1002 is currently DELIVERED (Shipment: DELIVERED, Carrier: GlobalParcel, Tracking: TRK-123456789). Items: Mechanical Gaming Keyboard (1).",
          "request_another_identifier": false,
          "is_simulated": true
        },
        "error": null
      }
    ],
    "final_output": {
      "order_found": true,
      "order_id": "ORD-1002",
      "orders": [
        {
          "order_id": "ORD-1002",
          "order_status": "DELIVERED",
          "order_date": "2026-10-05",
          "items": "Mechanical Gaming Keyboard (1)",
          "total_amount": 79.5,
          "currency": "USD",
          "has_shipment": true,
          "carrier": "GlobalParcel",
          "tracking_number": "TRK-123456789",
          "estimated_delivery": "2026-10-07",
          "shipment_status": "DELIVERED",
          "last_location": "Front Porch - Seattle WA"
        }
      ],
      "summary": "Order ORD-1002 is currently DELIVERED (Shipment: DELIVERED, Carrier: GlobalParcel, Tracking: TRK-123456789). Items: Mechanical Gaming Keyboard (1).",
      "request_another_identifier": false,
      "is_simulated": true
    },
    "errors": [],
    "clarification_required": false,
    "routing_mode": "offline",
    "warnings": []
  },
  "wf006_duplicate_detection": {
    "request": "Find likely duplicate products in the catalog.",
    "selected_workflow_id": "WF006",
    "selected_workflow_name": "Duplicate Product Detection",
    "routing_confidence": 0.85,
    "routing_reasoning": "Offline keyword match against trigger/metadata for WF006 (Duplicate Product Detection): matched terms [duplicate, find, likely, product].",
    "status": "success",
    "steps": [
      {
        "step_number": 1,
        "step_name": "Load products",
        "status": "completed",
        "output_summary": "Loaded 9 product(s) from 'sample_products_catalog.csv'.",
        "output": {
          "raw_products": [
            {
              "product_id": "PRD-01",
              "sku": "SKU-1001",
              "product_name": "Logitech MX Master 3S Wireless Mouse",
              "category": "Electronics",
              "brand": "Logitech",
              "price": 99.99
            },
            {
              "product_id": "PRD-02",
              "sku": "SKU-1001",
              "product_name": "Logitech MX Master 3S Mouse - Graphite",
              "category": "Electronics",
              "brand": "Logitech",
              "price": 99.99
            },
            {
              "product_id": "PRD-03",
              "sku": "SKU-2001",
              "product_name": "Keychron K2 Mechanical Keyboard RGB",
              "category": "Electronics",
              "brand": "Keychron",
              "price": 79.99
            },
            {
              "product_id": "PRD-04",
              "sku": "SKU-2002",
              "product_name": "Keychron K2 Wireless Mechanical Keyboard (RGB)",
              "category": "Electronics",
              "brand": "Keychron",
              "price": 79.99
            },
            {
              "product_id": "PRD-05",
              "sku": "SKU-3001",
              "product_name": "Sony WH-1000XM5 Noise Canceling Headphones",
              "category": "Audio",
              "brand": "Sony",
              "price": 399.99
            },
            {
              "product_id": "PRD-06",
              "sku": "SKU-3002",
              "product_name": "Sony WH 1000XM5 Headphones - Silver",
              "category": "Audio",
              "brand": "Sony",
              "price": 399.99
            },
            {
              "product_id": "PRD-07",
              "sku": "SKU-4001",
              "product_name": "Apple MacBook Pro 16-inch M3 Max",
              "category": "Computers",
              "brand": "Apple",
              "price": 3499.0
            },
            {
              "product_id": "PRD-08",
              "sku": "SKU-5001",
              "product_name": "Dell UltraSharp 27 4K USB-C Hub Monitor",
              "category": "Displays",
              "brand": "Dell",
              "price": 549.99
            },
            {
              "product_id": "PRD-09",
              "sku": "SKU-6001",
              "product_name": "Anker 737 Power Bank 24000mAh",
              "category": "Accessories",
              "brand": "Anker",
              "price": 149.99
            }
          ],
          "total_products_loaded": 9,
          "summary": "Loaded 9 product(s) from 'sample_products_catalog.csv'."
        },
        "error": null
      },
      {
        "step_number": 2,
        "step_name": "normalize names/SKUs",
        "status": "completed",
        "output_summary": "Normalized 9 catalog product records.",
        "output": {
          "normalized_products": [
            {
              "product_id": "PRD-01",
              "raw_sku": "SKU-1001",
              "normalized_sku": "SKU1001",
              "raw_name": "Logitech MX Master 3S Wireless Mouse",
              "normalized_name": "logitech mx master 3s wireless mouse",
              "tokens": [
                "3s",
                "logitech",
                "master",
                "mouse",
                "mx",
                "wireless"
              ],
              "category": "electronics",
              "brand": "logitech",
              "price": 99.99
            },
            {
              "product_id": "PRD-02",
              "raw_sku": "SKU-1001",
              "normalized_sku": "SKU1001",
              "raw_name": "Logitech MX Master 3S Mouse - Graphite",
              "normalized_name": "logitech mx master 3s mouse - graphite",
              "tokens": [
                "3s",
                "graphite",
                "logitech",
                "master",
                "mouse",
                "mx"
              ],
              "category": "electronics",
              "brand": "logitech",
              "price": 99.99
            },
            {
              "product_id": "PRD-03",
              "raw_sku": "SKU-2001",
              "normalized_sku": "SKU2001",
              "raw_name": "Keychron K2 Mechanical Keyboard RGB",
              "normalized_name": "keychron k2 mechanical keyboard rgb",
              "tokens": [
                "k2",
                "keyboard",
                "keychron",
                "mechanical",
                "rgb"
              ],
              "category": "electronics",
              "brand": "keychron",
              "price": 79.99
            },
            {
              "product_id": "PRD-04",
              "raw_sku": "SKU-2002",
              "normalized_sku": "SKU2002",
              "raw_name": "Keychron K2 Wireless Mechanical Keyboard (RGB)",
              "normalized_name": "keychron k2 wireless mechanical keyboard (rgb)",
              "tokens": [
                "k2",
                "keyboard",
                "keychron",
                "mechanical",
                "rgb",
                "wireless"
              ],
              "category": "electronics",
              "brand": "keychron",
              "price": 79.99
            },
            {
              "product_id": "PRD-05",
              "raw_sku": "SKU-3001",
              "normalized_sku": "SKU3001",
              "raw_name": "Sony WH-1000XM5 Noise Canceling Headphones",
              "normalized_name": "sony wh-1000xm5 noise canceling headphones",
              "tokens": [
                "1000xm5",
                "canceling",
                "headphones",
                "noise",
                "sony",
                "wh"
              ],
              "category": "audio",
              "brand": "sony",
              "price": 399.99
            },
            {
              "product_id": "PRD-06",
              "raw_sku": "SKU-3002",
              "normalized_sku": "SKU3002",
              "raw_name": "Sony WH 1000XM5 Headphones - Silver",
              "normalized_name": "sony wh 1000xm5 headphones - silver",
              "tokens": [
                "1000xm5",
                "headphones",
                "silver",
                "sony",
                "wh"
              ],
              "category": "audio",
              "brand": "sony",
              "price": 399.99
            },
            {
              "product_id": "PRD-07",
              "raw_sku": "SKU-4001",
              "normalized_sku": "SKU4001",
              "raw_name": "Apple MacBook Pro 16-inch M3 Max",
              "normalized_name": "apple macbook pro 16-inch m3 max",
              "tokens": [
                "16",
                "apple",
                "inch",
                "m3",
                "macbook",
                "max",
                "pro"
              ],
              "category": "computers",
              "brand": "apple",
              "price": 3499.0
            },
            {
              "product_id": "PRD-08",
              "raw_sku": "SKU-5001",
              "normalized_sku": "SKU5001",
              "raw_name": "Dell UltraSharp 27 4K USB-C Hub Monitor",
              "normalized_name": "dell ultrasharp 27 4k usb-c hub monitor",
              "tokens": [
                "27",
                "4k",
                "dell",
                "hub",
                "monitor",
                "ultrasharp",
                "usb"
              ],
              "category": "displays",
              "brand": "dell",
              "price": 549.99
            },
            {
              "product_id": "PRD-09",
              "raw_sku": "SKU-6001",
              "normalized_sku": "SKU6001",
              "raw_name": "Anker 737 Power Bank 24000mAh",
              "normalized_name": "anker 737 power bank 24000mah",
              "tokens": [
                "24000mah",
                "737",
                "anker",
                "bank",
                "power"
              ],
              "category": "accessories",
              "brand": "anker",
              "price": 149.99
            }
          ],
          "summary": "Normalized 9 catalog product records."
        },
        "error": null
      },
      {
        "step_number": 3,
        "step_name": "compare identifiers",
        "status": "completed",
        "output_summary": "Identified 1 exact duplicate SKU group(s).",
        "output": {
          "exact_sku_matches": [
            {
              "sku": "SKU1001",
              "duplicate_count": 2,
              "products": [
                "PRD-01",
                "PRD-02"
              ]
            }
          ],
          "exact_duplicate_sku_count": 1,
          "summary": "Identified 1 exact duplicate SKU group(s)."
        },
        "error": null
      },
      {
        "step_number": 4,
        "step_name": "compare product attributes",
        "status": "completed",
        "output_summary": "Found 3 duplicate candidate pair(s).",
        "output": {
          "duplicate_candidates": [
            {
              "primary_product_id": "PRD-01",
              "primary_sku": "SKU-1001",
              "primary_name": "Logitech MX Master 3S Wireless Mouse",
              "duplicate_product_id": "PRD-02",
              "duplicate_sku": "SKU-1001",
              "duplicate_name": "Logitech MX Master 3S Mouse - Graphite",
              "match_type": "exact_sku_match",
              "confidence": "definite",
              "similarity_score": 1.0,
              "matching_fields": [
                "sku"
              ],
              "explanation": "Definite duplicate: Identical SKU found across multiple records."
            },
            {
              "primary_product_id": "PRD-03",
              "primary_sku": "SKU-2001",
              "primary_name": "Keychron K2 Mechanical Keyboard RGB",
              "duplicate_product_id": "PRD-04",
              "duplicate_sku": "SKU-2002",
              "duplicate_name": "Keychron K2 Wireless Mechanical Keyboard (RGB)",
              "match_type": "high_attribute_similarity",
              "confidence": "likely",
              "similarity_score": 0.91,
              "matching_fields": [
                "product_name",
                "brand",
                "category"
              ],
              "explanation": "Likely duplicate: High token similarity (91%) with matching brand 'Keychron'."
            },
            {
              "primary_product_id": "PRD-05",
              "primary_sku": "SKU-3001",
              "primary_name": "Sony WH-1000XM5 Noise Canceling Headphones",
              "duplicate_product_id": "PRD-06",
              "duplicate_sku": "SKU-3002",
              "duplicate_name": "Sony WH 1000XM5 Headphones - Silver",
              "match_type": "possible_attribute_similarity",
              "confidence": "possible",
              "similarity_score": 0.73,
              "matching_fields": [
                "product_name"
              ],
              "explanation": "Possible duplicate: Moderate name overlap (73%); manual verification recommended."
            }
          ],
          "total_candidates_found": 3,
          "summary": "Found 3 duplicate candidate pair(s)."
        },
        "error": null
      },
      {
        "step_number": 5,
        "step_name": "group likely duplicates",
        "status": "completed",
        "output_summary": "Grouped duplicates: 1 definite, 1 likely, 1 possible.",
        "output": {
          "grouped_duplicates": {
            "definite": [
              {
                "primary_product_id": "PRD-01",
                "primary_sku": "SKU-1001",
                "primary_name": "Logitech MX Master 3S Wireless Mouse",
                "duplicate_product_id": "PRD-02",
                "duplicate_sku": "SKU-1001",
                "duplicate_name": "Logitech MX Master 3S Mouse - Graphite",
                "match_type": "exact_sku_match",
                "confidence": "definite",
                "similarity_score": 1.0,
                "matching_fields": [
                  "sku"
                ],
                "explanation": "Definite duplicate: Identical SKU found across multiple records."
              }
            ],
            "likely": [
              {
                "primary_product_id": "PRD-03",
                "primary_sku": "SKU-2001",
                "primary_name": "Keychron K2 Mechanical Keyboard RGB",
                "duplicate_product_id": "PRD-04",
                "duplicate_sku": "SKU-2002",
                "duplicate_name": "Keychron K2 Wireless Mechanical Keyboard (RGB)",
                "match_type": "high_attribute_similarity",
                "confidence": "likely",
                "similarity_score": 0.91,
                "matching_fields": [
                  "product_name",
                  "brand",
                  "category"
                ],
                "explanation": "Likely duplicate: High token similarity (91%) with matching brand 'Keychron'."
              }
            ],
            "possible": [
              {
                "primary_product_id": "PRD-05",
                "primary_sku": "SKU-3001",
                "primary_name": "Sony WH-1000XM5 Noise Canceling Headphones",
                "duplicate_product_id": "PRD-06",
                "duplicate_sku": "SKU-3002",
                "duplicate_name": "Sony WH 1000XM5 Headphones - Silver",
                "match_type": "possible_attribute_similarity",
                "confidence": "possible",
                "similarity_score": 0.73,
                "matching_fields": [
                  "product_name"
                ],
                "explanation": "Possible duplicate: Moderate name overlap (73%); manual verification recommended."
              }
            ]
          },
          "summary": "Grouped duplicates: 1 definite, 1 likely, 1 possible."
        },
        "error": null
      },
      {
        "step_number": 6,
        "step_name": "assign confidence",
        "status": "completed",
        "output_summary": "Detected 3 duplicate group(s) across catalog: 1 definite (exact SKU), 1 likely (high similarity), 1 possible.",
        "output": {
          "duplicate_candidates": [
            {
              "primary_product_id": "PRD-01",
              "primary_sku": "SKU-1001",
              "primary_name": "Logitech MX Master 3S Wireless Mouse",
              "duplicate_product_id": "PRD-02",
              "duplicate_sku": "SKU-1001",
              "duplicate_name": "Logitech MX Master 3S Mouse - Graphite",
              "match_type": "exact_sku_match",
              "confidence": "definite",
              "similarity_score": 1.0,
              "matching_fields": [
                "sku"
              ],
              "explanation": "Definite duplicate: Identical SKU found across multiple records."
            },
            {
              "primary_product_id": "PRD-03",
              "primary_sku": "SKU-2001",
              "primary_name": "Keychron K2 Mechanical Keyboard RGB",
              "duplicate_product_id": "PRD-04",
              "duplicate_sku": "SKU-2002",
              "duplicate_name": "Keychron K2 Wireless Mechanical Keyboard (RGB)",
              "match_type": "high_attribute_similarity",
              "confidence": "likely",
              "similarity_score": 0.91,
              "matching_fields": [
                "product_name",
                "brand",
                "category"
              ],
              "explanation": "Likely duplicate: High token similarity (91%) with matching brand 'Keychron'."
            },
            {
              "primary_product_id": "PRD-05",
              "primary_sku": "SKU-3001",
              "primary_name": "Sony WH-1000XM5 Noise Canceling Headphones",
              "duplicate_product_id": "PRD-06",
              "duplicate_sku": "SKU-3002",
              "duplicate_name": "Sony WH 1000XM5 Headphones - Silver",
              "match_type": "possible_attribute_similarity",
              "confidence": "possible",
              "similarity_score": 0.73,
              "matching_fields": [
                "product_name"
              ],
              "explanation": "Possible duplicate: Moderate name overlap (73%); manual verification recommended."
            }
          ],
          "total_duplicates_found": 3,
          "definite_duplicates_count": 1,
          "likely_duplicates_count": 1,
          "possible_duplicates_count": 1,
          "methodology": "Matching Method: (1) Exact normalized SKU equality marks definite duplicates. (2) Token Dice similarity >= 0.75 with matching brand marks likely duplicates. (3) Token Dice similarity between 0.65-0.74 marks possible duplicates. Limitations: Token-based matching does not parse semantic synonyms (e.g. 'lap desk' vs 'bed tray') and requires manual review for possible duplicates.",
          "limitations": "Matching Method: (1) Exact normalized SKU equality marks definite duplicates. (2) Token Dice similarity >= 0.75 with matching brand marks likely duplicates. (3) Token Dice similarity between 0.65-0.74 marks possible duplicates. Limitations: Token-based matching does not parse semantic synonyms (e.g. 'lap desk' vs 'bed tray') and requires manual review for possible duplicates.",
          "summary": "Detected 3 duplicate group(s) across catalog: 1 definite (exact SKU), 1 likely (high similarity), 1 possible."
        },
        "error": null
      }
    ],
    "final_output": {
      "duplicate_candidates": [
        {
          "primary_product_id": "PRD-01",
          "primary_sku": "SKU-1001",
          "primary_name": "Logitech MX Master 3S Wireless Mouse",
          "duplicate_product_id": "PRD-02",
          "duplicate_sku": "SKU-1001",
          "duplicate_name": "Logitech MX Master 3S Mouse - Graphite",
          "match_type": "exact_sku_match",
          "confidence": "definite",
          "similarity_score": 1.0,
          "matching_fields": [
            "sku"
          ],
          "explanation": "Definite duplicate: Identical SKU found across multiple records."
        },
        {
          "primary_product_id": "PRD-03",
          "primary_sku": "SKU-2001",
          "primary_name": "Keychron K2 Mechanical Keyboard RGB",
          "duplicate_product_id": "PRD-04",
          "duplicate_sku": "SKU-2002",
          "duplicate_name": "Keychron K2 Wireless Mechanical Keyboard (RGB)",
          "match_type": "high_attribute_similarity",
          "confidence": "likely",
          "similarity_score": 0.91,
          "matching_fields": [
            "product_name",
            "brand",
            "category"
          ],
          "explanation": "Likely duplicate: High token similarity (91%) with matching brand 'Keychron'."
        },
        {
          "primary_product_id": "PRD-05",
          "primary_sku": "SKU-3001",
          "primary_name": "Sony WH-1000XM5 Noise Canceling Headphones",
          "duplicate_product_id": "PRD-06",
          "duplicate_sku": "SKU-3002",
          "duplicate_name": "Sony WH 1000XM5 Headphones - Silver",
          "match_type": "possible_attribute_similarity",
          "confidence": "possible",
          "similarity_score": 0.73,
          "matching_fields": [
            "product_name"
          ],
          "explanation": "Possible duplicate: Moderate name overlap (73%); manual verification recommended."
        }
      ],
      "total_duplicates_found": 3,
      "definite_duplicates_count": 1,
      "likely_duplicates_count": 1,
      "possible_duplicates_count": 1,
      "methodology": "Matching Method: (1) Exact normalized SKU equality marks definite duplicates. (2) Token Dice similarity >= 0.75 with matching brand marks likely duplicates. (3) Token Dice similarity between 0.65-0.74 marks possible duplicates. Limitations: Token-based matching does not parse semantic synonyms (e.g. 'lap desk' vs 'bed tray') and requires manual review for possible duplicates.",
      "limitations": "Matching Method: (1) Exact normalized SKU equality marks definite duplicates. (2) Token Dice similarity >= 0.75 with matching brand marks likely duplicates. (3) Token Dice similarity between 0.65-0.74 marks possible duplicates. Limitations: Token-based matching does not parse semantic synonyms (e.g. 'lap desk' vs 'bed tray') and requires manual review for possible duplicates.",
      "summary": "Detected 3 duplicate group(s) across catalog: 1 definite (exact SKU), 1 likely (high similarity), 1 possible."
    },
    "errors": [],
    "clarification_required": false,
    "routing_mode": "offline",
    "warnings": []
  },
  "wf006_paraphrase": {
    "request": "Detect duplicate catalog listings that have matching titles or identical SKUs.",
    "selected_workflow_id": "WF006",
    "selected_workflow_name": "Duplicate Product Detection",
    "routing_confidence": 0.75,
    "routing_reasoning": "Offline keyword match against trigger/metadata for WF006 (Duplicate Product Detection): matched terms [duplicate, sku].",
    "status": "success",
    "steps": [
      {
        "step_number": 1,
        "step_name": "Load products",
        "status": "completed",
        "output_summary": "Loaded 9 product(s) from 'sample_products_catalog.csv'.",
        "output": {
          "raw_products": [
            {
              "product_id": "PRD-01",
              "sku": "SKU-1001",
              "product_name": "Logitech MX Master 3S Wireless Mouse",
              "category": "Electronics",
              "brand": "Logitech",
              "price": 99.99
            },
            {
              "product_id": "PRD-02",
              "sku": "SKU-1001",
              "product_name": "Logitech MX Master 3S Mouse - Graphite",
              "category": "Electronics",
              "brand": "Logitech",
              "price": 99.99
            },
            {
              "product_id": "PRD-03",
              "sku": "SKU-2001",
              "product_name": "Keychron K2 Mechanical Keyboard RGB",
              "category": "Electronics",
              "brand": "Keychron",
              "price": 79.99
            },
            {
              "product_id": "PRD-04",
              "sku": "SKU-2002",
              "product_name": "Keychron K2 Wireless Mechanical Keyboard (RGB)",
              "category": "Electronics",
              "brand": "Keychron",
              "price": 79.99
            },
            {
              "product_id": "PRD-05",
              "sku": "SKU-3001",
              "product_name": "Sony WH-1000XM5 Noise Canceling Headphones",
              "category": "Audio",
              "brand": "Sony",
              "price": 399.99
            },
            {
              "product_id": "PRD-06",
              "sku": "SKU-3002",
              "product_name": "Sony WH 1000XM5 Headphones - Silver",
              "category": "Audio",
              "brand": "Sony",
              "price": 399.99
            },
            {
              "product_id": "PRD-07",
              "sku": "SKU-4001",
              "product_name": "Apple MacBook Pro 16-inch M3 Max",
              "category": "Computers",
              "brand": "Apple",
              "price": 3499.0
            },
            {
              "product_id": "PRD-08",
              "sku": "SKU-5001",
              "product_name": "Dell UltraSharp 27 4K USB-C Hub Monitor",
              "category": "Displays",
              "brand": "Dell",
              "price": 549.99
            },
            {
              "product_id": "PRD-09",
              "sku": "SKU-6001",
              "product_name": "Anker 737 Power Bank 24000mAh",
              "category": "Accessories",
              "brand": "Anker",
              "price": 149.99
            }
          ],
          "total_products_loaded": 9,
          "summary": "Loaded 9 product(s) from 'sample_products_catalog.csv'."
        },
        "error": null
      },
      {
        "step_number": 2,
        "step_name": "normalize names/SKUs",
        "status": "completed",
        "output_summary": "Normalized 9 catalog product records.",
        "output": {
          "normalized_products": [
            {
              "product_id": "PRD-01",
              "raw_sku": "SKU-1001",
              "normalized_sku": "SKU1001",
              "raw_name": "Logitech MX Master 3S Wireless Mouse",
              "normalized_name": "logitech mx master 3s wireless mouse",
              "tokens": [
                "3s",
                "logitech",
                "master",
                "mouse",
                "mx",
                "wireless"
              ],
              "category": "electronics",
              "brand": "logitech",
              "price": 99.99
            },
            {
              "product_id": "PRD-02",
              "raw_sku": "SKU-1001",
              "normalized_sku": "SKU1001",
              "raw_name": "Logitech MX Master 3S Mouse - Graphite",
              "normalized_name": "logitech mx master 3s mouse - graphite",
              "tokens": [
                "3s",
                "graphite",
                "logitech",
                "master",
                "mouse",
                "mx"
              ],
              "category": "electronics",
              "brand": "logitech",
              "price": 99.99
            },
            {
              "product_id": "PRD-03",
              "raw_sku": "SKU-2001",
              "normalized_sku": "SKU2001",
              "raw_name": "Keychron K2 Mechanical Keyboard RGB",
              "normalized_name": "keychron k2 mechanical keyboard rgb",
              "tokens": [
                "k2",
                "keyboard",
                "keychron",
                "mechanical",
                "rgb"
              ],
              "category": "electronics",
              "brand": "keychron",
              "price": 79.99
            },
            {
              "product_id": "PRD-04",
              "raw_sku": "SKU-2002",
              "normalized_sku": "SKU2002",
              "raw_name": "Keychron K2 Wireless Mechanical Keyboard (RGB)",
              "normalized_name": "keychron k2 wireless mechanical keyboard (rgb)",
              "tokens": [
                "k2",
                "keyboard",
                "keychron",
                "mechanical",
                "rgb",
                "wireless"
              ],
              "category": "electronics",
              "brand": "keychron",
              "price": 79.99
            },
            {
              "product_id": "PRD-05",
              "raw_sku": "SKU-3001",
              "normalized_sku": "SKU3001",
              "raw_name": "Sony WH-1000XM5 Noise Canceling Headphones",
              "normalized_name": "sony wh-1000xm5 noise canceling headphones",
              "tokens": [
                "1000xm5",
                "canceling",
                "headphones",
                "noise",
                "sony",
                "wh"
              ],
              "category": "audio",
              "brand": "sony",
              "price": 399.99
            },
            {
              "product_id": "PRD-06",
              "raw_sku": "SKU-3002",
              "normalized_sku": "SKU3002",
              "raw_name": "Sony WH 1000XM5 Headphones - Silver",
              "normalized_name": "sony wh 1000xm5 headphones - silver",
              "tokens": [
                "1000xm5",
                "headphones",
                "silver",
                "sony",
                "wh"
              ],
              "category": "audio",
              "brand": "sony",
              "price": 399.99
            },
            {
              "product_id": "PRD-07",
              "raw_sku": "SKU-4001",
              "normalized_sku": "SKU4001",
              "raw_name": "Apple MacBook Pro 16-inch M3 Max",
              "normalized_name": "apple macbook pro 16-inch m3 max",
              "tokens": [
                "16",
                "apple",
                "inch",
                "m3",
                "macbook",
                "max",
                "pro"
              ],
              "category": "computers",
              "brand": "apple",
              "price": 3499.0
            },
            {
              "product_id": "PRD-08",
              "raw_sku": "SKU-5001",
              "normalized_sku": "SKU5001",
              "raw_name": "Dell UltraSharp 27 4K USB-C Hub Monitor",
              "normalized_name": "dell ultrasharp 27 4k usb-c hub monitor",
              "tokens": [
                "27",
                "4k",
                "dell",
                "hub",
                "monitor",
                "ultrasharp",
                "usb"
              ],
              "category": "displays",
              "brand": "dell",
              "price": 549.99
            },
            {
              "product_id": "PRD-09",
              "raw_sku": "SKU-6001",
              "normalized_sku": "SKU6001",
              "raw_name": "Anker 737 Power Bank 24000mAh",
              "normalized_name": "anker 737 power bank 24000mah",
              "tokens": [
                "24000mah",
                "737",
                "anker",
                "bank",
                "power"
              ],
              "category": "accessories",
              "brand": "anker",
              "price": 149.99
            }
          ],
          "summary": "Normalized 9 catalog product records."
        },
        "error": null
      },
      {
        "step_number": 3,
        "step_name": "compare identifiers",
        "status": "completed",
        "output_summary": "Identified 1 exact duplicate SKU group(s).",
        "output": {
          "exact_sku_matches": [
            {
              "sku": "SKU1001",
              "duplicate_count": 2,
              "products": [
                "PRD-01",
                "PRD-02"
              ]
            }
          ],
          "exact_duplicate_sku_count": 1,
          "summary": "Identified 1 exact duplicate SKU group(s)."
        },
        "error": null
      },
      {
        "step_number": 4,
        "step_name": "compare product attributes",
        "status": "completed",
        "output_summary": "Found 3 duplicate candidate pair(s).",
        "output": {
          "duplicate_candidates": [
            {
              "primary_product_id": "PRD-01",
              "primary_sku": "SKU-1001",
              "primary_name": "Logitech MX Master 3S Wireless Mouse",
              "duplicate_product_id": "PRD-02",
              "duplicate_sku": "SKU-1001",
              "duplicate_name": "Logitech MX Master 3S Mouse - Graphite",
              "match_type": "exact_sku_match",
              "confidence": "definite",
              "similarity_score": 1.0,
              "matching_fields": [
                "sku"
              ],
              "explanation": "Definite duplicate: Identical SKU found across multiple records."
            },
            {
              "primary_product_id": "PRD-03",
              "primary_sku": "SKU-2001",
              "primary_name": "Keychron K2 Mechanical Keyboard RGB",
              "duplicate_product_id": "PRD-04",
              "duplicate_sku": "SKU-2002",
              "duplicate_name": "Keychron K2 Wireless Mechanical Keyboard (RGB)",
              "match_type": "high_attribute_similarity",
              "confidence": "likely",
              "similarity_score": 0.91,
              "matching_fields": [
                "product_name",
                "brand",
                "category"
              ],
              "explanation": "Likely duplicate: High token similarity (91%) with matching brand 'Keychron'."
            },
            {
              "primary_product_id": "PRD-05",
              "primary_sku": "SKU-3001",
              "primary_name": "Sony WH-1000XM5 Noise Canceling Headphones",
              "duplicate_product_id": "PRD-06",
              "duplicate_sku": "SKU-3002",
              "duplicate_name": "Sony WH 1000XM5 Headphones - Silver",
              "match_type": "possible_attribute_similarity",
              "confidence": "possible",
              "similarity_score": 0.73,
              "matching_fields": [
                "product_name"
              ],
              "explanation": "Possible duplicate: Moderate name overlap (73%); manual verification recommended."
            }
          ],
          "total_candidates_found": 3,
          "summary": "Found 3 duplicate candidate pair(s)."
        },
        "error": null
      },
      {
        "step_number": 5,
        "step_name": "group likely duplicates",
        "status": "completed",
        "output_summary": "Grouped duplicates: 1 definite, 1 likely, 1 possible.",
        "output": {
          "grouped_duplicates": {
            "definite": [
              {
                "primary_product_id": "PRD-01",
                "primary_sku": "SKU-1001",
                "primary_name": "Logitech MX Master 3S Wireless Mouse",
                "duplicate_product_id": "PRD-02",
                "duplicate_sku": "SKU-1001",
                "duplicate_name": "Logitech MX Master 3S Mouse - Graphite",
                "match_type": "exact_sku_match",
                "confidence": "definite",
                "similarity_score": 1.0,
                "matching_fields": [
                  "sku"
                ],
                "explanation": "Definite duplicate: Identical SKU found across multiple records."
              }
            ],
            "likely": [
              {
                "primary_product_id": "PRD-03",
                "primary_sku": "SKU-2001",
                "primary_name": "Keychron K2 Mechanical Keyboard RGB",
                "duplicate_product_id": "PRD-04",
                "duplicate_sku": "SKU-2002",
                "duplicate_name": "Keychron K2 Wireless Mechanical Keyboard (RGB)",
                "match_type": "high_attribute_similarity",
                "confidence": "likely",
                "similarity_score": 0.91,
                "matching_fields": [
                  "product_name",
                  "brand",
                  "category"
                ],
                "explanation": "Likely duplicate: High token similarity (91%) with matching brand 'Keychron'."
              }
            ],
            "possible": [
              {
                "primary_product_id": "PRD-05",
                "primary_sku": "SKU-3001",
                "primary_name": "Sony WH-1000XM5 Noise Canceling Headphones",
                "duplicate_product_id": "PRD-06",
                "duplicate_sku": "SKU-3002",
                "duplicate_name": "Sony WH 1000XM5 Headphones - Silver",
                "match_type": "possible_attribute_similarity",
                "confidence": "possible",
                "similarity_score": 0.73,
                "matching_fields": [
                  "product_name"
                ],
                "explanation": "Possible duplicate: Moderate name overlap (73%); manual verification recommended."
              }
            ]
          },
          "summary": "Grouped duplicates: 1 definite, 1 likely, 1 possible."
        },
        "error": null
      },
      {
        "step_number": 6,
        "step_name": "assign confidence",
        "status": "completed",
        "output_summary": "Detected 3 duplicate group(s) across catalog: 1 definite (exact SKU), 1 likely (high similarity), 1 possible.",
        "output": {
          "duplicate_candidates": [
            {
              "primary_product_id": "PRD-01",
              "primary_sku": "SKU-1001",
              "primary_name": "Logitech MX Master 3S Wireless Mouse",
              "duplicate_product_id": "PRD-02",
              "duplicate_sku": "SKU-1001",
              "duplicate_name": "Logitech MX Master 3S Mouse - Graphite",
              "match_type": "exact_sku_match",
              "confidence": "definite",
              "similarity_score": 1.0,
              "matching_fields": [
                "sku"
              ],
              "explanation": "Definite duplicate: Identical SKU found across multiple records."
            },
            {
              "primary_product_id": "PRD-03",
              "primary_sku": "SKU-2001",
              "primary_name": "Keychron K2 Mechanical Keyboard RGB",
              "duplicate_product_id": "PRD-04",
              "duplicate_sku": "SKU-2002",
              "duplicate_name": "Keychron K2 Wireless Mechanical Keyboard (RGB)",
              "match_type": "high_attribute_similarity",
              "confidence": "likely",
              "similarity_score": 0.91,
              "matching_fields": [
                "product_name",
                "brand",
                "category"
              ],
              "explanation": "Likely duplicate: High token similarity (91%) with matching brand 'Keychron'."
            },
            {
              "primary_product_id": "PRD-05",
              "primary_sku": "SKU-3001",
              "primary_name": "Sony WH-1000XM5 Noise Canceling Headphones",
              "duplicate_product_id": "PRD-06",
              "duplicate_sku": "SKU-3002",
              "duplicate_name": "Sony WH 1000XM5 Headphones - Silver",
              "match_type": "possible_attribute_similarity",
              "confidence": "possible",
              "similarity_score": 0.73,
              "matching_fields": [
                "product_name"
              ],
              "explanation": "Possible duplicate: Moderate name overlap (73%); manual verification recommended."
            }
          ],
          "total_duplicates_found": 3,
          "definite_duplicates_count": 1,
          "likely_duplicates_count": 1,
          "possible_duplicates_count": 1,
          "methodology": "Matching Method: (1) Exact normalized SKU equality marks definite duplicates. (2) Token Dice similarity >= 0.75 with matching brand marks likely duplicates. (3) Token Dice similarity between 0.65-0.74 marks possible duplicates. Limitations: Token-based matching does not parse semantic synonyms (e.g. 'lap desk' vs 'bed tray') and requires manual review for possible duplicates.",
          "limitations": "Matching Method: (1) Exact normalized SKU equality marks definite duplicates. (2) Token Dice similarity >= 0.75 with matching brand marks likely duplicates. (3) Token Dice similarity between 0.65-0.74 marks possible duplicates. Limitations: Token-based matching does not parse semantic synonyms (e.g. 'lap desk' vs 'bed tray') and requires manual review for possible duplicates.",
          "summary": "Detected 3 duplicate group(s) across catalog: 1 definite (exact SKU), 1 likely (high similarity), 1 possible."
        },
        "error": null
      }
    ],
    "final_output": {
      "duplicate_candidates": [
        {
          "primary_product_id": "PRD-01",
          "primary_sku": "SKU-1001",
          "primary_name": "Logitech MX Master 3S Wireless Mouse",
          "duplicate_product_id": "PRD-02",
          "duplicate_sku": "SKU-1001",
          "duplicate_name": "Logitech MX Master 3S Mouse - Graphite",
          "match_type": "exact_sku_match",
          "confidence": "definite",
          "similarity_score": 1.0,
          "matching_fields": [
            "sku"
          ],
          "explanation": "Definite duplicate: Identical SKU found across multiple records."
        },
        {
          "primary_product_id": "PRD-03",
          "primary_sku": "SKU-2001",
          "primary_name": "Keychron K2 Mechanical Keyboard RGB",
          "duplicate_product_id": "PRD-04",
          "duplicate_sku": "SKU-2002",
          "duplicate_name": "Keychron K2 Wireless Mechanical Keyboard (RGB)",
          "match_type": "high_attribute_similarity",
          "confidence": "likely",
          "similarity_score": 0.91,
          "matching_fields": [
            "product_name",
            "brand",
            "category"
          ],
          "explanation": "Likely duplicate: High token similarity (91%) with matching brand 'Keychron'."
        },
        {
          "primary_product_id": "PRD-05",
          "primary_sku": "SKU-3001",
          "primary_name": "Sony WH-1000XM5 Noise Canceling Headphones",
          "duplicate_product_id": "PRD-06",
          "duplicate_sku": "SKU-3002",
          "duplicate_name": "Sony WH 1000XM5 Headphones - Silver",
          "match_type": "possible_attribute_similarity",
          "confidence": "possible",
          "similarity_score": 0.73,
          "matching_fields": [
            "product_name"
          ],
          "explanation": "Possible duplicate: Moderate name overlap (73%); manual verification recommended."
        }
      ],
      "total_duplicates_found": 3,
      "definite_duplicates_count": 1,
      "likely_duplicates_count": 1,
      "possible_duplicates_count": 1,
      "methodology": "Matching Method: (1) Exact normalized SKU equality marks definite duplicates. (2) Token Dice similarity >= 0.75 with matching brand marks likely duplicates. (3) Token Dice similarity between 0.65-0.74 marks possible duplicates. Limitations: Token-based matching does not parse semantic synonyms (e.g. 'lap desk' vs 'bed tray') and requires manual review for possible duplicates.",
      "limitations": "Matching Method: (1) Exact normalized SKU equality marks definite duplicates. (2) Token Dice similarity >= 0.75 with matching brand marks likely duplicates. (3) Token Dice similarity between 0.65-0.74 marks possible duplicates. Limitations: Token-based matching does not parse semantic synonyms (e.g. 'lap desk' vs 'bed tray') and requires manual review for possible duplicates.",
      "summary": "Detected 3 duplicate group(s) across catalog: 1 definite (exact SKU), 1 likely (high similarity), 1 possible."
    },
    "errors": [],
    "clarification_required": false,
    "routing_mode": "offline",
    "warnings": []
  },
  "wf007_campaign_brief": {
    "request": "Create a campaign brief for the new collection.",
    "selected_workflow_id": "WF007",
    "selected_workflow_name": "Marketing Campaign Brief",
    "routing_confidence": 0.8,
    "routing_reasoning": "Offline keyword match against trigger/metadata for WF007 (Marketing Campaign Brief): matched terms [brief, campaign, create].",
    "status": "needs_clarification",
    "steps": [
      {
        "step_number": 1,
        "step_name": "Validate inputs",
        "status": "needs_clarification",
        "output_summary": null,
        "output": null,
        "error": "Required input 'campaign_goal' is missing. Please provide a specific campaign goal before generating the campaign brief."
      }
    ],
    "final_output": null,
    "errors": [
      "Required input 'campaign_goal' is missing. Please provide a specific campaign goal before generating the campaign brief."
    ],
    "clarification_required": true,
    "routing_mode": "offline",
    "warnings": []
  },
  "wf007_paraphrase": {
    "request": "Draft a comprehensive marketing brief including audience messaging and channel checklist.",
    "selected_workflow_id": "WF007",
    "selected_workflow_name": "Marketing Campaign Brief",
    "routing_confidence": 0.9,
    "routing_reasoning": "Offline keyword match against trigger/metadata for WF007 (Marketing Campaign Brief): matched terms [brief, channel, checklist, market, messag].",
    "status": "needs_clarification",
    "steps": [
      {
        "step_number": 1,
        "step_name": "Validate inputs",
        "status": "needs_clarification",
        "output_summary": null,
        "output": null,
        "error": "Required input 'campaign_goal' is missing. Please provide a specific campaign goal before generating the campaign brief."
      }
    ],
    "final_output": null,
    "errors": [
      "Required input 'campaign_goal' is missing. Please provide a specific campaign goal before generating the campaign brief."
    ],
    "clarification_required": true,
    "routing_mode": "offline",
    "warnings": []
  },
  "wf008_paraphrase": {
    "request": "Group SEO search queries by user intent and assign keyword priorities.",
    "selected_workflow_id": "WF008",
    "selected_workflow_name": "SEO Keyword Classification",
    "routing_confidence": 0.8,
    "routing_reasoning": "Offline keyword match against trigger/metadata for WF008 (SEO Keyword Classification): matched terms [intent, keyword, seo].",
    "status": "success",
    "steps": [
      {
        "step_number": 1,
        "step_name": "Read keywords",
        "status": "completed",
        "output_summary": "Read 13 keyword record(s).",
        "output": {
          "raw_keywords": [
            {
              "keyword": "how to clean mechanical keyboard",
              "search_volume": 8500,
              "cpc": 0.45,
              "competition": "Low"
            },
            {
              "keyword": "buy keychron k2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High"
            },
            {
              "keyword": "best mechanical keyboard for coding",
              "search_volume": 22000,
              "cpc": 1.8,
              "competition": "Medium"
            },
            {
              "keyword": "logitech mx master 3s official website",
              "search_volume": 9800,
              "cpc": 0.85,
              "competition": "Low"
            },
            {
              "keyword": "Keychron K2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High"
            },
            {
              "keyword": "BUY Keychron K2 Wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High"
            },
            {
              "keyword": "ergonomic office chair setup guide",
              "search_volume": 4300,
              "cpc": 0.6,
              "competition": "Low"
            },
            {
              "keyword": "order logitech mx master 3s discount",
              "search_volume": 11000,
              "cpc": 2.4,
              "competition": "High"
            },
            {
              "keyword": "sony wh-1000xm5 review vs bose",
              "search_volume": 18500,
              "cpc": 1.95,
              "competition": "Medium"
            },
            {
              "keyword": "top noise cancelling headphones 2026",
              "search_volume": 29000,
              "cpc": 2.1,
              "competition": "High"
            },
            {
              "keyword": "logitech support customer portal",
              "search_volume": 6200,
              "cpc": 0.3,
              "competition": "Low"
            },
            {
              "keyword": "purchase usb-c docking station 4k",
              "search_volume": 7800,
              "cpc": 2.8,
              "competition": "High"
            },
            {
              "keyword": "what is an ergonomic vertical mouse",
              "search_volume": 5100,
              "cpc": 0.5,
              "competition": "Low"
            }
          ],
          "total_keywords_read": 13,
          "summary": "Read 13 keyword record(s)."
        },
        "error": null
      },
      {
        "step_number": 2,
        "step_name": "remove duplicates",
        "status": "completed",
        "output_summary": "Deduplicated keyword list: 12 unique keywords (1 duplicates removed).",
        "output": {
          "deduplicated_keywords": [
            {
              "keyword": "how to clean mechanical keyboard",
              "search_volume": 8500,
              "cpc": 0.45,
              "competition": "Low"
            },
            {
              "keyword": "buy keychron k2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High"
            },
            {
              "keyword": "best mechanical keyboard for coding",
              "search_volume": 22000,
              "cpc": 1.8,
              "competition": "Medium"
            },
            {
              "keyword": "logitech mx master 3s official website",
              "search_volume": 9800,
              "cpc": 0.85,
              "competition": "Low"
            },
            {
              "keyword": "keychron k2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High"
            },
            {
              "keyword": "ergonomic office chair setup guide",
              "search_volume": 4300,
              "cpc": 0.6,
              "competition": "Low"
            },
            {
              "keyword": "order logitech mx master 3s discount",
              "search_volume": 11000,
              "cpc": 2.4,
              "competition": "High"
            },
            {
              "keyword": "sony wh-1000xm5 review vs bose",
              "search_volume": 18500,
              "cpc": 1.95,
              "competition": "Medium"
            },
            {
              "keyword": "top noise cancelling headphones 2026",
              "search_volume": 29000,
              "cpc": 2.1,
              "competition": "High"
            },
            {
              "keyword": "logitech support customer portal",
              "search_volume": 6200,
              "cpc": 0.3,
              "competition": "Low"
            },
            {
              "keyword": "purchase usb-c docking station 4k",
              "search_volume": 7800,
              "cpc": 2.8,
              "competition": "High"
            },
            {
              "keyword": "what is an ergonomic vertical mouse",
              "search_volume": 5100,
              "cpc": 0.5,
              "competition": "Low"
            }
          ],
          "duplicates_removed": 1,
          "total_unique_keywords": 12,
          "summary": "Deduplicated keyword list: 12 unique keywords (1 duplicates removed)."
        },
        "error": null
      },
      {
        "step_number": 3,
        "step_name": "classify search intent",
        "status": "completed",
        "output_summary": "Classified 12 keyword(s): 3 transactional, 4 commercial, 3 informational, 2 navigational.",
        "output": {
          "classified_keywords": [
            {
              "keyword": "how to clean mechanical keyboard",
              "search_volume": 8500,
              "cpc": 0.45,
              "competition": "Low",
              "intent": "informational"
            },
            {
              "keyword": "buy keychron k2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High",
              "intent": "transactional"
            },
            {
              "keyword": "best mechanical keyboard for coding",
              "search_volume": 22000,
              "cpc": 1.8,
              "competition": "Medium",
              "intent": "commercial"
            },
            {
              "keyword": "logitech mx master 3s official website",
              "search_volume": 9800,
              "cpc": 0.85,
              "competition": "Low",
              "intent": "navigational"
            },
            {
              "keyword": "keychron k2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High",
              "intent": "commercial"
            },
            {
              "keyword": "ergonomic office chair setup guide",
              "search_volume": 4300,
              "cpc": 0.6,
              "competition": "Low",
              "intent": "informational"
            },
            {
              "keyword": "order logitech mx master 3s discount",
              "search_volume": 11000,
              "cpc": 2.4,
              "competition": "High",
              "intent": "transactional"
            },
            {
              "keyword": "sony wh-1000xm5 review vs bose",
              "search_volume": 18500,
              "cpc": 1.95,
              "competition": "Medium",
              "intent": "commercial"
            },
            {
              "keyword": "top noise cancelling headphones 2026",
              "search_volume": 29000,
              "cpc": 2.1,
              "competition": "High",
              "intent": "commercial"
            },
            {
              "keyword": "logitech support customer portal",
              "search_volume": 6200,
              "cpc": 0.3,
              "competition": "Low",
              "intent": "navigational"
            },
            {
              "keyword": "purchase usb-c docking station 4k",
              "search_volume": 7800,
              "cpc": 2.8,
              "competition": "High",
              "intent": "transactional"
            },
            {
              "keyword": "what is an ergonomic vertical mouse",
              "search_volume": 5100,
              "cpc": 0.5,
              "competition": "Low",
              "intent": "informational"
            }
          ],
          "intent_counts": {
            "transactional": 3,
            "commercial": 4,
            "navigational": 2,
            "informational": 3
          },
          "summary": "Classified 12 keyword(s): 3 transactional, 4 commercial, 3 informational, 2 navigational."
        },
        "error": null
      },
      {
        "step_number": 4,
        "step_name": "map keywords to categories",
        "status": "completed",
        "output_summary": "Mapped 12 keyword(s) across 6 product category/categories.",
        "output": {
          "mapped_keywords": [
            {
              "keyword": "how to clean mechanical keyboard",
              "search_volume": 8500,
              "cpc": 0.45,
              "competition": "Low",
              "intent": "informational",
              "category": "Keyboards & Input",
              "target_page": "/guides/how-to-clean-mechanical-keyboard"
            },
            {
              "keyword": "buy keychron k2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High",
              "intent": "transactional",
              "category": "Keyboards & Input",
              "target_page": "/products/keyboards"
            },
            {
              "keyword": "best mechanical keyboard for coding",
              "search_volume": 22000,
              "cpc": 1.8,
              "competition": "Medium",
              "intent": "commercial",
              "category": "Keyboards & Input",
              "target_page": "/collections/keyboards"
            },
            {
              "keyword": "logitech mx master 3s official website",
              "search_volume": 9800,
              "cpc": 0.85,
              "competition": "Low",
              "intent": "navigational",
              "category": "Mice & Ergonomics",
              "target_page": "/brand/mice"
            },
            {
              "keyword": "keychron k2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High",
              "intent": "commercial",
              "category": "Keyboards & Input",
              "target_page": "/collections/keyboards"
            },
            {
              "keyword": "ergonomic office chair setup guide",
              "search_volume": 4300,
              "cpc": 0.6,
              "competition": "Low",
              "intent": "informational",
              "category": "Office Furniture & Ergonomics",
              "target_page": "/guides/ergonomic-office-chair-setup-guide"
            },
            {
              "keyword": "order logitech mx master 3s discount",
              "search_volume": 11000,
              "cpc": 2.4,
              "competition": "High",
              "intent": "transactional",
              "category": "Mice & Ergonomics",
              "target_page": "/products/mice"
            },
            {
              "keyword": "sony wh-1000xm5 review vs bose",
              "search_volume": 18500,
              "cpc": 1.95,
              "competition": "Medium",
              "intent": "commercial",
              "category": "Audio & Headphones",
              "target_page": "/collections/audio"
            },
            {
              "keyword": "top noise cancelling headphones 2026",
              "search_volume": 29000,
              "cpc": 2.1,
              "competition": "High",
              "intent": "commercial",
              "category": "Audio & Headphones",
              "target_page": "/collections/audio"
            },
            {
              "keyword": "logitech support customer portal",
              "search_volume": 6200,
              "cpc": 0.3,
              "competition": "Low",
              "intent": "navigational",
              "category": "General Tech",
              "target_page": "/support"
            },
            {
              "keyword": "purchase usb-c docking station 4k",
              "search_volume": 7800,
              "cpc": 2.8,
              "competition": "High",
              "intent": "transactional",
              "category": "Docks & Connectivity",
              "target_page": "/products/accessories"
            },
            {
              "keyword": "what is an ergonomic vertical mouse",
              "search_volume": 5100,
              "cpc": 0.5,
              "competition": "Low",
              "intent": "informational",
              "category": "Mice & Ergonomics",
              "target_page": "/guides/what-is-an-ergonomic-vertical-mouse"
            }
          ],
          "category_counts": {
            "Keyboards & Input": 4,
            "Mice & Ergonomics": 3,
            "Office Furniture & Ergonomics": 1,
            "Audio & Headphones": 2,
            "General Tech": 1,
            "Docks & Connectivity": 1
          },
          "summary": "Mapped 12 keyword(s) across 6 product category/categories."
        },
        "error": null
      },
      {
        "step_number": 5,
        "step_name": "identify high-priority keywords",
        "status": "completed",
        "output_summary": "Assigned priorities: 6 HIGH, 2 MEDIUM, 4 LOW.",
        "output": {
          "prioritized_keywords": [
            {
              "keyword": "how to clean mechanical keyboard",
              "search_volume": 8500,
              "cpc": 0.45,
              "competition": "Low",
              "intent": "informational",
              "category": "Keyboards & Input",
              "target_page": "/guides/how-to-clean-mechanical-keyboard",
              "priority": "MEDIUM",
              "priority_reasoning": "Moderate consideration intent or substantial informational discovery volume."
            },
            {
              "keyword": "buy keychron k2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High",
              "intent": "transactional",
              "category": "Keyboards & Input",
              "target_page": "/products/keyboards",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "best mechanical keyboard for coding",
              "search_volume": 22000,
              "cpc": 1.8,
              "competition": "Medium",
              "intent": "commercial",
              "category": "Keyboards & Input",
              "target_page": "/collections/keyboards",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "logitech mx master 3s official website",
              "search_volume": 9800,
              "cpc": 0.85,
              "competition": "Low",
              "intent": "navigational",
              "category": "Mice & Ergonomics",
              "target_page": "/brand/mice",
              "priority": "LOW",
              "priority_reasoning": "Navigational or lower-volume informational discovery."
            },
            {
              "keyword": "keychron k2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High",
              "intent": "commercial",
              "category": "Keyboards & Input",
              "target_page": "/collections/keyboards",
              "priority": "MEDIUM",
              "priority_reasoning": "Moderate consideration intent or substantial informational discovery volume."
            },
            {
              "keyword": "ergonomic office chair setup guide",
              "search_volume": 4300,
              "cpc": 0.6,
              "competition": "Low",
              "intent": "informational",
              "category": "Office Furniture & Ergonomics",
              "target_page": "/guides/ergonomic-office-chair-setup-guide",
              "priority": "LOW",
              "priority_reasoning": "Navigational or lower-volume informational discovery."
            },
            {
              "keyword": "order logitech mx master 3s discount",
              "search_volume": 11000,
              "cpc": 2.4,
              "competition": "High",
              "intent": "transactional",
              "category": "Mice & Ergonomics",
              "target_page": "/products/mice",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "sony wh-1000xm5 review vs bose",
              "search_volume": 18500,
              "cpc": 1.95,
              "competition": "Medium",
              "intent": "commercial",
              "category": "Audio & Headphones",
              "target_page": "/collections/audio",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "top noise cancelling headphones 2026",
              "search_volume": 29000,
              "cpc": 2.1,
              "competition": "High",
              "intent": "commercial",
              "category": "Audio & Headphones",
              "target_page": "/collections/audio",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "logitech support customer portal",
              "search_volume": 6200,
              "cpc": 0.3,
              "competition": "Low",
              "intent": "navigational",
              "category": "General Tech",
              "target_page": "/support",
              "priority": "LOW",
              "priority_reasoning": "Navigational or lower-volume informational discovery."
            },
            {
              "keyword": "purchase usb-c docking station 4k",
              "search_volume": 7800,
              "cpc": 2.8,
              "competition": "High",
              "intent": "transactional",
              "category": "Docks & Connectivity",
              "target_page": "/products/accessories",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "what is an ergonomic vertical mouse",
              "search_volume": 5100,
              "cpc": 0.5,
              "competition": "Low",
              "intent": "informational",
              "category": "Mice & Ergonomics",
              "target_page": "/guides/what-is-an-ergonomic-vertical-mouse",
              "priority": "LOW",
              "priority_reasoning": "Navigational or lower-volume informational discovery."
            }
          ],
          "high_priority_count": 6,
          "medium_priority_count": 2,
          "low_priority_count": 4,
          "summary": "Assigned priorities: 6 HIGH, 2 MEDIUM, 4 LOW."
        },
        "error": null
      },
      {
        "step_number": 6,
        "step_name": "export results",
        "status": "completed",
        "output_summary": "Successfully processed and classified 12 keyword(s). Found 6 high-priority keyword(s) for immediate content/landing page optimization.",
        "output": {
          "total_keywords": 12,
          "high_priority_count": 6,
          "medium_priority_count": 2,
          "low_priority_count": 4,
          "intent_counts": {
            "transactional": 3,
            "commercial": 4,
            "navigational": 2,
            "informational": 3
          },
          "category_counts": {
            "Keyboards & Input": 4,
            "Mice & Ergonomics": 3,
            "Office Furniture & Ergonomics": 1,
            "Audio & Headphones": 2,
            "General Tech": 1,
            "Docks & Connectivity": 1
          },
          "keyword_records": [
            {
              "keyword": "how to clean mechanical keyboard",
              "search_volume": 8500,
              "cpc": 0.45,
              "competition": "Low",
              "intent": "informational",
              "category": "Keyboards & Input",
              "target_page": "/guides/how-to-clean-mechanical-keyboard",
              "priority": "MEDIUM",
              "priority_reasoning": "Moderate consideration intent or substantial informational discovery volume."
            },
            {
              "keyword": "buy keychron k2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High",
              "intent": "transactional",
              "category": "Keyboards & Input",
              "target_page": "/products/keyboards",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "best mechanical keyboard for coding",
              "search_volume": 22000,
              "cpc": 1.8,
              "competition": "Medium",
              "intent": "commercial",
              "category": "Keyboards & Input",
              "target_page": "/collections/keyboards",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "logitech mx master 3s official website",
              "search_volume": 9800,
              "cpc": 0.85,
              "competition": "Low",
              "intent": "navigational",
              "category": "Mice & Ergonomics",
              "target_page": "/brand/mice",
              "priority": "LOW",
              "priority_reasoning": "Navigational or lower-volume informational discovery."
            },
            {
              "keyword": "keychron k2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High",
              "intent": "commercial",
              "category": "Keyboards & Input",
              "target_page": "/collections/keyboards",
              "priority": "MEDIUM",
              "priority_reasoning": "Moderate consideration intent or substantial informational discovery volume."
            },
            {
              "keyword": "ergonomic office chair setup guide",
              "search_volume": 4300,
              "cpc": 0.6,
              "competition": "Low",
              "intent": "informational",
              "category": "Office Furniture & Ergonomics",
              "target_page": "/guides/ergonomic-office-chair-setup-guide",
              "priority": "LOW",
              "priority_reasoning": "Navigational or lower-volume informational discovery."
            },
            {
              "keyword": "order logitech mx master 3s discount",
              "search_volume": 11000,
              "cpc": 2.4,
              "competition": "High",
              "intent": "transactional",
              "category": "Mice & Ergonomics",
              "target_page": "/products/mice",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "sony wh-1000xm5 review vs bose",
              "search_volume": 18500,
              "cpc": 1.95,
              "competition": "Medium",
              "intent": "commercial",
              "category": "Audio & Headphones",
              "target_page": "/collections/audio",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "top noise cancelling headphones 2026",
              "search_volume": 29000,
              "cpc": 2.1,
              "competition": "High",
              "intent": "commercial",
              "category": "Audio & Headphones",
              "target_page": "/collections/audio",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "logitech support customer portal",
              "search_volume": 6200,
              "cpc": 0.3,
              "competition": "Low",
              "intent": "navigational",
              "category": "General Tech",
              "target_page": "/support",
              "priority": "LOW",
              "priority_reasoning": "Navigational or lower-volume informational discovery."
            },
            {
              "keyword": "purchase usb-c docking station 4k",
              "search_volume": 7800,
              "cpc": 2.8,
              "competition": "High",
              "intent": "transactional",
              "category": "Docks & Connectivity",
              "target_page": "/products/accessories",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "what is an ergonomic vertical mouse",
              "search_volume": 5100,
              "cpc": 0.5,
              "competition": "Low",
              "intent": "informational",
              "category": "Mice & Ergonomics",
              "target_page": "/guides/what-is-an-ergonomic-vertical-mouse",
              "priority": "LOW",
              "priority_reasoning": "Navigational or lower-volume informational discovery."
            }
          ],
          "high_priority_recommendations": [
            {
              "keyword": "buy keychron k2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High",
              "intent": "transactional",
              "category": "Keyboards & Input",
              "target_page": "/products/keyboards",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "best mechanical keyboard for coding",
              "search_volume": 22000,
              "cpc": 1.8,
              "competition": "Medium",
              "intent": "commercial",
              "category": "Keyboards & Input",
              "target_page": "/collections/keyboards",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "order logitech mx master 3s discount",
              "search_volume": 11000,
              "cpc": 2.4,
              "competition": "High",
              "intent": "transactional",
              "category": "Mice & Ergonomics",
              "target_page": "/products/mice",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "sony wh-1000xm5 review vs bose",
              "search_volume": 18500,
              "cpc": 1.95,
              "competition": "Medium",
              "intent": "commercial",
              "category": "Audio & Headphones",
              "target_page": "/collections/audio",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "top noise cancelling headphones 2026",
              "search_volume": 29000,
              "cpc": 2.1,
              "competition": "High",
              "intent": "commercial",
              "category": "Audio & Headphones",
              "target_page": "/collections/audio",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            }
          ],
          "is_simulated": true,
          "summary": "Successfully processed and classified 12 keyword(s). Found 6 high-priority keyword(s) for immediate content/landing page optimization."
        },
        "error": null
      }
    ],
    "final_output": {
      "total_keywords": 12,
      "high_priority_count": 6,
      "medium_priority_count": 2,
      "low_priority_count": 4,
      "intent_counts": {
        "transactional": 3,
        "commercial": 4,
        "navigational": 2,
        "informational": 3
      },
      "category_counts": {
        "Keyboards & Input": 4,
        "Mice & Ergonomics": 3,
        "Office Furniture & Ergonomics": 1,
        "Audio & Headphones": 2,
        "General Tech": 1,
        "Docks & Connectivity": 1
      },
      "keyword_records": [
        {
          "keyword": "how to clean mechanical keyboard",
          "search_volume": 8500,
          "cpc": 0.45,
          "competition": "Low",
          "intent": "informational",
          "category": "Keyboards & Input",
          "target_page": "/guides/how-to-clean-mechanical-keyboard",
          "priority": "MEDIUM",
          "priority_reasoning": "Moderate consideration intent or substantial informational discovery volume."
        },
        {
          "keyword": "buy keychron k2 wireless",
          "search_volume": 14200,
          "cpc": 2.15,
          "competition": "High",
          "intent": "transactional",
          "category": "Keyboards & Input",
          "target_page": "/products/keyboards",
          "priority": "HIGH",
          "priority_reasoning": "High commercial conversion intent or high search volume."
        },
        {
          "keyword": "best mechanical keyboard for coding",
          "search_volume": 22000,
          "cpc": 1.8,
          "competition": "Medium",
          "intent": "commercial",
          "category": "Keyboards & Input",
          "target_page": "/collections/keyboards",
          "priority": "HIGH",
          "priority_reasoning": "High commercial conversion intent or high search volume."
        },
        {
          "keyword": "logitech mx master 3s official website",
          "search_volume": 9800,
          "cpc": 0.85,
          "competition": "Low",
          "intent": "navigational",
          "category": "Mice & Ergonomics",
          "target_page": "/brand/mice",
          "priority": "LOW",
          "priority_reasoning": "Navigational or lower-volume informational discovery."
        },
        {
          "keyword": "keychron k2 wireless",
          "search_volume": 14200,
          "cpc": 2.15,
          "competition": "High",
          "intent": "commercial",
          "category": "Keyboards & Input",
          "target_page": "/collections/keyboards",
          "priority": "MEDIUM",
          "priority_reasoning": "Moderate consideration intent or substantial informational discovery volume."
        },
        {
          "keyword": "ergonomic office chair setup guide",
          "search_volume": 4300,
          "cpc": 0.6,
          "competition": "Low",
          "intent": "informational",
          "category": "Office Furniture & Ergonomics",
          "target_page": "/guides/ergonomic-office-chair-setup-guide",
          "priority": "LOW",
          "priority_reasoning": "Navigational or lower-volume informational discovery."
        },
        {
          "keyword": "order logitech mx master 3s discount",
          "search_volume": 11000,
          "cpc": 2.4,
          "competition": "High",
          "intent": "transactional",
          "category": "Mice & Ergonomics",
          "target_page": "/products/mice",
          "priority": "HIGH",
          "priority_reasoning": "High commercial conversion intent or high search volume."
        },
        {
          "keyword": "sony wh-1000xm5 review vs bose",
          "search_volume": 18500,
          "cpc": 1.95,
          "competition": "Medium",
          "intent": "commercial",
          "category": "Audio & Headphones",
          "target_page": "/collections/audio",
          "priority": "HIGH",
          "priority_reasoning": "High commercial conversion intent or high search volume."
        },
        {
          "keyword": "top noise cancelling headphones 2026",
          "search_volume": 29000,
          "cpc": 2.1,
          "competition": "High",
          "intent": "commercial",
          "category": "Audio & Headphones",
          "target_page": "/collections/audio",
          "priority": "HIGH",
          "priority_reasoning": "High commercial conversion intent or high search volume."
        },
        {
          "keyword": "logitech support customer portal",
          "search_volume": 6200,
          "cpc": 0.3,
          "competition": "Low",
          "intent": "navigational",
          "category": "General Tech",
          "target_page": "/support",
          "priority": "LOW",
          "priority_reasoning": "Navigational or lower-volume informational discovery."
        },
        {
          "keyword": "purchase usb-c docking station 4k",
          "search_volume": 7800,
          "cpc": 2.8,
          "competition": "High",
          "intent": "transactional",
          "category": "Docks & Connectivity",
          "target_page": "/products/accessories",
          "priority": "HIGH",
          "priority_reasoning": "High commercial conversion intent or high search volume."
        },
        {
          "keyword": "what is an ergonomic vertical mouse",
          "search_volume": 5100,
          "cpc": 0.5,
          "competition": "Low",
          "intent": "informational",
          "category": "Mice & Ergonomics",
          "target_page": "/guides/what-is-an-ergonomic-vertical-mouse",
          "priority": "LOW",
          "priority_reasoning": "Navigational or lower-volume informational discovery."
        }
      ],
      "high_priority_recommendations": [
        {
          "keyword": "buy keychron k2 wireless",
          "search_volume": 14200,
          "cpc": 2.15,
          "competition": "High",
          "intent": "transactional",
          "category": "Keyboards & Input",
          "target_page": "/products/keyboards",
          "priority": "HIGH",
          "priority_reasoning": "High commercial conversion intent or high search volume."
        },
        {
          "keyword": "best mechanical keyboard for coding",
          "search_volume": 22000,
          "cpc": 1.8,
          "competition": "Medium",
          "intent": "commercial",
          "category": "Keyboards & Input",
          "target_page": "/collections/keyboards",
          "priority": "HIGH",
          "priority_reasoning": "High commercial conversion intent or high search volume."
        },
        {
          "keyword": "order logitech mx master 3s discount",
          "search_volume": 11000,
          "cpc": 2.4,
          "competition": "High",
          "intent": "transactional",
          "category": "Mice & Ergonomics",
          "target_page": "/products/mice",
          "priority": "HIGH",
          "priority_reasoning": "High commercial conversion intent or high search volume."
        },
        {
          "keyword": "sony wh-1000xm5 review vs bose",
          "search_volume": 18500,
          "cpc": 1.95,
          "competition": "Medium",
          "intent": "commercial",
          "category": "Audio & Headphones",
          "target_page": "/collections/audio",
          "priority": "HIGH",
          "priority_reasoning": "High commercial conversion intent or high search volume."
        },
        {
          "keyword": "top noise cancelling headphones 2026",
          "search_volume": 29000,
          "cpc": 2.1,
          "competition": "High",
          "intent": "commercial",
          "category": "Audio & Headphones",
          "target_page": "/collections/audio",
          "priority": "HIGH",
          "priority_reasoning": "High commercial conversion intent or high search volume."
        }
      ],
      "is_simulated": true,
      "summary": "Successfully processed and classified 12 keyword(s). Found 6 high-priority keyword(s) for immediate content/landing page optimization."
    },
    "errors": [],
    "clarification_required": false,
    "routing_mode": "offline",
    "warnings": []
  },
  "wf008_seo_keywords": {
    "request": "Classify these keywords and map them to pages.",
    "selected_workflow_id": "WF008",
    "selected_workflow_name": "SEO Keyword Classification",
    "routing_confidence": 0.8,
    "routing_reasoning": "Offline keyword match against trigger/metadata for WF008 (SEO Keyword Classification): matched terms [classify, keyword, map].",
    "status": "success",
    "steps": [
      {
        "step_number": 1,
        "step_name": "Read keywords",
        "status": "completed",
        "output_summary": "Read 13 keyword record(s).",
        "output": {
          "raw_keywords": [
            {
              "keyword": "how to clean mechanical keyboard",
              "search_volume": 8500,
              "cpc": 0.45,
              "competition": "Low"
            },
            {
              "keyword": "buy keychron k2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High"
            },
            {
              "keyword": "best mechanical keyboard for coding",
              "search_volume": 22000,
              "cpc": 1.8,
              "competition": "Medium"
            },
            {
              "keyword": "logitech mx master 3s official website",
              "search_volume": 9800,
              "cpc": 0.85,
              "competition": "Low"
            },
            {
              "keyword": "Keychron K2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High"
            },
            {
              "keyword": "BUY Keychron K2 Wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High"
            },
            {
              "keyword": "ergonomic office chair setup guide",
              "search_volume": 4300,
              "cpc": 0.6,
              "competition": "Low"
            },
            {
              "keyword": "order logitech mx master 3s discount",
              "search_volume": 11000,
              "cpc": 2.4,
              "competition": "High"
            },
            {
              "keyword": "sony wh-1000xm5 review vs bose",
              "search_volume": 18500,
              "cpc": 1.95,
              "competition": "Medium"
            },
            {
              "keyword": "top noise cancelling headphones 2026",
              "search_volume": 29000,
              "cpc": 2.1,
              "competition": "High"
            },
            {
              "keyword": "logitech support customer portal",
              "search_volume": 6200,
              "cpc": 0.3,
              "competition": "Low"
            },
            {
              "keyword": "purchase usb-c docking station 4k",
              "search_volume": 7800,
              "cpc": 2.8,
              "competition": "High"
            },
            {
              "keyword": "what is an ergonomic vertical mouse",
              "search_volume": 5100,
              "cpc": 0.5,
              "competition": "Low"
            }
          ],
          "total_keywords_read": 13,
          "summary": "Read 13 keyword record(s)."
        },
        "error": null
      },
      {
        "step_number": 2,
        "step_name": "remove duplicates",
        "status": "completed",
        "output_summary": "Deduplicated keyword list: 12 unique keywords (1 duplicates removed).",
        "output": {
          "deduplicated_keywords": [
            {
              "keyword": "how to clean mechanical keyboard",
              "search_volume": 8500,
              "cpc": 0.45,
              "competition": "Low"
            },
            {
              "keyword": "buy keychron k2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High"
            },
            {
              "keyword": "best mechanical keyboard for coding",
              "search_volume": 22000,
              "cpc": 1.8,
              "competition": "Medium"
            },
            {
              "keyword": "logitech mx master 3s official website",
              "search_volume": 9800,
              "cpc": 0.85,
              "competition": "Low"
            },
            {
              "keyword": "keychron k2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High"
            },
            {
              "keyword": "ergonomic office chair setup guide",
              "search_volume": 4300,
              "cpc": 0.6,
              "competition": "Low"
            },
            {
              "keyword": "order logitech mx master 3s discount",
              "search_volume": 11000,
              "cpc": 2.4,
              "competition": "High"
            },
            {
              "keyword": "sony wh-1000xm5 review vs bose",
              "search_volume": 18500,
              "cpc": 1.95,
              "competition": "Medium"
            },
            {
              "keyword": "top noise cancelling headphones 2026",
              "search_volume": 29000,
              "cpc": 2.1,
              "competition": "High"
            },
            {
              "keyword": "logitech support customer portal",
              "search_volume": 6200,
              "cpc": 0.3,
              "competition": "Low"
            },
            {
              "keyword": "purchase usb-c docking station 4k",
              "search_volume": 7800,
              "cpc": 2.8,
              "competition": "High"
            },
            {
              "keyword": "what is an ergonomic vertical mouse",
              "search_volume": 5100,
              "cpc": 0.5,
              "competition": "Low"
            }
          ],
          "duplicates_removed": 1,
          "total_unique_keywords": 12,
          "summary": "Deduplicated keyword list: 12 unique keywords (1 duplicates removed)."
        },
        "error": null
      },
      {
        "step_number": 3,
        "step_name": "classify search intent",
        "status": "completed",
        "output_summary": "Classified 12 keyword(s): 3 transactional, 4 commercial, 3 informational, 2 navigational.",
        "output": {
          "classified_keywords": [
            {
              "keyword": "how to clean mechanical keyboard",
              "search_volume": 8500,
              "cpc": 0.45,
              "competition": "Low",
              "intent": "informational"
            },
            {
              "keyword": "buy keychron k2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High",
              "intent": "transactional"
            },
            {
              "keyword": "best mechanical keyboard for coding",
              "search_volume": 22000,
              "cpc": 1.8,
              "competition": "Medium",
              "intent": "commercial"
            },
            {
              "keyword": "logitech mx master 3s official website",
              "search_volume": 9800,
              "cpc": 0.85,
              "competition": "Low",
              "intent": "navigational"
            },
            {
              "keyword": "keychron k2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High",
              "intent": "commercial"
            },
            {
              "keyword": "ergonomic office chair setup guide",
              "search_volume": 4300,
              "cpc": 0.6,
              "competition": "Low",
              "intent": "informational"
            },
            {
              "keyword": "order logitech mx master 3s discount",
              "search_volume": 11000,
              "cpc": 2.4,
              "competition": "High",
              "intent": "transactional"
            },
            {
              "keyword": "sony wh-1000xm5 review vs bose",
              "search_volume": 18500,
              "cpc": 1.95,
              "competition": "Medium",
              "intent": "commercial"
            },
            {
              "keyword": "top noise cancelling headphones 2026",
              "search_volume": 29000,
              "cpc": 2.1,
              "competition": "High",
              "intent": "commercial"
            },
            {
              "keyword": "logitech support customer portal",
              "search_volume": 6200,
              "cpc": 0.3,
              "competition": "Low",
              "intent": "navigational"
            },
            {
              "keyword": "purchase usb-c docking station 4k",
              "search_volume": 7800,
              "cpc": 2.8,
              "competition": "High",
              "intent": "transactional"
            },
            {
              "keyword": "what is an ergonomic vertical mouse",
              "search_volume": 5100,
              "cpc": 0.5,
              "competition": "Low",
              "intent": "informational"
            }
          ],
          "intent_counts": {
            "transactional": 3,
            "commercial": 4,
            "navigational": 2,
            "informational": 3
          },
          "summary": "Classified 12 keyword(s): 3 transactional, 4 commercial, 3 informational, 2 navigational."
        },
        "error": null
      },
      {
        "step_number": 4,
        "step_name": "map keywords to categories",
        "status": "completed",
        "output_summary": "Mapped 12 keyword(s) across 6 product category/categories.",
        "output": {
          "mapped_keywords": [
            {
              "keyword": "how to clean mechanical keyboard",
              "search_volume": 8500,
              "cpc": 0.45,
              "competition": "Low",
              "intent": "informational",
              "category": "Keyboards & Input",
              "target_page": "/guides/how-to-clean-mechanical-keyboard"
            },
            {
              "keyword": "buy keychron k2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High",
              "intent": "transactional",
              "category": "Keyboards & Input",
              "target_page": "/products/keyboards"
            },
            {
              "keyword": "best mechanical keyboard for coding",
              "search_volume": 22000,
              "cpc": 1.8,
              "competition": "Medium",
              "intent": "commercial",
              "category": "Keyboards & Input",
              "target_page": "/collections/keyboards"
            },
            {
              "keyword": "logitech mx master 3s official website",
              "search_volume": 9800,
              "cpc": 0.85,
              "competition": "Low",
              "intent": "navigational",
              "category": "Mice & Ergonomics",
              "target_page": "/brand/mice"
            },
            {
              "keyword": "keychron k2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High",
              "intent": "commercial",
              "category": "Keyboards & Input",
              "target_page": "/collections/keyboards"
            },
            {
              "keyword": "ergonomic office chair setup guide",
              "search_volume": 4300,
              "cpc": 0.6,
              "competition": "Low",
              "intent": "informational",
              "category": "Office Furniture & Ergonomics",
              "target_page": "/guides/ergonomic-office-chair-setup-guide"
            },
            {
              "keyword": "order logitech mx master 3s discount",
              "search_volume": 11000,
              "cpc": 2.4,
              "competition": "High",
              "intent": "transactional",
              "category": "Mice & Ergonomics",
              "target_page": "/products/mice"
            },
            {
              "keyword": "sony wh-1000xm5 review vs bose",
              "search_volume": 18500,
              "cpc": 1.95,
              "competition": "Medium",
              "intent": "commercial",
              "category": "Audio & Headphones",
              "target_page": "/collections/audio"
            },
            {
              "keyword": "top noise cancelling headphones 2026",
              "search_volume": 29000,
              "cpc": 2.1,
              "competition": "High",
              "intent": "commercial",
              "category": "Audio & Headphones",
              "target_page": "/collections/audio"
            },
            {
              "keyword": "logitech support customer portal",
              "search_volume": 6200,
              "cpc": 0.3,
              "competition": "Low",
              "intent": "navigational",
              "category": "General Tech",
              "target_page": "/support"
            },
            {
              "keyword": "purchase usb-c docking station 4k",
              "search_volume": 7800,
              "cpc": 2.8,
              "competition": "High",
              "intent": "transactional",
              "category": "Docks & Connectivity",
              "target_page": "/products/accessories"
            },
            {
              "keyword": "what is an ergonomic vertical mouse",
              "search_volume": 5100,
              "cpc": 0.5,
              "competition": "Low",
              "intent": "informational",
              "category": "Mice & Ergonomics",
              "target_page": "/guides/what-is-an-ergonomic-vertical-mouse"
            }
          ],
          "category_counts": {
            "Keyboards & Input": 4,
            "Mice & Ergonomics": 3,
            "Office Furniture & Ergonomics": 1,
            "Audio & Headphones": 2,
            "General Tech": 1,
            "Docks & Connectivity": 1
          },
          "summary": "Mapped 12 keyword(s) across 6 product category/categories."
        },
        "error": null
      },
      {
        "step_number": 5,
        "step_name": "identify high-priority keywords",
        "status": "completed",
        "output_summary": "Assigned priorities: 6 HIGH, 2 MEDIUM, 4 LOW.",
        "output": {
          "prioritized_keywords": [
            {
              "keyword": "how to clean mechanical keyboard",
              "search_volume": 8500,
              "cpc": 0.45,
              "competition": "Low",
              "intent": "informational",
              "category": "Keyboards & Input",
              "target_page": "/guides/how-to-clean-mechanical-keyboard",
              "priority": "MEDIUM",
              "priority_reasoning": "Moderate consideration intent or substantial informational discovery volume."
            },
            {
              "keyword": "buy keychron k2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High",
              "intent": "transactional",
              "category": "Keyboards & Input",
              "target_page": "/products/keyboards",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "best mechanical keyboard for coding",
              "search_volume": 22000,
              "cpc": 1.8,
              "competition": "Medium",
              "intent": "commercial",
              "category": "Keyboards & Input",
              "target_page": "/collections/keyboards",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "logitech mx master 3s official website",
              "search_volume": 9800,
              "cpc": 0.85,
              "competition": "Low",
              "intent": "navigational",
              "category": "Mice & Ergonomics",
              "target_page": "/brand/mice",
              "priority": "LOW",
              "priority_reasoning": "Navigational or lower-volume informational discovery."
            },
            {
              "keyword": "keychron k2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High",
              "intent": "commercial",
              "category": "Keyboards & Input",
              "target_page": "/collections/keyboards",
              "priority": "MEDIUM",
              "priority_reasoning": "Moderate consideration intent or substantial informational discovery volume."
            },
            {
              "keyword": "ergonomic office chair setup guide",
              "search_volume": 4300,
              "cpc": 0.6,
              "competition": "Low",
              "intent": "informational",
              "category": "Office Furniture & Ergonomics",
              "target_page": "/guides/ergonomic-office-chair-setup-guide",
              "priority": "LOW",
              "priority_reasoning": "Navigational or lower-volume informational discovery."
            },
            {
              "keyword": "order logitech mx master 3s discount",
              "search_volume": 11000,
              "cpc": 2.4,
              "competition": "High",
              "intent": "transactional",
              "category": "Mice & Ergonomics",
              "target_page": "/products/mice",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "sony wh-1000xm5 review vs bose",
              "search_volume": 18500,
              "cpc": 1.95,
              "competition": "Medium",
              "intent": "commercial",
              "category": "Audio & Headphones",
              "target_page": "/collections/audio",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "top noise cancelling headphones 2026",
              "search_volume": 29000,
              "cpc": 2.1,
              "competition": "High",
              "intent": "commercial",
              "category": "Audio & Headphones",
              "target_page": "/collections/audio",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "logitech support customer portal",
              "search_volume": 6200,
              "cpc": 0.3,
              "competition": "Low",
              "intent": "navigational",
              "category": "General Tech",
              "target_page": "/support",
              "priority": "LOW",
              "priority_reasoning": "Navigational or lower-volume informational discovery."
            },
            {
              "keyword": "purchase usb-c docking station 4k",
              "search_volume": 7800,
              "cpc": 2.8,
              "competition": "High",
              "intent": "transactional",
              "category": "Docks & Connectivity",
              "target_page": "/products/accessories",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "what is an ergonomic vertical mouse",
              "search_volume": 5100,
              "cpc": 0.5,
              "competition": "Low",
              "intent": "informational",
              "category": "Mice & Ergonomics",
              "target_page": "/guides/what-is-an-ergonomic-vertical-mouse",
              "priority": "LOW",
              "priority_reasoning": "Navigational or lower-volume informational discovery."
            }
          ],
          "high_priority_count": 6,
          "medium_priority_count": 2,
          "low_priority_count": 4,
          "summary": "Assigned priorities: 6 HIGH, 2 MEDIUM, 4 LOW."
        },
        "error": null
      },
      {
        "step_number": 6,
        "step_name": "export results",
        "status": "completed",
        "output_summary": "Successfully processed and classified 12 keyword(s). Found 6 high-priority keyword(s) for immediate content/landing page optimization.",
        "output": {
          "total_keywords": 12,
          "high_priority_count": 6,
          "medium_priority_count": 2,
          "low_priority_count": 4,
          "intent_counts": {
            "transactional": 3,
            "commercial": 4,
            "navigational": 2,
            "informational": 3
          },
          "category_counts": {
            "Keyboards & Input": 4,
            "Mice & Ergonomics": 3,
            "Office Furniture & Ergonomics": 1,
            "Audio & Headphones": 2,
            "General Tech": 1,
            "Docks & Connectivity": 1
          },
          "keyword_records": [
            {
              "keyword": "how to clean mechanical keyboard",
              "search_volume": 8500,
              "cpc": 0.45,
              "competition": "Low",
              "intent": "informational",
              "category": "Keyboards & Input",
              "target_page": "/guides/how-to-clean-mechanical-keyboard",
              "priority": "MEDIUM",
              "priority_reasoning": "Moderate consideration intent or substantial informational discovery volume."
            },
            {
              "keyword": "buy keychron k2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High",
              "intent": "transactional",
              "category": "Keyboards & Input",
              "target_page": "/products/keyboards",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "best mechanical keyboard for coding",
              "search_volume": 22000,
              "cpc": 1.8,
              "competition": "Medium",
              "intent": "commercial",
              "category": "Keyboards & Input",
              "target_page": "/collections/keyboards",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "logitech mx master 3s official website",
              "search_volume": 9800,
              "cpc": 0.85,
              "competition": "Low",
              "intent": "navigational",
              "category": "Mice & Ergonomics",
              "target_page": "/brand/mice",
              "priority": "LOW",
              "priority_reasoning": "Navigational or lower-volume informational discovery."
            },
            {
              "keyword": "keychron k2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High",
              "intent": "commercial",
              "category": "Keyboards & Input",
              "target_page": "/collections/keyboards",
              "priority": "MEDIUM",
              "priority_reasoning": "Moderate consideration intent or substantial informational discovery volume."
            },
            {
              "keyword": "ergonomic office chair setup guide",
              "search_volume": 4300,
              "cpc": 0.6,
              "competition": "Low",
              "intent": "informational",
              "category": "Office Furniture & Ergonomics",
              "target_page": "/guides/ergonomic-office-chair-setup-guide",
              "priority": "LOW",
              "priority_reasoning": "Navigational or lower-volume informational discovery."
            },
            {
              "keyword": "order logitech mx master 3s discount",
              "search_volume": 11000,
              "cpc": 2.4,
              "competition": "High",
              "intent": "transactional",
              "category": "Mice & Ergonomics",
              "target_page": "/products/mice",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "sony wh-1000xm5 review vs bose",
              "search_volume": 18500,
              "cpc": 1.95,
              "competition": "Medium",
              "intent": "commercial",
              "category": "Audio & Headphones",
              "target_page": "/collections/audio",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "top noise cancelling headphones 2026",
              "search_volume": 29000,
              "cpc": 2.1,
              "competition": "High",
              "intent": "commercial",
              "category": "Audio & Headphones",
              "target_page": "/collections/audio",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "logitech support customer portal",
              "search_volume": 6200,
              "cpc": 0.3,
              "competition": "Low",
              "intent": "navigational",
              "category": "General Tech",
              "target_page": "/support",
              "priority": "LOW",
              "priority_reasoning": "Navigational or lower-volume informational discovery."
            },
            {
              "keyword": "purchase usb-c docking station 4k",
              "search_volume": 7800,
              "cpc": 2.8,
              "competition": "High",
              "intent": "transactional",
              "category": "Docks & Connectivity",
              "target_page": "/products/accessories",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "what is an ergonomic vertical mouse",
              "search_volume": 5100,
              "cpc": 0.5,
              "competition": "Low",
              "intent": "informational",
              "category": "Mice & Ergonomics",
              "target_page": "/guides/what-is-an-ergonomic-vertical-mouse",
              "priority": "LOW",
              "priority_reasoning": "Navigational or lower-volume informational discovery."
            }
          ],
          "high_priority_recommendations": [
            {
              "keyword": "buy keychron k2 wireless",
              "search_volume": 14200,
              "cpc": 2.15,
              "competition": "High",
              "intent": "transactional",
              "category": "Keyboards & Input",
              "target_page": "/products/keyboards",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "best mechanical keyboard for coding",
              "search_volume": 22000,
              "cpc": 1.8,
              "competition": "Medium",
              "intent": "commercial",
              "category": "Keyboards & Input",
              "target_page": "/collections/keyboards",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "order logitech mx master 3s discount",
              "search_volume": 11000,
              "cpc": 2.4,
              "competition": "High",
              "intent": "transactional",
              "category": "Mice & Ergonomics",
              "target_page": "/products/mice",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "sony wh-1000xm5 review vs bose",
              "search_volume": 18500,
              "cpc": 1.95,
              "competition": "Medium",
              "intent": "commercial",
              "category": "Audio & Headphones",
              "target_page": "/collections/audio",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            },
            {
              "keyword": "top noise cancelling headphones 2026",
              "search_volume": 29000,
              "cpc": 2.1,
              "competition": "High",
              "intent": "commercial",
              "category": "Audio & Headphones",
              "target_page": "/collections/audio",
              "priority": "HIGH",
              "priority_reasoning": "High commercial conversion intent or high search volume."
            }
          ],
          "is_simulated": true,
          "summary": "Successfully processed and classified 12 keyword(s). Found 6 high-priority keyword(s) for immediate content/landing page optimization."
        },
        "error": null
      }
    ],
    "final_output": {
      "total_keywords": 12,
      "high_priority_count": 6,
      "medium_priority_count": 2,
      "low_priority_count": 4,
      "intent_counts": {
        "transactional": 3,
        "commercial": 4,
        "navigational": 2,
        "informational": 3
      },
      "category_counts": {
        "Keyboards & Input": 4,
        "Mice & Ergonomics": 3,
        "Office Furniture & Ergonomics": 1,
        "Audio & Headphones": 2,
        "General Tech": 1,
        "Docks & Connectivity": 1
      },
      "keyword_records": [
        {
          "keyword": "how to clean mechanical keyboard",
          "search_volume": 8500,
          "cpc": 0.45,
          "competition": "Low",
          "intent": "informational",
          "category": "Keyboards & Input",
          "target_page": "/guides/how-to-clean-mechanical-keyboard",
          "priority": "MEDIUM",
          "priority_reasoning": "Moderate consideration intent or substantial informational discovery volume."
        },
        {
          "keyword": "buy keychron k2 wireless",
          "search_volume": 14200,
          "cpc": 2.15,
          "competition": "High",
          "intent": "transactional",
          "category": "Keyboards & Input",
          "target_page": "/products/keyboards",
          "priority": "HIGH",
          "priority_reasoning": "High commercial conversion intent or high search volume."
        },
        {
          "keyword": "best mechanical keyboard for coding",
          "search_volume": 22000,
          "cpc": 1.8,
          "competition": "Medium",
          "intent": "commercial",
          "category": "Keyboards & Input",
          "target_page": "/collections/keyboards",
          "priority": "HIGH",
          "priority_reasoning": "High commercial conversion intent or high search volume."
        },
        {
          "keyword": "logitech mx master 3s official website",
          "search_volume": 9800,
          "cpc": 0.85,
          "competition": "Low",
          "intent": "navigational",
          "category": "Mice & Ergonomics",
          "target_page": "/brand/mice",
          "priority": "LOW",
          "priority_reasoning": "Navigational or lower-volume informational discovery."
        },
        {
          "keyword": "keychron k2 wireless",
          "search_volume": 14200,
          "cpc": 2.15,
          "competition": "High",
          "intent": "commercial",
          "category": "Keyboards & Input",
          "target_page": "/collections/keyboards",
          "priority": "MEDIUM",
          "priority_reasoning": "Moderate consideration intent or substantial informational discovery volume."
        },
        {
          "keyword": "ergonomic office chair setup guide",
          "search_volume": 4300,
          "cpc": 0.6,
          "competition": "Low",
          "intent": "informational",
          "category": "Office Furniture & Ergonomics",
          "target_page": "/guides/ergonomic-office-chair-setup-guide",
          "priority": "LOW",
          "priority_reasoning": "Navigational or lower-volume informational discovery."
        },
        {
          "keyword": "order logitech mx master 3s discount",
          "search_volume": 11000,
          "cpc": 2.4,
          "competition": "High",
          "intent": "transactional",
          "category": "Mice & Ergonomics",
          "target_page": "/products/mice",
          "priority": "HIGH",
          "priority_reasoning": "High commercial conversion intent or high search volume."
        },
        {
          "keyword": "sony wh-1000xm5 review vs bose",
          "search_volume": 18500,
          "cpc": 1.95,
          "competition": "Medium",
          "intent": "commercial",
          "category": "Audio & Headphones",
          "target_page": "/collections/audio",
          "priority": "HIGH",
          "priority_reasoning": "High commercial conversion intent or high search volume."
        },
        {
          "keyword": "top noise cancelling headphones 2026",
          "search_volume": 29000,
          "cpc": 2.1,
          "competition": "High",
          "intent": "commercial",
          "category": "Audio & Headphones",
          "target_page": "/collections/audio",
          "priority": "HIGH",
          "priority_reasoning": "High commercial conversion intent or high search volume."
        },
        {
          "keyword": "logitech support customer portal",
          "search_volume": 6200,
          "cpc": 0.3,
          "competition": "Low",
          "intent": "navigational",
          "category": "General Tech",
          "target_page": "/support",
          "priority": "LOW",
          "priority_reasoning": "Navigational or lower-volume informational discovery."
        },
        {
          "keyword": "purchase usb-c docking station 4k",
          "search_volume": 7800,
          "cpc": 2.8,
          "competition": "High",
          "intent": "transactional",
          "category": "Docks & Connectivity",
          "target_page": "/products/accessories",
          "priority": "HIGH",
          "priority_reasoning": "High commercial conversion intent or high search volume."
        },
        {
          "keyword": "what is an ergonomic vertical mouse",
          "search_volume": 5100,
          "cpc": 0.5,
          "competition": "Low",
          "intent": "informational",
          "category": "Mice & Ergonomics",
          "target_page": "/guides/what-is-an-ergonomic-vertical-mouse",
          "priority": "LOW",
          "priority_reasoning": "Navigational or lower-volume informational discovery."
        }
      ],
      "high_priority_recommendations": [
        {
          "keyword": "buy keychron k2 wireless",
          "search_volume": 14200,
          "cpc": 2.15,
          "competition": "High",
          "intent": "transactional",
          "category": "Keyboards & Input",
          "target_page": "/products/keyboards",
          "priority": "HIGH",
          "priority_reasoning": "High commercial conversion intent or high search volume."
        },
        {
          "keyword": "best mechanical keyboard for coding",
          "search_volume": 22000,
          "cpc": 1.8,
          "competition": "Medium",
          "intent": "commercial",
          "category": "Keyboards & Input",
          "target_page": "/collections/keyboards",
          "priority": "HIGH",
          "priority_reasoning": "High commercial conversion intent or high search volume."
        },
        {
          "keyword": "order logitech mx master 3s discount",
          "search_volume": 11000,
          "cpc": 2.4,
          "competition": "High",
          "intent": "transactional",
          "category": "Mice & Ergonomics",
          "target_page": "/products/mice",
          "priority": "HIGH",
          "priority_reasoning": "High commercial conversion intent or high search volume."
        },
        {
          "keyword": "sony wh-1000xm5 review vs bose",
          "search_volume": 18500,
          "cpc": 1.95,
          "competition": "Medium",
          "intent": "commercial",
          "category": "Audio & Headphones",
          "target_page": "/collections/audio",
          "priority": "HIGH",
          "priority_reasoning": "High commercial conversion intent or high search volume."
        },
        {
          "keyword": "top noise cancelling headphones 2026",
          "search_volume": 29000,
          "cpc": 2.1,
          "competition": "High",
          "intent": "commercial",
          "category": "Audio & Headphones",
          "target_page": "/collections/audio",
          "priority": "HIGH",
          "priority_reasoning": "High commercial conversion intent or high search volume."
        }
      ],
      "is_simulated": true,
      "summary": "Successfully processed and classified 12 keyword(s). Found 6 high-priority keyword(s) for immediate content/landing page optimization."
    },
    "errors": [],
    "clarification_required": false,
    "routing_mode": "offline",
    "warnings": []
  },
  "wf009_paraphrase": {
    "request": "Match this new task to an engineer based on skills and current capacity.",
    "selected_workflow_id": "WF009",
    "selected_workflow_name": "Employee Task Assignment",
    "routing_confidence": 0.85,
    "routing_reasoning": "Offline keyword match against trigger/metadata for WF009 (Employee Task Assignment): matched terms [current, employee, skill, task].",
    "status": "needs_clarification",
    "steps": [
      {
        "step_number": 1,
        "step_name": "Understand task requirements",
        "status": "needs_clarification",
        "output_summary": null,
        "output": null,
        "error": "Required input 'task_description' is missing. Please describe the task to assign."
      }
    ],
    "final_output": null,
    "errors": [
      "Required input 'task_description' is missing. Please describe the task to assign."
    ],
    "clarification_required": true,
    "routing_mode": "offline",
    "warnings": []
  },
  "wf009_task_assignment": {
    "request": "Assign this urgent task to the best available developer.",
    "selected_workflow_id": "WF009",
    "selected_workflow_name": "Employee Task Assignment",
    "routing_confidence": 0.8,
    "routing_reasoning": "Offline keyword match against trigger/metadata for WF009 (Employee Task Assignment): matched terms [assign, employee, task].",
    "status": "needs_clarification",
    "steps": [
      {
        "step_number": 1,
        "step_name": "Understand task requirements",
        "status": "needs_clarification",
        "output_summary": null,
        "output": null,
        "error": "Required input 'task_description' is missing. Please describe the task to assign."
      }
    ],
    "final_output": null,
    "errors": [
      "Required input 'task_description' is missing. Please describe the task to assign."
    ],
    "clarification_required": true,
    "routing_mode": "offline",
    "warnings": []
  },
  "wf010_paraphrase": {
    "request": "Show execution health report, error rates, and slowest steps across automated pipelines.",
    "selected_workflow_id": "WF010",
    "selected_workflow_name": "Workflow Performance Report",
    "routing_confidence": 0.9,
    "routing_reasoning": "Offline keyword match against trigger/metadata for WF010 (Workflow Performance Report): matched terms [error, perform, report, step, workflow].",
    "status": "success",
    "steps": [
      {
        "step_number": 1,
        "step_name": "Load execution logs",
        "status": "completed",
        "output_summary": "Loaded 39 workflow execution log record(s).",
        "output": {
          "raw_logs": [
            {
              "log_id": "LOG-1001",
              "workflow_id": "WF001",
              "workflow_name": "Inventory Restock Check",
              "step_name": "restock_reporter",
              "execution_time_seconds": 0.45,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T09:00:00Z"
            },
            {
              "log_id": "LOG-1002",
              "workflow_id": "WF001",
              "workflow_name": "Inventory Restock Check",
              "step_name": "restock_reporter",
              "execution_time_seconds": 0.52,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T09:15:00Z"
            },
            {
              "log_id": "LOG-1003",
              "workflow_id": "WF001",
              "workflow_name": "Inventory Restock Check",
              "step_name": "restock_reporter",
              "execution_time_seconds": 0.48,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T09:30:00Z"
            },
            {
              "log_id": "LOG-1004",
              "workflow_id": "WF001",
              "workflow_name": "Inventory Restock Check",
              "step_name": "restock_reporter",
              "execution_time_seconds": 0.61,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T10:00:00Z"
            },
            {
              "log_id": "LOG-1005",
              "workflow_id": "WF001",
              "workflow_name": "Inventory Restock Check",
              "step_name": "restock_reporter",
              "execution_time_seconds": 0.55,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T10:30:00Z"
            },
            {
              "log_id": "LOG-1006",
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_exception_flagger",
              "execution_time_seconds": 1.15,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T11:00:00Z"
            },
            {
              "log_id": "LOG-1007",
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_exception_flagger",
              "execution_time_seconds": 1.32,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T11:15:00Z"
            },
            {
              "log_id": "LOG-1008",
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_exception_flagger",
              "execution_time_seconds": 1.2,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T11:30:00Z"
            },
            {
              "log_id": "LOG-1009",
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_comparator",
              "execution_time_seconds": 1.1,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T11:45:00Z"
            },
            {
              "log_id": "LOG-1010",
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_exception_flagger",
              "execution_time_seconds": 1.25,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T12:00:00Z"
            },
            {
              "log_id": "LOG-1011",
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_exception_flagger",
              "execution_time_seconds": 1.4,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T12:15:00Z"
            },
            {
              "log_id": "LOG-1012",
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_exception_flagger",
              "execution_time_seconds": 1.18,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T12:30:00Z"
            },
            {
              "log_id": "LOG-1013",
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_exception_flagger",
              "execution_time_seconds": 1.22,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T12:45:00Z"
            },
            {
              "log_id": "LOG-1014",
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_exception_flagger",
              "execution_time_seconds": 1.3,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T13:00:00Z"
            },
            {
              "log_id": "LOG-1015",
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_data_loader",
              "execution_time_seconds": 0.95,
              "status": "FAILED",
              "error_message": "MissingColumnError: vendor_price column absent",
              "timestamp": "2026-10-10T13:15:00Z"
            },
            {
              "log_id": "LOG-1016",
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "execution_time_seconds": 6.8,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T14:00:00Z"
            },
            {
              "log_id": "LOG-1017",
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "execution_time_seconds": 7.2,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T14:15:00Z"
            },
            {
              "log_id": "LOG-1018",
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "execution_time_seconds": 6.1,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T14:30:00Z"
            },
            {
              "log_id": "LOG-1019",
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "vendor_file_reader",
              "execution_time_seconds": 1.8,
              "status": "FAILED",
              "error_message": "FormatError: Invalid CSV delimiter",
              "timestamp": "2026-10-10T14:45:00Z"
            },
            {
              "log_id": "LOG-1020",
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "execution_time_seconds": 8.5,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T15:00:00Z"
            },
            {
              "log_id": "LOG-1021",
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "execution_time_seconds": 6.9,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T15:15:00Z"
            },
            {
              "log_id": "LOG-1022",
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "execution_time_seconds": 5.9,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T15:30:00Z"
            },
            {
              "log_id": "LOG-1023",
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "vendor_file_reader",
              "execution_time_seconds": 1.75,
              "status": "FAILED",
              "error_message": "FormatError: Invalid CSV delimiter",
              "timestamp": "2026-10-10T15:45:00Z"
            },
            {
              "log_id": "LOG-1024",
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "execution_time_seconds": 6.4,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T16:00:00Z"
            },
            {
              "log_id": "LOG-1025",
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "execution_time_seconds": 7.1,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T16:15:00Z"
            },
            {
              "log_id": "LOG-1026",
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "execution_time_seconds": 9.1,
              "status": "FAILED",
              "error_message": "Timeout: file upload timeout after 9s",
              "timestamp": "2026-10-10T16:30:00Z"
            },
            {
              "log_id": "LOG-1027",
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "execution_time_seconds": 6.3,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T16:45:00Z"
            },
            {
              "log_id": "LOG-1028",
              "workflow_id": "WF004",
              "workflow_name": "Product Description Generator",
              "step_name": "meta_description_generator",
              "execution_time_seconds": 2.1,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T17:00:00Z"
            },
            {
              "log_id": "LOG-1029",
              "workflow_id": "WF004",
              "workflow_name": "Product Description Generator",
              "step_name": "meta_description_generator",
              "execution_time_seconds": 1.95,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T17:15:00Z"
            },
            {
              "log_id": "LOG-1030",
              "workflow_id": "WF004",
              "workflow_name": "Product Description Generator",
              "step_name": "meta_description_generator",
              "execution_time_seconds": 2.25,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T17:30:00Z"
            },
            {
              "log_id": "LOG-1031",
              "workflow_id": "WF005",
              "workflow_name": "Customer Order Status",
              "step_name": "order_status_summarizer",
              "execution_time_seconds": 0.75,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T18:00:00Z"
            },
            {
              "log_id": "LOG-1032",
              "workflow_id": "WF005",
              "workflow_name": "Customer Order Status",
              "step_name": "order_status_summarizer",
              "execution_time_seconds": 0.82,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T18:15:00Z"
            },
            {
              "log_id": "LOG-1033",
              "workflow_id": "WF005",
              "workflow_name": "Customer Order Status",
              "step_name": "order_status_summarizer",
              "execution_time_seconds": 0.78,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T18:30:00Z"
            },
            {
              "log_id": "LOG-1034",
              "workflow_id": "WF005",
              "workflow_name": "Customer Order Status",
              "step_name": "shipment_info_retriever",
              "execution_time_seconds": 1.9,
              "status": "FAILED",
              "error_message": "CarrierAPIError: Simulated carrier timeout",
              "timestamp": "2026-10-10T18:45:00Z"
            },
            {
              "log_id": "LOG-1035",
              "workflow_id": "WF005",
              "workflow_name": "Customer Order Status",
              "step_name": "order_status_summarizer",
              "execution_time_seconds": 0.85,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T19:00:00Z"
            },
            {
              "log_id": "LOG-1036",
              "workflow_id": "WF006",
              "workflow_name": "Duplicate Product Detection",
              "step_name": "duplicate_confidence_assigner",
              "execution_time_seconds": 3.1,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T19:15:00Z"
            },
            {
              "log_id": "LOG-1037",
              "workflow_id": "WF006",
              "workflow_name": "Duplicate Product Detection",
              "step_name": "duplicate_confidence_assigner",
              "execution_time_seconds": 3.4,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T19:30:00Z"
            },
            {
              "log_id": "LOG-1038",
              "workflow_id": "WF007",
              "workflow_name": "Marketing Campaign Brief",
              "step_name": "campaign_checklist_creator",
              "execution_time_seconds": 1.45,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T19:45:00Z"
            },
            {
              "log_id": "LOG-1039",
              "workflow_id": "WF007",
              "workflow_name": "Marketing Campaign Brief",
              "step_name": "campaign_checklist_creator",
              "execution_time_seconds": 1.55,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T20:00:00Z"
            }
          ],
          "total_logs": 39,
          "summary": "Loaded 39 workflow execution log record(s)."
        },
        "error": null
      },
      {
        "step_number": 2,
        "step_name": "calculate success/failure rate",
        "status": "completed",
        "output_summary": "Overall Success Rate: 87.2% (34/39), Failure Rate: 12.8% (5/39). Workflows exceeding 10.0% failure threshold: WF003, WF005.",
        "output": {
          "workflow_rates": {
            "WF001": {
              "workflow_id": "WF001",
              "workflow_name": "Inventory Restock Check",
              "total_runs": 5,
              "success_count": 5,
              "failure_count": 0,
              "success_rate_percent": 100.0,
              "failure_rate_percent": 0.0,
              "is_failure_flagged": false
            },
            "WF002": {
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "total_runs": 10,
              "success_count": 9,
              "failure_count": 1,
              "success_rate_percent": 90.0,
              "failure_rate_percent": 10.0,
              "is_failure_flagged": false
            },
            "WF003": {
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "total_runs": 12,
              "success_count": 9,
              "failure_count": 3,
              "success_rate_percent": 75.0,
              "failure_rate_percent": 25.0,
              "is_failure_flagged": true
            },
            "WF004": {
              "workflow_id": "WF004",
              "workflow_name": "Product Description Generator",
              "total_runs": 3,
              "success_count": 3,
              "failure_count": 0,
              "success_rate_percent": 100.0,
              "failure_rate_percent": 0.0,
              "is_failure_flagged": false
            },
            "WF005": {
              "workflow_id": "WF005",
              "workflow_name": "Customer Order Status",
              "total_runs": 5,
              "success_count": 4,
              "failure_count": 1,
              "success_rate_percent": 80.0,
              "failure_rate_percent": 20.0,
              "is_failure_flagged": true
            },
            "WF006": {
              "workflow_id": "WF006",
              "workflow_name": "Duplicate Product Detection",
              "total_runs": 2,
              "success_count": 2,
              "failure_count": 0,
              "success_rate_percent": 100.0,
              "failure_rate_percent": 0.0,
              "is_failure_flagged": false
            },
            "WF007": {
              "workflow_id": "WF007",
              "workflow_name": "Marketing Campaign Brief",
              "total_runs": 2,
              "success_count": 2,
              "failure_count": 0,
              "success_rate_percent": 100.0,
              "failure_rate_percent": 0.0,
              "is_failure_flagged": false
            }
          },
          "overall_success_rate": 87.2,
          "overall_failure_rate": 12.8,
          "flagged_high_failure_workflows": [
            "WF003",
            "WF005"
          ],
          "summary": "Overall Success Rate: 87.2% (34/39), Failure Rate: 12.8% (5/39). Workflows exceeding 10.0% failure threshold: WF003, WF005."
        },
        "error": null
      },
      {
        "step_number": 3,
        "step_name": "calculate average execution time",
        "status": "completed",
        "output_summary": "Overall Avg Execution Time: 2.81s. Workflows exceeding 5.0s threshold: WF003.",
        "output": {
          "workflow_times": {
            "WF001": {
              "workflow_id": "WF001",
              "workflow_name": "Inventory Restock Check",
              "avg_execution_time_seconds": 0.52,
              "min_execution_time_seconds": 0.45,
              "max_execution_time_seconds": 0.61,
              "is_slow_flagged": false
            },
            "WF002": {
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "avg_execution_time_seconds": 1.21,
              "min_execution_time_seconds": 0.95,
              "max_execution_time_seconds": 1.4,
              "is_slow_flagged": false
            },
            "WF003": {
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "avg_execution_time_seconds": 6.15,
              "min_execution_time_seconds": 1.75,
              "max_execution_time_seconds": 9.1,
              "is_slow_flagged": true
            },
            "WF004": {
              "workflow_id": "WF004",
              "workflow_name": "Product Description Generator",
              "avg_execution_time_seconds": 2.1,
              "min_execution_time_seconds": 1.95,
              "max_execution_time_seconds": 2.25,
              "is_slow_flagged": false
            },
            "WF005": {
              "workflow_id": "WF005",
              "workflow_name": "Customer Order Status",
              "avg_execution_time_seconds": 1.02,
              "min_execution_time_seconds": 0.75,
              "max_execution_time_seconds": 1.9,
              "is_slow_flagged": false
            },
            "WF006": {
              "workflow_id": "WF006",
              "workflow_name": "Duplicate Product Detection",
              "avg_execution_time_seconds": 3.25,
              "min_execution_time_seconds": 3.1,
              "max_execution_time_seconds": 3.4,
              "is_slow_flagged": false
            },
            "WF007": {
              "workflow_id": "WF007",
              "workflow_name": "Marketing Campaign Brief",
              "avg_execution_time_seconds": 1.5,
              "min_execution_time_seconds": 1.45,
              "max_execution_time_seconds": 1.55,
              "is_slow_flagged": false
            }
          },
          "overall_avg_time": 2.81,
          "flagged_slow_workflows": [
            "WF003"
          ],
          "summary": "Overall Avg Execution Time: 2.81s. Workflows exceeding 5.0s threshold: WF003."
        },
        "error": null
      },
      {
        "step_number": 4,
        "step_name": "identify frequent errors",
        "status": "completed",
        "output_summary": "Identified 5 failure(s) across 4 distinct error type(s).",
        "output": {
          "frequent_errors": [
            {
              "error_message": "FormatError: Invalid CSV delimiter",
              "count": 2,
              "affected_workflows": [
                "WF003"
              ]
            },
            {
              "error_message": "MissingColumnError: vendor_price column absent",
              "count": 1,
              "affected_workflows": [
                "WF002"
              ]
            },
            {
              "error_message": "Timeout: file upload timeout after 9s",
              "count": 1,
              "affected_workflows": [
                "WF003"
              ]
            },
            {
              "error_message": "CarrierAPIError: Simulated carrier timeout",
              "count": 1,
              "affected_workflows": [
                "WF005"
              ]
            }
          ],
          "total_errors_found": 5,
          "summary": "Identified 5 failure(s) across 4 distinct error type(s)."
        },
        "error": null
      },
      {
        "step_number": 5,
        "step_name": "identify slow steps",
        "status": "completed",
        "output_summary": "Identified 1 step(s) with average latency exceeding 4.0s.",
        "output": {
          "slow_steps": [
            {
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "run_count": 10,
              "avg_time_seconds": 7.03,
              "max_time_seconds": 9.1,
              "is_slow": true
            },
            {
              "workflow_id": "WF006",
              "workflow_name": "Duplicate Product Detection",
              "step_name": "duplicate_confidence_assigner",
              "run_count": 2,
              "avg_time_seconds": 3.25,
              "max_time_seconds": 3.4,
              "is_slow": false
            },
            {
              "workflow_id": "WF004",
              "workflow_name": "Product Description Generator",
              "step_name": "meta_description_generator",
              "run_count": 3,
              "avg_time_seconds": 2.1,
              "max_time_seconds": 2.25,
              "is_slow": false
            },
            {
              "workflow_id": "WF005",
              "workflow_name": "Customer Order Status",
              "step_name": "shipment_info_retriever",
              "run_count": 1,
              "avg_time_seconds": 1.9,
              "max_time_seconds": 1.9,
              "is_slow": false
            },
            {
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "vendor_file_reader",
              "run_count": 2,
              "avg_time_seconds": 1.77,
              "max_time_seconds": 1.8,
              "is_slow": false
            },
            {
              "workflow_id": "WF007",
              "workflow_name": "Marketing Campaign Brief",
              "step_name": "campaign_checklist_creator",
              "run_count": 2,
              "avg_time_seconds": 1.5,
              "max_time_seconds": 1.55,
              "is_slow": false
            },
            {
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_exception_flagger",
              "run_count": 8,
              "avg_time_seconds": 1.25,
              "max_time_seconds": 1.4,
              "is_slow": false
            },
            {
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_comparator",
              "run_count": 1,
              "avg_time_seconds": 1.1,
              "max_time_seconds": 1.1,
              "is_slow": false
            },
            {
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_data_loader",
              "run_count": 1,
              "avg_time_seconds": 0.95,
              "max_time_seconds": 0.95,
              "is_slow": false
            },
            {
              "workflow_id": "WF005",
              "workflow_name": "Customer Order Status",
              "step_name": "order_status_summarizer",
              "run_count": 4,
              "avg_time_seconds": 0.8,
              "max_time_seconds": 0.85,
              "is_slow": false
            },
            {
              "workflow_id": "WF001",
              "workflow_name": "Inventory Restock Check",
              "step_name": "restock_reporter",
              "run_count": 5,
              "avg_time_seconds": 0.52,
              "max_time_seconds": 0.61,
              "is_slow": false
            }
          ],
          "flagged_slow_steps": [
            {
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "run_count": 10,
              "avg_time_seconds": 7.03,
              "max_time_seconds": 9.1,
              "is_slow": true
            }
          ],
          "summary": "Identified 1 step(s) with average latency exceeding 4.0s."
        },
        "error": null
      },
      {
        "step_number": 6,
        "step_name": "generate recommendations",
        "status": "completed",
        "output_summary": "Generated 5 recommendation(s) across 7 monitored workflow(s). Flagged 2 high-failure workflow(s) and 1 slow workflow(s).",
        "output": {
          "overall_metrics": {
            "success_rate_percent": 87.2,
            "failure_rate_percent": 12.8,
            "avg_execution_time_seconds": 2.81,
            "total_workflows_monitored": 7
          },
          "workflow_performance": {
            "WF001": {
              "workflow_id": "WF001",
              "workflow_name": "Inventory Restock Check",
              "total_runs": 5,
              "success_count": 5,
              "failure_count": 0,
              "success_rate_percent": 100.0,
              "failure_rate_percent": 0.0,
              "is_failure_flagged": false
            },
            "WF002": {
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "total_runs": 10,
              "success_count": 9,
              "failure_count": 1,
              "success_rate_percent": 90.0,
              "failure_rate_percent": 10.0,
              "is_failure_flagged": false
            },
            "WF003": {
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "total_runs": 12,
              "success_count": 9,
              "failure_count": 3,
              "success_rate_percent": 75.0,
              "failure_rate_percent": 25.0,
              "is_failure_flagged": true
            },
            "WF004": {
              "workflow_id": "WF004",
              "workflow_name": "Product Description Generator",
              "total_runs": 3,
              "success_count": 3,
              "failure_count": 0,
              "success_rate_percent": 100.0,
              "failure_rate_percent": 0.0,
              "is_failure_flagged": false
            },
            "WF005": {
              "workflow_id": "WF005",
              "workflow_name": "Customer Order Status",
              "total_runs": 5,
              "success_count": 4,
              "failure_count": 1,
              "success_rate_percent": 80.0,
              "failure_rate_percent": 20.0,
              "is_failure_flagged": true
            },
            "WF006": {
              "workflow_id": "WF006",
              "workflow_name": "Duplicate Product Detection",
              "total_runs": 2,
              "success_count": 2,
              "failure_count": 0,
              "success_rate_percent": 100.0,
              "failure_rate_percent": 0.0,
              "is_failure_flagged": false
            },
            "WF007": {
              "workflow_id": "WF007",
              "workflow_name": "Marketing Campaign Brief",
              "total_runs": 2,
              "success_count": 2,
              "failure_count": 0,
              "success_rate_percent": 100.0,
              "failure_rate_percent": 0.0,
              "is_failure_flagged": false
            }
          },
          "workflow_timings": {
            "WF001": {
              "workflow_id": "WF001",
              "workflow_name": "Inventory Restock Check",
              "avg_execution_time_seconds": 0.52,
              "min_execution_time_seconds": 0.45,
              "max_execution_time_seconds": 0.61,
              "is_slow_flagged": false
            },
            "WF002": {
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "avg_execution_time_seconds": 1.21,
              "min_execution_time_seconds": 0.95,
              "max_execution_time_seconds": 1.4,
              "is_slow_flagged": false
            },
            "WF003": {
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "avg_execution_time_seconds": 6.15,
              "min_execution_time_seconds": 1.75,
              "max_execution_time_seconds": 9.1,
              "is_slow_flagged": true
            },
            "WF004": {
              "workflow_id": "WF004",
              "workflow_name": "Product Description Generator",
              "avg_execution_time_seconds": 2.1,
              "min_execution_time_seconds": 1.95,
              "max_execution_time_seconds": 2.25,
              "is_slow_flagged": false
            },
            "WF005": {
              "workflow_id": "WF005",
              "workflow_name": "Customer Order Status",
              "avg_execution_time_seconds": 1.02,
              "min_execution_time_seconds": 0.75,
              "max_execution_time_seconds": 1.9,
              "is_slow_flagged": false
            },
            "WF006": {
              "workflow_id": "WF006",
              "workflow_name": "Duplicate Product Detection",
              "avg_execution_time_seconds": 3.25,
              "min_execution_time_seconds": 3.1,
              "max_execution_time_seconds": 3.4,
              "is_slow_flagged": false
            },
            "WF007": {
              "workflow_id": "WF007",
              "workflow_name": "Marketing Campaign Brief",
              "avg_execution_time_seconds": 1.5,
              "min_execution_time_seconds": 1.45,
              "max_execution_time_seconds": 1.55,
              "is_slow_flagged": false
            }
          },
          "flagged_high_failure_workflows": [
            "WF003",
            "WF005"
          ],
          "flagged_slow_workflows": [
            "WF003"
          ],
          "frequent_errors": [
            {
              "error_message": "FormatError: Invalid CSV delimiter",
              "count": 2,
              "affected_workflows": [
                "WF003"
              ]
            },
            {
              "error_message": "MissingColumnError: vendor_price column absent",
              "count": 1,
              "affected_workflows": [
                "WF002"
              ]
            },
            {
              "error_message": "Timeout: file upload timeout after 9s",
              "count": 1,
              "affected_workflows": [
                "WF003"
              ]
            },
            {
              "error_message": "CarrierAPIError: Simulated carrier timeout",
              "count": 1,
              "affected_workflows": [
                "WF005"
              ]
            }
          ],
          "slow_steps": [
            {
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "run_count": 10,
              "avg_time_seconds": 7.03,
              "max_time_seconds": 9.1,
              "is_slow": true
            }
          ],
          "recommendations": [
            {
              "category": "RELIABILITY",
              "workflow_id": "WF003",
              "priority": "HIGH",
              "finding": "WF003 (Vendor File Processing) has an elevated failure rate of 25.0% (Threshold: 10.0%).",
              "action": "Implement retry policies, strict schema validation, or robust error recovery in WF003."
            },
            {
              "category": "RELIABILITY",
              "workflow_id": "WF005",
              "priority": "HIGH",
              "finding": "WF005 (Customer Order Status) has an elevated failure rate of 20.0% (Threshold: 10.0%).",
              "action": "Implement retry policies, strict schema validation, or robust error recovery in WF005."
            },
            {
              "category": "PERFORMANCE",
              "workflow_id": "WF003",
              "priority": "MEDIUM",
              "finding": "WF003 (Vendor File Processing) average execution time is 6.15s (Threshold: 5.0s).",
              "action": "Profile step execution in WF003, optimize file streaming, or add caching for repetitive operations."
            },
            {
              "category": "ERROR_MITIGATION",
              "workflow_id": "WF003",
              "priority": "HIGH",
              "finding": "Top error (2 occurrences): 'FormatError: Invalid CSV delimiter'.",
              "action": "Add upstream input sanitization or fallback handling for this error type."
            },
            {
              "category": "BOTTLENECK_OPTIMIZATION",
              "workflow_id": "WF003",
              "priority": "MEDIUM",
              "finding": "Step 'clean_dataset_producer' in WF003 averages 7.03s.",
              "action": "Refactor I/O or parallelize chunk processing to reduce latency."
            }
          ],
          "is_simulated": true,
          "summary": "Generated 5 recommendation(s) across 7 monitored workflow(s). Flagged 2 high-failure workflow(s) and 1 slow workflow(s)."
        },
        "error": null
      }
    ],
    "final_output": {
      "overall_metrics": {
        "success_rate_percent": 87.2,
        "failure_rate_percent": 12.8,
        "avg_execution_time_seconds": 2.81,
        "total_workflows_monitored": 7
      },
      "workflow_performance": {
        "WF001": {
          "workflow_id": "WF001",
          "workflow_name": "Inventory Restock Check",
          "total_runs": 5,
          "success_count": 5,
          "failure_count": 0,
          "success_rate_percent": 100.0,
          "failure_rate_percent": 0.0,
          "is_failure_flagged": false
        },
        "WF002": {
          "workflow_id": "WF002",
          "workflow_name": "Product Price Validation",
          "total_runs": 10,
          "success_count": 9,
          "failure_count": 1,
          "success_rate_percent": 90.0,
          "failure_rate_percent": 10.0,
          "is_failure_flagged": false
        },
        "WF003": {
          "workflow_id": "WF003",
          "workflow_name": "Vendor File Processing",
          "total_runs": 12,
          "success_count": 9,
          "failure_count": 3,
          "success_rate_percent": 75.0,
          "failure_rate_percent": 25.0,
          "is_failure_flagged": true
        },
        "WF004": {
          "workflow_id": "WF004",
          "workflow_name": "Product Description Generator",
          "total_runs": 3,
          "success_count": 3,
          "failure_count": 0,
          "success_rate_percent": 100.0,
          "failure_rate_percent": 0.0,
          "is_failure_flagged": false
        },
        "WF005": {
          "workflow_id": "WF005",
          "workflow_name": "Customer Order Status",
          "total_runs": 5,
          "success_count": 4,
          "failure_count": 1,
          "success_rate_percent": 80.0,
          "failure_rate_percent": 20.0,
          "is_failure_flagged": true
        },
        "WF006": {
          "workflow_id": "WF006",
          "workflow_name": "Duplicate Product Detection",
          "total_runs": 2,
          "success_count": 2,
          "failure_count": 0,
          "success_rate_percent": 100.0,
          "failure_rate_percent": 0.0,
          "is_failure_flagged": false
        },
        "WF007": {
          "workflow_id": "WF007",
          "workflow_name": "Marketing Campaign Brief",
          "total_runs": 2,
          "success_count": 2,
          "failure_count": 0,
          "success_rate_percent": 100.0,
          "failure_rate_percent": 0.0,
          "is_failure_flagged": false
        }
      },
      "workflow_timings": {
        "WF001": {
          "workflow_id": "WF001",
          "workflow_name": "Inventory Restock Check",
          "avg_execution_time_seconds": 0.52,
          "min_execution_time_seconds": 0.45,
          "max_execution_time_seconds": 0.61,
          "is_slow_flagged": false
        },
        "WF002": {
          "workflow_id": "WF002",
          "workflow_name": "Product Price Validation",
          "avg_execution_time_seconds": 1.21,
          "min_execution_time_seconds": 0.95,
          "max_execution_time_seconds": 1.4,
          "is_slow_flagged": false
        },
        "WF003": {
          "workflow_id": "WF003",
          "workflow_name": "Vendor File Processing",
          "avg_execution_time_seconds": 6.15,
          "min_execution_time_seconds": 1.75,
          "max_execution_time_seconds": 9.1,
          "is_slow_flagged": true
        },
        "WF004": {
          "workflow_id": "WF004",
          "workflow_name": "Product Description Generator",
          "avg_execution_time_seconds": 2.1,
          "min_execution_time_seconds": 1.95,
          "max_execution_time_seconds": 2.25,
          "is_slow_flagged": false
        },
        "WF005": {
          "workflow_id": "WF005",
          "workflow_name": "Customer Order Status",
          "avg_execution_time_seconds": 1.02,
          "min_execution_time_seconds": 0.75,
          "max_execution_time_seconds": 1.9,
          "is_slow_flagged": false
        },
        "WF006": {
          "workflow_id": "WF006",
          "workflow_name": "Duplicate Product Detection",
          "avg_execution_time_seconds": 3.25,
          "min_execution_time_seconds": 3.1,
          "max_execution_time_seconds": 3.4,
          "is_slow_flagged": false
        },
        "WF007": {
          "workflow_id": "WF007",
          "workflow_name": "Marketing Campaign Brief",
          "avg_execution_time_seconds": 1.5,
          "min_execution_time_seconds": 1.45,
          "max_execution_time_seconds": 1.55,
          "is_slow_flagged": false
        }
      },
      "flagged_high_failure_workflows": [
        "WF003",
        "WF005"
      ],
      "flagged_slow_workflows": [
        "WF003"
      ],
      "frequent_errors": [
        {
          "error_message": "FormatError: Invalid CSV delimiter",
          "count": 2,
          "affected_workflows": [
            "WF003"
          ]
        },
        {
          "error_message": "MissingColumnError: vendor_price column absent",
          "count": 1,
          "affected_workflows": [
            "WF002"
          ]
        },
        {
          "error_message": "Timeout: file upload timeout after 9s",
          "count": 1,
          "affected_workflows": [
            "WF003"
          ]
        },
        {
          "error_message": "CarrierAPIError: Simulated carrier timeout",
          "count": 1,
          "affected_workflows": [
            "WF005"
          ]
        }
      ],
      "slow_steps": [
        {
          "workflow_id": "WF003",
          "workflow_name": "Vendor File Processing",
          "step_name": "clean_dataset_producer",
          "run_count": 10,
          "avg_time_seconds": 7.03,
          "max_time_seconds": 9.1,
          "is_slow": true
        }
      ],
      "recommendations": [
        {
          "category": "RELIABILITY",
          "workflow_id": "WF003",
          "priority": "HIGH",
          "finding": "WF003 (Vendor File Processing) has an elevated failure rate of 25.0% (Threshold: 10.0%).",
          "action": "Implement retry policies, strict schema validation, or robust error recovery in WF003."
        },
        {
          "category": "RELIABILITY",
          "workflow_id": "WF005",
          "priority": "HIGH",
          "finding": "WF005 (Customer Order Status) has an elevated failure rate of 20.0% (Threshold: 10.0%).",
          "action": "Implement retry policies, strict schema validation, or robust error recovery in WF005."
        },
        {
          "category": "PERFORMANCE",
          "workflow_id": "WF003",
          "priority": "MEDIUM",
          "finding": "WF003 (Vendor File Processing) average execution time is 6.15s (Threshold: 5.0s).",
          "action": "Profile step execution in WF003, optimize file streaming, or add caching for repetitive operations."
        },
        {
          "category": "ERROR_MITIGATION",
          "workflow_id": "WF003",
          "priority": "HIGH",
          "finding": "Top error (2 occurrences): 'FormatError: Invalid CSV delimiter'.",
          "action": "Add upstream input sanitization or fallback handling for this error type."
        },
        {
          "category": "BOTTLENECK_OPTIMIZATION",
          "workflow_id": "WF003",
          "priority": "MEDIUM",
          "finding": "Step 'clean_dataset_producer' in WF003 averages 7.03s.",
          "action": "Refactor I/O or parallelize chunk processing to reduce latency."
        }
      ],
      "is_simulated": true,
      "summary": "Generated 5 recommendation(s) across 7 monitored workflow(s). Flagged 2 high-failure workflow(s) and 1 slow workflow(s)."
    },
    "errors": [],
    "clarification_required": false,
    "routing_mode": "offline",
    "warnings": []
  },
  "wf010_performance_report": {
    "request": "Which workflows are failing most often?",
    "selected_workflow_id": "WF010",
    "selected_workflow_name": "Workflow Performance Report",
    "routing_confidence": 0.75,
    "routing_reasoning": "Offline keyword match against trigger/metadata for WF010 (Workflow Performance Report): matched terms [fail, workflow].",
    "status": "success",
    "steps": [
      {
        "step_number": 1,
        "step_name": "Load execution logs",
        "status": "completed",
        "output_summary": "Loaded 39 workflow execution log record(s).",
        "output": {
          "raw_logs": [
            {
              "log_id": "LOG-1001",
              "workflow_id": "WF001",
              "workflow_name": "Inventory Restock Check",
              "step_name": "restock_reporter",
              "execution_time_seconds": 0.45,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T09:00:00Z"
            },
            {
              "log_id": "LOG-1002",
              "workflow_id": "WF001",
              "workflow_name": "Inventory Restock Check",
              "step_name": "restock_reporter",
              "execution_time_seconds": 0.52,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T09:15:00Z"
            },
            {
              "log_id": "LOG-1003",
              "workflow_id": "WF001",
              "workflow_name": "Inventory Restock Check",
              "step_name": "restock_reporter",
              "execution_time_seconds": 0.48,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T09:30:00Z"
            },
            {
              "log_id": "LOG-1004",
              "workflow_id": "WF001",
              "workflow_name": "Inventory Restock Check",
              "step_name": "restock_reporter",
              "execution_time_seconds": 0.61,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T10:00:00Z"
            },
            {
              "log_id": "LOG-1005",
              "workflow_id": "WF001",
              "workflow_name": "Inventory Restock Check",
              "step_name": "restock_reporter",
              "execution_time_seconds": 0.55,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T10:30:00Z"
            },
            {
              "log_id": "LOG-1006",
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_exception_flagger",
              "execution_time_seconds": 1.15,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T11:00:00Z"
            },
            {
              "log_id": "LOG-1007",
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_exception_flagger",
              "execution_time_seconds": 1.32,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T11:15:00Z"
            },
            {
              "log_id": "LOG-1008",
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_exception_flagger",
              "execution_time_seconds": 1.2,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T11:30:00Z"
            },
            {
              "log_id": "LOG-1009",
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_comparator",
              "execution_time_seconds": 1.1,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T11:45:00Z"
            },
            {
              "log_id": "LOG-1010",
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_exception_flagger",
              "execution_time_seconds": 1.25,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T12:00:00Z"
            },
            {
              "log_id": "LOG-1011",
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_exception_flagger",
              "execution_time_seconds": 1.4,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T12:15:00Z"
            },
            {
              "log_id": "LOG-1012",
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_exception_flagger",
              "execution_time_seconds": 1.18,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T12:30:00Z"
            },
            {
              "log_id": "LOG-1013",
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_exception_flagger",
              "execution_time_seconds": 1.22,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T12:45:00Z"
            },
            {
              "log_id": "LOG-1014",
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_exception_flagger",
              "execution_time_seconds": 1.3,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T13:00:00Z"
            },
            {
              "log_id": "LOG-1015",
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_data_loader",
              "execution_time_seconds": 0.95,
              "status": "FAILED",
              "error_message": "MissingColumnError: vendor_price column absent",
              "timestamp": "2026-10-10T13:15:00Z"
            },
            {
              "log_id": "LOG-1016",
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "execution_time_seconds": 6.8,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T14:00:00Z"
            },
            {
              "log_id": "LOG-1017",
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "execution_time_seconds": 7.2,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T14:15:00Z"
            },
            {
              "log_id": "LOG-1018",
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "execution_time_seconds": 6.1,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T14:30:00Z"
            },
            {
              "log_id": "LOG-1019",
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "vendor_file_reader",
              "execution_time_seconds": 1.8,
              "status": "FAILED",
              "error_message": "FormatError: Invalid CSV delimiter",
              "timestamp": "2026-10-10T14:45:00Z"
            },
            {
              "log_id": "LOG-1020",
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "execution_time_seconds": 8.5,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T15:00:00Z"
            },
            {
              "log_id": "LOG-1021",
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "execution_time_seconds": 6.9,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T15:15:00Z"
            },
            {
              "log_id": "LOG-1022",
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "execution_time_seconds": 5.9,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T15:30:00Z"
            },
            {
              "log_id": "LOG-1023",
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "vendor_file_reader",
              "execution_time_seconds": 1.75,
              "status": "FAILED",
              "error_message": "FormatError: Invalid CSV delimiter",
              "timestamp": "2026-10-10T15:45:00Z"
            },
            {
              "log_id": "LOG-1024",
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "execution_time_seconds": 6.4,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T16:00:00Z"
            },
            {
              "log_id": "LOG-1025",
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "execution_time_seconds": 7.1,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T16:15:00Z"
            },
            {
              "log_id": "LOG-1026",
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "execution_time_seconds": 9.1,
              "status": "FAILED",
              "error_message": "Timeout: file upload timeout after 9s",
              "timestamp": "2026-10-10T16:30:00Z"
            },
            {
              "log_id": "LOG-1027",
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "execution_time_seconds": 6.3,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T16:45:00Z"
            },
            {
              "log_id": "LOG-1028",
              "workflow_id": "WF004",
              "workflow_name": "Product Description Generator",
              "step_name": "meta_description_generator",
              "execution_time_seconds": 2.1,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T17:00:00Z"
            },
            {
              "log_id": "LOG-1029",
              "workflow_id": "WF004",
              "workflow_name": "Product Description Generator",
              "step_name": "meta_description_generator",
              "execution_time_seconds": 1.95,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T17:15:00Z"
            },
            {
              "log_id": "LOG-1030",
              "workflow_id": "WF004",
              "workflow_name": "Product Description Generator",
              "step_name": "meta_description_generator",
              "execution_time_seconds": 2.25,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T17:30:00Z"
            },
            {
              "log_id": "LOG-1031",
              "workflow_id": "WF005",
              "workflow_name": "Customer Order Status",
              "step_name": "order_status_summarizer",
              "execution_time_seconds": 0.75,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T18:00:00Z"
            },
            {
              "log_id": "LOG-1032",
              "workflow_id": "WF005",
              "workflow_name": "Customer Order Status",
              "step_name": "order_status_summarizer",
              "execution_time_seconds": 0.82,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T18:15:00Z"
            },
            {
              "log_id": "LOG-1033",
              "workflow_id": "WF005",
              "workflow_name": "Customer Order Status",
              "step_name": "order_status_summarizer",
              "execution_time_seconds": 0.78,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T18:30:00Z"
            },
            {
              "log_id": "LOG-1034",
              "workflow_id": "WF005",
              "workflow_name": "Customer Order Status",
              "step_name": "shipment_info_retriever",
              "execution_time_seconds": 1.9,
              "status": "FAILED",
              "error_message": "CarrierAPIError: Simulated carrier timeout",
              "timestamp": "2026-10-10T18:45:00Z"
            },
            {
              "log_id": "LOG-1035",
              "workflow_id": "WF005",
              "workflow_name": "Customer Order Status",
              "step_name": "order_status_summarizer",
              "execution_time_seconds": 0.85,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T19:00:00Z"
            },
            {
              "log_id": "LOG-1036",
              "workflow_id": "WF006",
              "workflow_name": "Duplicate Product Detection",
              "step_name": "duplicate_confidence_assigner",
              "execution_time_seconds": 3.1,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T19:15:00Z"
            },
            {
              "log_id": "LOG-1037",
              "workflow_id": "WF006",
              "workflow_name": "Duplicate Product Detection",
              "step_name": "duplicate_confidence_assigner",
              "execution_time_seconds": 3.4,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T19:30:00Z"
            },
            {
              "log_id": "LOG-1038",
              "workflow_id": "WF007",
              "workflow_name": "Marketing Campaign Brief",
              "step_name": "campaign_checklist_creator",
              "execution_time_seconds": 1.45,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T19:45:00Z"
            },
            {
              "log_id": "LOG-1039",
              "workflow_id": "WF007",
              "workflow_name": "Marketing Campaign Brief",
              "step_name": "campaign_checklist_creator",
              "execution_time_seconds": 1.55,
              "status": "SUCCESS",
              "error_message": "",
              "timestamp": "2026-10-10T20:00:00Z"
            }
          ],
          "total_logs": 39,
          "summary": "Loaded 39 workflow execution log record(s)."
        },
        "error": null
      },
      {
        "step_number": 2,
        "step_name": "calculate success/failure rate",
        "status": "completed",
        "output_summary": "Overall Success Rate: 87.2% (34/39), Failure Rate: 12.8% (5/39). Workflows exceeding 10.0% failure threshold: WF003, WF005.",
        "output": {
          "workflow_rates": {
            "WF001": {
              "workflow_id": "WF001",
              "workflow_name": "Inventory Restock Check",
              "total_runs": 5,
              "success_count": 5,
              "failure_count": 0,
              "success_rate_percent": 100.0,
              "failure_rate_percent": 0.0,
              "is_failure_flagged": false
            },
            "WF002": {
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "total_runs": 10,
              "success_count": 9,
              "failure_count": 1,
              "success_rate_percent": 90.0,
              "failure_rate_percent": 10.0,
              "is_failure_flagged": false
            },
            "WF003": {
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "total_runs": 12,
              "success_count": 9,
              "failure_count": 3,
              "success_rate_percent": 75.0,
              "failure_rate_percent": 25.0,
              "is_failure_flagged": true
            },
            "WF004": {
              "workflow_id": "WF004",
              "workflow_name": "Product Description Generator",
              "total_runs": 3,
              "success_count": 3,
              "failure_count": 0,
              "success_rate_percent": 100.0,
              "failure_rate_percent": 0.0,
              "is_failure_flagged": false
            },
            "WF005": {
              "workflow_id": "WF005",
              "workflow_name": "Customer Order Status",
              "total_runs": 5,
              "success_count": 4,
              "failure_count": 1,
              "success_rate_percent": 80.0,
              "failure_rate_percent": 20.0,
              "is_failure_flagged": true
            },
            "WF006": {
              "workflow_id": "WF006",
              "workflow_name": "Duplicate Product Detection",
              "total_runs": 2,
              "success_count": 2,
              "failure_count": 0,
              "success_rate_percent": 100.0,
              "failure_rate_percent": 0.0,
              "is_failure_flagged": false
            },
            "WF007": {
              "workflow_id": "WF007",
              "workflow_name": "Marketing Campaign Brief",
              "total_runs": 2,
              "success_count": 2,
              "failure_count": 0,
              "success_rate_percent": 100.0,
              "failure_rate_percent": 0.0,
              "is_failure_flagged": false
            }
          },
          "overall_success_rate": 87.2,
          "overall_failure_rate": 12.8,
          "flagged_high_failure_workflows": [
            "WF003",
            "WF005"
          ],
          "summary": "Overall Success Rate: 87.2% (34/39), Failure Rate: 12.8% (5/39). Workflows exceeding 10.0% failure threshold: WF003, WF005."
        },
        "error": null
      },
      {
        "step_number": 3,
        "step_name": "calculate average execution time",
        "status": "completed",
        "output_summary": "Overall Avg Execution Time: 2.81s. Workflows exceeding 5.0s threshold: WF003.",
        "output": {
          "workflow_times": {
            "WF001": {
              "workflow_id": "WF001",
              "workflow_name": "Inventory Restock Check",
              "avg_execution_time_seconds": 0.52,
              "min_execution_time_seconds": 0.45,
              "max_execution_time_seconds": 0.61,
              "is_slow_flagged": false
            },
            "WF002": {
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "avg_execution_time_seconds": 1.21,
              "min_execution_time_seconds": 0.95,
              "max_execution_time_seconds": 1.4,
              "is_slow_flagged": false
            },
            "WF003": {
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "avg_execution_time_seconds": 6.15,
              "min_execution_time_seconds": 1.75,
              "max_execution_time_seconds": 9.1,
              "is_slow_flagged": true
            },
            "WF004": {
              "workflow_id": "WF004",
              "workflow_name": "Product Description Generator",
              "avg_execution_time_seconds": 2.1,
              "min_execution_time_seconds": 1.95,
              "max_execution_time_seconds": 2.25,
              "is_slow_flagged": false
            },
            "WF005": {
              "workflow_id": "WF005",
              "workflow_name": "Customer Order Status",
              "avg_execution_time_seconds": 1.02,
              "min_execution_time_seconds": 0.75,
              "max_execution_time_seconds": 1.9,
              "is_slow_flagged": false
            },
            "WF006": {
              "workflow_id": "WF006",
              "workflow_name": "Duplicate Product Detection",
              "avg_execution_time_seconds": 3.25,
              "min_execution_time_seconds": 3.1,
              "max_execution_time_seconds": 3.4,
              "is_slow_flagged": false
            },
            "WF007": {
              "workflow_id": "WF007",
              "workflow_name": "Marketing Campaign Brief",
              "avg_execution_time_seconds": 1.5,
              "min_execution_time_seconds": 1.45,
              "max_execution_time_seconds": 1.55,
              "is_slow_flagged": false
            }
          },
          "overall_avg_time": 2.81,
          "flagged_slow_workflows": [
            "WF003"
          ],
          "summary": "Overall Avg Execution Time: 2.81s. Workflows exceeding 5.0s threshold: WF003."
        },
        "error": null
      },
      {
        "step_number": 4,
        "step_name": "identify frequent errors",
        "status": "completed",
        "output_summary": "Identified 5 failure(s) across 4 distinct error type(s).",
        "output": {
          "frequent_errors": [
            {
              "error_message": "FormatError: Invalid CSV delimiter",
              "count": 2,
              "affected_workflows": [
                "WF003"
              ]
            },
            {
              "error_message": "MissingColumnError: vendor_price column absent",
              "count": 1,
              "affected_workflows": [
                "WF002"
              ]
            },
            {
              "error_message": "Timeout: file upload timeout after 9s",
              "count": 1,
              "affected_workflows": [
                "WF003"
              ]
            },
            {
              "error_message": "CarrierAPIError: Simulated carrier timeout",
              "count": 1,
              "affected_workflows": [
                "WF005"
              ]
            }
          ],
          "total_errors_found": 5,
          "summary": "Identified 5 failure(s) across 4 distinct error type(s)."
        },
        "error": null
      },
      {
        "step_number": 5,
        "step_name": "identify slow steps",
        "status": "completed",
        "output_summary": "Identified 1 step(s) with average latency exceeding 4.0s.",
        "output": {
          "slow_steps": [
            {
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "run_count": 10,
              "avg_time_seconds": 7.03,
              "max_time_seconds": 9.1,
              "is_slow": true
            },
            {
              "workflow_id": "WF006",
              "workflow_name": "Duplicate Product Detection",
              "step_name": "duplicate_confidence_assigner",
              "run_count": 2,
              "avg_time_seconds": 3.25,
              "max_time_seconds": 3.4,
              "is_slow": false
            },
            {
              "workflow_id": "WF004",
              "workflow_name": "Product Description Generator",
              "step_name": "meta_description_generator",
              "run_count": 3,
              "avg_time_seconds": 2.1,
              "max_time_seconds": 2.25,
              "is_slow": false
            },
            {
              "workflow_id": "WF005",
              "workflow_name": "Customer Order Status",
              "step_name": "shipment_info_retriever",
              "run_count": 1,
              "avg_time_seconds": 1.9,
              "max_time_seconds": 1.9,
              "is_slow": false
            },
            {
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "vendor_file_reader",
              "run_count": 2,
              "avg_time_seconds": 1.77,
              "max_time_seconds": 1.8,
              "is_slow": false
            },
            {
              "workflow_id": "WF007",
              "workflow_name": "Marketing Campaign Brief",
              "step_name": "campaign_checklist_creator",
              "run_count": 2,
              "avg_time_seconds": 1.5,
              "max_time_seconds": 1.55,
              "is_slow": false
            },
            {
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_exception_flagger",
              "run_count": 8,
              "avg_time_seconds": 1.25,
              "max_time_seconds": 1.4,
              "is_slow": false
            },
            {
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_comparator",
              "run_count": 1,
              "avg_time_seconds": 1.1,
              "max_time_seconds": 1.1,
              "is_slow": false
            },
            {
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "step_name": "price_data_loader",
              "run_count": 1,
              "avg_time_seconds": 0.95,
              "max_time_seconds": 0.95,
              "is_slow": false
            },
            {
              "workflow_id": "WF005",
              "workflow_name": "Customer Order Status",
              "step_name": "order_status_summarizer",
              "run_count": 4,
              "avg_time_seconds": 0.8,
              "max_time_seconds": 0.85,
              "is_slow": false
            },
            {
              "workflow_id": "WF001",
              "workflow_name": "Inventory Restock Check",
              "step_name": "restock_reporter",
              "run_count": 5,
              "avg_time_seconds": 0.52,
              "max_time_seconds": 0.61,
              "is_slow": false
            }
          ],
          "flagged_slow_steps": [
            {
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "run_count": 10,
              "avg_time_seconds": 7.03,
              "max_time_seconds": 9.1,
              "is_slow": true
            }
          ],
          "summary": "Identified 1 step(s) with average latency exceeding 4.0s."
        },
        "error": null
      },
      {
        "step_number": 6,
        "step_name": "generate recommendations",
        "status": "completed",
        "output_summary": "Generated 5 recommendation(s) across 7 monitored workflow(s). Flagged 2 high-failure workflow(s) and 1 slow workflow(s).",
        "output": {
          "overall_metrics": {
            "success_rate_percent": 87.2,
            "failure_rate_percent": 12.8,
            "avg_execution_time_seconds": 2.81,
            "total_workflows_monitored": 7
          },
          "workflow_performance": {
            "WF001": {
              "workflow_id": "WF001",
              "workflow_name": "Inventory Restock Check",
              "total_runs": 5,
              "success_count": 5,
              "failure_count": 0,
              "success_rate_percent": 100.0,
              "failure_rate_percent": 0.0,
              "is_failure_flagged": false
            },
            "WF002": {
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "total_runs": 10,
              "success_count": 9,
              "failure_count": 1,
              "success_rate_percent": 90.0,
              "failure_rate_percent": 10.0,
              "is_failure_flagged": false
            },
            "WF003": {
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "total_runs": 12,
              "success_count": 9,
              "failure_count": 3,
              "success_rate_percent": 75.0,
              "failure_rate_percent": 25.0,
              "is_failure_flagged": true
            },
            "WF004": {
              "workflow_id": "WF004",
              "workflow_name": "Product Description Generator",
              "total_runs": 3,
              "success_count": 3,
              "failure_count": 0,
              "success_rate_percent": 100.0,
              "failure_rate_percent": 0.0,
              "is_failure_flagged": false
            },
            "WF005": {
              "workflow_id": "WF005",
              "workflow_name": "Customer Order Status",
              "total_runs": 5,
              "success_count": 4,
              "failure_count": 1,
              "success_rate_percent": 80.0,
              "failure_rate_percent": 20.0,
              "is_failure_flagged": true
            },
            "WF006": {
              "workflow_id": "WF006",
              "workflow_name": "Duplicate Product Detection",
              "total_runs": 2,
              "success_count": 2,
              "failure_count": 0,
              "success_rate_percent": 100.0,
              "failure_rate_percent": 0.0,
              "is_failure_flagged": false
            },
            "WF007": {
              "workflow_id": "WF007",
              "workflow_name": "Marketing Campaign Brief",
              "total_runs": 2,
              "success_count": 2,
              "failure_count": 0,
              "success_rate_percent": 100.0,
              "failure_rate_percent": 0.0,
              "is_failure_flagged": false
            }
          },
          "workflow_timings": {
            "WF001": {
              "workflow_id": "WF001",
              "workflow_name": "Inventory Restock Check",
              "avg_execution_time_seconds": 0.52,
              "min_execution_time_seconds": 0.45,
              "max_execution_time_seconds": 0.61,
              "is_slow_flagged": false
            },
            "WF002": {
              "workflow_id": "WF002",
              "workflow_name": "Product Price Validation",
              "avg_execution_time_seconds": 1.21,
              "min_execution_time_seconds": 0.95,
              "max_execution_time_seconds": 1.4,
              "is_slow_flagged": false
            },
            "WF003": {
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "avg_execution_time_seconds": 6.15,
              "min_execution_time_seconds": 1.75,
              "max_execution_time_seconds": 9.1,
              "is_slow_flagged": true
            },
            "WF004": {
              "workflow_id": "WF004",
              "workflow_name": "Product Description Generator",
              "avg_execution_time_seconds": 2.1,
              "min_execution_time_seconds": 1.95,
              "max_execution_time_seconds": 2.25,
              "is_slow_flagged": false
            },
            "WF005": {
              "workflow_id": "WF005",
              "workflow_name": "Customer Order Status",
              "avg_execution_time_seconds": 1.02,
              "min_execution_time_seconds": 0.75,
              "max_execution_time_seconds": 1.9,
              "is_slow_flagged": false
            },
            "WF006": {
              "workflow_id": "WF006",
              "workflow_name": "Duplicate Product Detection",
              "avg_execution_time_seconds": 3.25,
              "min_execution_time_seconds": 3.1,
              "max_execution_time_seconds": 3.4,
              "is_slow_flagged": false
            },
            "WF007": {
              "workflow_id": "WF007",
              "workflow_name": "Marketing Campaign Brief",
              "avg_execution_time_seconds": 1.5,
              "min_execution_time_seconds": 1.45,
              "max_execution_time_seconds": 1.55,
              "is_slow_flagged": false
            }
          },
          "flagged_high_failure_workflows": [
            "WF003",
            "WF005"
          ],
          "flagged_slow_workflows": [
            "WF003"
          ],
          "frequent_errors": [
            {
              "error_message": "FormatError: Invalid CSV delimiter",
              "count": 2,
              "affected_workflows": [
                "WF003"
              ]
            },
            {
              "error_message": "MissingColumnError: vendor_price column absent",
              "count": 1,
              "affected_workflows": [
                "WF002"
              ]
            },
            {
              "error_message": "Timeout: file upload timeout after 9s",
              "count": 1,
              "affected_workflows": [
                "WF003"
              ]
            },
            {
              "error_message": "CarrierAPIError: Simulated carrier timeout",
              "count": 1,
              "affected_workflows": [
                "WF005"
              ]
            }
          ],
          "slow_steps": [
            {
              "workflow_id": "WF003",
              "workflow_name": "Vendor File Processing",
              "step_name": "clean_dataset_producer",
              "run_count": 10,
              "avg_time_seconds": 7.03,
              "max_time_seconds": 9.1,
              "is_slow": true
            }
          ],
          "recommendations": [
            {
              "category": "RELIABILITY",
              "workflow_id": "WF003",
              "priority": "HIGH",
              "finding": "WF003 (Vendor File Processing) has an elevated failure rate of 25.0% (Threshold: 10.0%).",
              "action": "Implement retry policies, strict schema validation, or robust error recovery in WF003."
            },
            {
              "category": "RELIABILITY",
              "workflow_id": "WF005",
              "priority": "HIGH",
              "finding": "WF005 (Customer Order Status) has an elevated failure rate of 20.0% (Threshold: 10.0%).",
              "action": "Implement retry policies, strict schema validation, or robust error recovery in WF005."
            },
            {
              "category": "PERFORMANCE",
              "workflow_id": "WF003",
              "priority": "MEDIUM",
              "finding": "WF003 (Vendor File Processing) average execution time is 6.15s (Threshold: 5.0s).",
              "action": "Profile step execution in WF003, optimize file streaming, or add caching for repetitive operations."
            },
            {
              "category": "ERROR_MITIGATION",
              "workflow_id": "WF003",
              "priority": "HIGH",
              "finding": "Top error (2 occurrences): 'FormatError: Invalid CSV delimiter'.",
              "action": "Add upstream input sanitization or fallback handling for this error type."
            },
            {
              "category": "BOTTLENECK_OPTIMIZATION",
              "workflow_id": "WF003",
              "priority": "MEDIUM",
              "finding": "Step 'clean_dataset_producer' in WF003 averages 7.03s.",
              "action": "Refactor I/O or parallelize chunk processing to reduce latency."
            }
          ],
          "is_simulated": true,
          "summary": "Generated 5 recommendation(s) across 7 monitored workflow(s). Flagged 2 high-failure workflow(s) and 1 slow workflow(s)."
        },
        "error": null
      }
    ],
    "final_output": {
      "overall_metrics": {
        "success_rate_percent": 87.2,
        "failure_rate_percent": 12.8,
        "avg_execution_time_seconds": 2.81,
        "total_workflows_monitored": 7
      },
      "workflow_performance": {
        "WF001": {
          "workflow_id": "WF001",
          "workflow_name": "Inventory Restock Check",
          "total_runs": 5,
          "success_count": 5,
          "failure_count": 0,
          "success_rate_percent": 100.0,
          "failure_rate_percent": 0.0,
          "is_failure_flagged": false
        },
        "WF002": {
          "workflow_id": "WF002",
          "workflow_name": "Product Price Validation",
          "total_runs": 10,
          "success_count": 9,
          "failure_count": 1,
          "success_rate_percent": 90.0,
          "failure_rate_percent": 10.0,
          "is_failure_flagged": false
        },
        "WF003": {
          "workflow_id": "WF003",
          "workflow_name": "Vendor File Processing",
          "total_runs": 12,
          "success_count": 9,
          "failure_count": 3,
          "success_rate_percent": 75.0,
          "failure_rate_percent": 25.0,
          "is_failure_flagged": true
        },
        "WF004": {
          "workflow_id": "WF004",
          "workflow_name": "Product Description Generator",
          "total_runs": 3,
          "success_count": 3,
          "failure_count": 0,
          "success_rate_percent": 100.0,
          "failure_rate_percent": 0.0,
          "is_failure_flagged": false
        },
        "WF005": {
          "workflow_id": "WF005",
          "workflow_name": "Customer Order Status",
          "total_runs": 5,
          "success_count": 4,
          "failure_count": 1,
          "success_rate_percent": 80.0,
          "failure_rate_percent": 20.0,
          "is_failure_flagged": true
        },
        "WF006": {
          "workflow_id": "WF006",
          "workflow_name": "Duplicate Product Detection",
          "total_runs": 2,
          "success_count": 2,
          "failure_count": 0,
          "success_rate_percent": 100.0,
          "failure_rate_percent": 0.0,
          "is_failure_flagged": false
        },
        "WF007": {
          "workflow_id": "WF007",
          "workflow_name": "Marketing Campaign Brief",
          "total_runs": 2,
          "success_count": 2,
          "failure_count": 0,
          "success_rate_percent": 100.0,
          "failure_rate_percent": 0.0,
          "is_failure_flagged": false
        }
      },
      "workflow_timings": {
        "WF001": {
          "workflow_id": "WF001",
          "workflow_name": "Inventory Restock Check",
          "avg_execution_time_seconds": 0.52,
          "min_execution_time_seconds": 0.45,
          "max_execution_time_seconds": 0.61,
          "is_slow_flagged": false
        },
        "WF002": {
          "workflow_id": "WF002",
          "workflow_name": "Product Price Validation",
          "avg_execution_time_seconds": 1.21,
          "min_execution_time_seconds": 0.95,
          "max_execution_time_seconds": 1.4,
          "is_slow_flagged": false
        },
        "WF003": {
          "workflow_id": "WF003",
          "workflow_name": "Vendor File Processing",
          "avg_execution_time_seconds": 6.15,
          "min_execution_time_seconds": 1.75,
          "max_execution_time_seconds": 9.1,
          "is_slow_flagged": true
        },
        "WF004": {
          "workflow_id": "WF004",
          "workflow_name": "Product Description Generator",
          "avg_execution_time_seconds": 2.1,
          "min_execution_time_seconds": 1.95,
          "max_execution_time_seconds": 2.25,
          "is_slow_flagged": false
        },
        "WF005": {
          "workflow_id": "WF005",
          "workflow_name": "Customer Order Status",
          "avg_execution_time_seconds": 1.02,
          "min_execution_time_seconds": 0.75,
          "max_execution_time_seconds": 1.9,
          "is_slow_flagged": false
        },
        "WF006": {
          "workflow_id": "WF006",
          "workflow_name": "Duplicate Product Detection",
          "avg_execution_time_seconds": 3.25,
          "min_execution_time_seconds": 3.1,
          "max_execution_time_seconds": 3.4,
          "is_slow_flagged": false
        },
        "WF007": {
          "workflow_id": "WF007",
          "workflow_name": "Marketing Campaign Brief",
          "avg_execution_time_seconds": 1.5,
          "min_execution_time_seconds": 1.45,
          "max_execution_time_seconds": 1.55,
          "is_slow_flagged": false
        }
      },
      "flagged_high_failure_workflows": [
        "WF003",
        "WF005"
      ],
      "flagged_slow_workflows": [
        "WF003"
      ],
      "frequent_errors": [
        {
          "error_message": "FormatError: Invalid CSV delimiter",
          "count": 2,
          "affected_workflows": [
            "WF003"
          ]
        },
        {
          "error_message": "MissingColumnError: vendor_price column absent",
          "count": 1,
          "affected_workflows": [
            "WF002"
          ]
        },
        {
          "error_message": "Timeout: file upload timeout after 9s",
          "count": 1,
          "affected_workflows": [
            "WF003"
          ]
        },
        {
          "error_message": "CarrierAPIError: Simulated carrier timeout",
          "count": 1,
          "affected_workflows": [
            "WF005"
          ]
        }
      ],
      "slow_steps": [
        {
          "workflow_id": "WF003",
          "workflow_name": "Vendor File Processing",
          "step_name": "clean_dataset_producer",
          "run_count": 10,
          "avg_time_seconds": 7.03,
          "max_time_seconds": 9.1,
          "is_slow": true
        }
      ],
      "recommendations": [
        {
          "category": "RELIABILITY",
          "workflow_id": "WF003",
          "priority": "HIGH",
          "finding": "WF003 (Vendor File Processing) has an elevated failure rate of 25.0% (Threshold: 10.0%).",
          "action": "Implement retry policies, strict schema validation, or robust error recovery in WF003."
        },
        {
          "category": "RELIABILITY",
          "workflow_id": "WF005",
          "priority": "HIGH",
          "finding": "WF005 (Customer Order Status) has an elevated failure rate of 20.0% (Threshold: 10.0%).",
          "action": "Implement retry policies, strict schema validation, or robust error recovery in WF005."
        },
        {
          "category": "PERFORMANCE",
          "workflow_id": "WF003",
          "priority": "MEDIUM",
          "finding": "WF003 (Vendor File Processing) average execution time is 6.15s (Threshold: 5.0s).",
          "action": "Profile step execution in WF003, optimize file streaming, or add caching for repetitive operations."
        },
        {
          "category": "ERROR_MITIGATION",
          "workflow_id": "WF003",
          "priority": "HIGH",
          "finding": "Top error (2 occurrences): 'FormatError: Invalid CSV delimiter'.",
          "action": "Add upstream input sanitization or fallback handling for this error type."
        },
        {
          "category": "BOTTLENECK_OPTIMIZATION",
          "workflow_id": "WF003",
          "priority": "MEDIUM",
          "finding": "Step 'clean_dataset_producer' in WF003 averages 7.03s.",
          "action": "Refactor I/O or parallelize chunk processing to reduce latency."
        }
      ],
      "is_simulated": true,
      "summary": "Generated 5 recommendation(s) across 7 monitored workflow(s). Flagged 2 high-failure workflow(s) and 1 slow workflow(s)."
    },
    "errors": [],
    "clarification_required": false,
    "routing_mode": "offline",
    "warnings": []
  }
};

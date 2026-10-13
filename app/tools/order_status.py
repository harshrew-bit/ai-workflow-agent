"""WF005 — Customer Order Status domain logic and execution tools.

Provides genuine domain execution for looking up customer order statuses,
retrieving shipment and tracking information, and safely prompting for another
identifier when no matching order is found, in accordance with data/workflows.xlsx.
"""

import csv
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field

from app.tools.base import BaseTool, ToolMetadata
from app.tools.base import ClarificationRequired


class OrderRecord(BaseModel):
    """Customer order entity."""

    order_id: str
    customer_email: str
    order_date: str
    status: str
    items: str
    total_amount: float
    currency: str = "USD"


class ShipmentRecord(BaseModel):
    """Fulfillment and shipment tracking entity."""

    shipment_id: str
    order_id: str
    carrier: str
    tracking_number: str
    estimated_delivery: str
    shipment_status: str
    last_location: str


def _load_orders_csv(file_path: Union[str, Path]) -> List[OrderRecord]:
    """Load orders from CSV safely."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Orders dataset file not found at '{path}'")

    orders: List[OrderRecord] = []
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
                raw_amt = row_dict.get("total_amount", "0").replace("$", "").replace(",", "")
                try:
                    amt = float(raw_amt)
                except ValueError:
                    amt = 0.0

                orders.append(
                    OrderRecord(
                        order_id=row_dict.get("order_id", ""),
                        customer_email=row_dict.get("customer_email", ""),
                        order_date=row_dict.get("order_date", ""),
                        status=row_dict.get("status", "UNKNOWN"),
                        items=row_dict.get("items", ""),
                        total_amount=amt,
                        currency=row_dict.get("currency", "USD"),
                    )
                )
    return orders


def _load_shipments_csv(file_path: Union[str, Path]) -> List[ShipmentRecord]:
    """Load shipments from CSV safely."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Shipments dataset file not found at '{path}'")

    shipments: List[ShipmentRecord] = []
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
                shipments.append(
                    ShipmentRecord(
                        shipment_id=row_dict.get("shipment_id", ""),
                        order_id=row_dict.get("order_id", ""),
                        carrier=row_dict.get("carrier", "Standard Carrier"),
                        tracking_number=row_dict.get("tracking_number", ""),
                        estimated_delivery=row_dict.get("estimated_delivery", "Pending"),
                        shipment_status=row_dict.get("shipment_status", "PROCESSING"),
                        last_location=row_dict.get("last_location", "Fulfillment Center"),
                    )
                )
    return shipments


def extract_order_identifier(
    identifier: Optional[str] = None,
    order_id: Optional[str] = None,
    customer_email: Optional[str] = None,
    request: Optional[str] = None,
    **kwargs: Any,
) -> Tuple[Optional[str], Optional[str]]:
    """Extract and categorize order identifier (order_id or customer_email)."""
    if order_id and order_id.strip():
        return order_id.strip(), "order_id"
    if customer_email and customer_email.strip():
        return customer_email.strip(), "customer_email"
    if identifier and identifier.strip():
        val = identifier.strip()
        if "@" in val:
            return val, "customer_email"
        return val, "order_id"

    # Inspect natural language request
    if request:
        # Check for order ID pattern e.g. ORD-1001 or #1001
        order_match = re.search(r"\b(ORD-\d{4,8})\b", request, re.IGNORECASE)
        if order_match:
            return order_match.group(1).upper(), "order_id"

        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", request)
        if email_match:
            return email_match.group(0), "customer_email"

    return None, None


# ==============================================================================
# Step Tools for Generic Execution Engine
# ==============================================================================


class OrderIdentifierValidatorTool(BaseTool):
    """Step 1 Tool: Validate identifier."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="order_identifier_validator",
            description="Validate the supplied order ID or customer email identifier.",
        )

    def execute(
        self,
        identifier: Optional[str] = None,
        order_id: Optional[str] = None,
        customer_email: Optional[str] = None,
        request: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        val, id_type = extract_order_identifier(
            identifier=identifier,
            order_id=order_id,
            customer_email=customer_email,
            request=request,
        )

        if not val:
            return {
                "identifier": None,
                "identifier_type": None,
                "is_valid": False,
                "summary": "No identifier provided. Please supply an Order ID or customer email.",
            }

        return {
            "identifier": val,
            "identifier_type": id_type,
            "is_valid": True,
            "summary": f"Validated identifier '{val}' (type: {id_type}).",
        }


class OrderDataSearchTool(BaseTool):
    """Step 2 Tool: search order data."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="order_data_search",
            description="Search order database for records matching order ID or customer email.",
        )

    def execute(
        self,
        identifier: Optional[str] = None,
        identifier_type: Optional[str] = None,
        orders_csv_path: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        default_path = Path("data/sample_orders.csv")
        target_path = Path(orders_csv_path) if orders_csv_path else default_path

        all_orders = _load_orders_csv(target_path)
        matching: List[OrderRecord] = []

        if identifier:
            clean_id = identifier.strip().lower()
            for o in all_orders:
                if clean_id == o.order_id.strip().lower() or clean_id == o.customer_email.strip().lower():
                    matching.append(o)

        order_found = len(matching) > 0
        summary_msg = (
            f"Found {len(matching)} order(s) for '{identifier}'."
            if order_found
            else f"No orders found matching '{identifier}'."
        )

        return {
            "matching_orders": [o.model_dump() for o in matching],
            "order_found": order_found,
            "identifier": identifier,
            "summary": summary_msg,
        }


class OrderStatusRetrieverTool(BaseTool):
    """Step 3 Tool: retrieve order status."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="order_status_retriever",
            description="Retrieve status and item details for matching order(s).",
        )

    def execute(
        self,
        matching_orders: Optional[List[Dict[str, Any]]] = None,
        order_found: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        orders = matching_orders or []
        order_statuses = [
            {
                "order_id": o["order_id"],
                "status": o["status"],
                "order_date": o["order_date"],
                "items": o["items"],
                "total_amount": o["total_amount"],
                "currency": o.get("currency", "USD"),
            }
            for o in orders
        ]

        summary_msg = (
            f"Retrieved status for {len(order_statuses)} order(s)."
            if order_statuses
            else "No order status to retrieve (no matching orders)."
        )

        return {
            "order_statuses": order_statuses,
            "order_found": order_found,
            "summary": summary_msg,
        }


class ShipmentInfoRetrieverTool(BaseTool):
    """Step 4 Tool: retrieve shipment information."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="shipment_info_retriever",
            description="Retrieve carrier tracking and shipment details for orders.",
        )

    def execute(
        self,
        matching_orders: Optional[List[Dict[str, Any]]] = None,
        shipments_csv_path: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        default_path = Path("data/sample_shipments.csv")
        target_path = Path(shipments_csv_path) if shipments_csv_path else default_path

        all_shipments = _load_shipments_csv(target_path)
        order_ids = {o["order_id"].strip().upper() for o in (matching_orders or [])}

        matching_shipments = [
            s.model_dump()
            for s in all_shipments
            if s.order_id.strip().upper() in order_ids
        ]

        return {
            "shipment_details": matching_shipments,
            "has_shipment": len(matching_shipments) > 0,
            "summary": f"Retrieved {len(matching_shipments)} shipment record(s).",
        }


class OrderStatusSummarizerTool(BaseTool):
    """Step 5 Tool: summarize current status."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="order_status_summarizer",
            description="Synthesize final customer order status and tracking summary.",
        )

    def execute(
        self,
        identifier: Optional[str] = None,
        matching_orders: Optional[List[Dict[str, Any]]] = None,
        order_statuses: Optional[List[Dict[str, Any]]] = None,
        shipment_details: Optional[List[Dict[str, Any]]] = None,
        order_found: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        orders = matching_orders or []
        shipments = {
            s["order_id"].strip().upper(): s for s in (shipment_details or [])
        }

        # Decision Logic: If no order is found, ask for another identifier
        if not order_found or not orders:
            id_text = f"'{identifier}'" if identifier else "provided identifier"
            prompt_msg = (
                f"No order found matching {id_text}. "
                "Please provide a valid Order ID (e.g., ORD-1001) or customer email address to locate your order."
            )
            raise ClarificationRequired(prompt_msg)

        summaries: List[Dict[str, Any]] = []
        for o in orders:
            oid = o["order_id"]
            ship = shipments.get(oid.strip().upper())

            summary_item = {
                "order_id": oid,
                "order_status": o["status"],
                "order_date": o["order_date"],
                "items": o["items"],
                "total_amount": o["total_amount"],
                "currency": o.get("currency", "USD"),
                "has_shipment": ship is not None,
                "carrier": ship["carrier"] if ship else "Pending Fulfillment",
                "tracking_number": ship["tracking_number"] if ship else "Not yet assigned",
                "estimated_delivery": ship["estimated_delivery"] if ship else "Not available",
                "shipment_status": ship["shipment_status"] if ship else "NOT_SHIPPED",
                "last_location": ship["last_location"] if ship else "Warehouse",
            }
            summaries.append(summary_item)

        primary = summaries[0]
        full_summary = (
            f"Order {primary['order_id']} is currently {primary['order_status']} "
            f"(Shipment: {primary['shipment_status']}"
            + (f", Carrier: {primary['carrier']}, Tracking: {primary['tracking_number']})" if primary['has_shipment'] else ")")
            + f". Items: {primary['items']}."
        )

        return {
            "order_found": True,
            "order_id": primary["order_id"],
            "orders": summaries,
            "summary": full_summary,
            "request_another_identifier": False,
            "is_simulated": True,
        }

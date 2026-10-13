"""Unit tests for WF005 — Customer Order Status domain tools and lookup logic."""

from pathlib import Path
import pytest

from app.tools.base import ClarificationRequired
from app.tools.order_status import (
    OrderDataSearchTool,
    OrderIdentifierValidatorTool,
    OrderStatusRetrieverTool,
    OrderStatusSummarizerTool,
    ShipmentInfoRetrieverTool,
    _load_orders_csv,
    _load_shipments_csv,
    extract_order_identifier,
)


def test_extract_order_identifier():
    """Verify identifier extraction from explicit args and natural language queries."""
    val, id_type = extract_order_identifier(order_id="ORD-1001")
    assert val == "ORD-1001"
    assert id_type == "order_id"

    val, id_type = extract_order_identifier(customer_email="alice@example.com")
    assert val == "alice@example.com"
    assert id_type == "customer_email"

    # From query string
    val, id_type = extract_order_identifier(request="Where is order ORD-1002?")
    assert val == "ORD-1002"
    assert id_type == "order_id"

    val, id_type = extract_order_identifier(request="Check status for bob@example.com please")
    assert val == "bob@example.com"
    assert id_type == "customer_email"


def test_load_sample_order_and_shipment_data():
    """Verify loading real sample order and shipment CSV files."""
    orders = _load_orders_csv("data/sample_orders.csv")
    shipments = _load_shipments_csv("data/sample_shipments.csv")

    assert len(orders) == 5
    assert len(shipments) == 2
    assert orders[0].order_id == "ORD-1001"
    assert shipments[0].order_id == "ORD-1001"
    assert shipments[0].carrier == "FastShip Express"


def test_known_order_with_shipment_lookup():
    """Verify looking up order ORD-1001 retrieves order status and active tracking details."""
    search_tool = OrderDataSearchTool()
    shipment_tool = ShipmentInfoRetrieverTool()
    summarizer_tool = OrderStatusSummarizerTool()

    search_res = search_tool.execute(identifier="ORD-1001", identifier_type="order_id")
    assert search_res["order_found"] is True
    assert len(search_res["matching_orders"]) == 1

    ship_res = shipment_tool.execute(matching_orders=search_res["matching_orders"])
    assert ship_res["has_shipment"] is True
    assert len(ship_res["shipment_details"]) == 1

    summary_res = summarizer_tool.execute(
        identifier="ORD-1001",
        matching_orders=search_res["matching_orders"],
        shipment_details=ship_res["shipment_details"],
        order_found=True,
    )
    assert summary_res["order_found"] is True
    assert summary_res["order_id"] == "ORD-1001"
    order_info = summary_res["orders"][0]
    assert order_info["order_status"] == "SHIPPED"
    assert order_info["carrier"] == "FastShip Express"
    assert order_info["tracking_number"] == "TRK-987654321"


def test_order_without_shipment_yet():
    """Verify order ORD-1003 (PROCESSING) retrieves status without crashing on missing shipment."""
    search_tool = OrderDataSearchTool()
    shipment_tool = ShipmentInfoRetrieverTool()
    summarizer_tool = OrderStatusSummarizerTool()

    search_res = search_tool.execute(identifier="ORD-1003", identifier_type="order_id")
    assert search_res["order_found"] is True

    ship_res = shipment_tool.execute(matching_orders=search_res["matching_orders"])
    assert ship_res["has_shipment"] is False

    summary_res = summarizer_tool.execute(
        identifier="ORD-1003",
        matching_orders=search_res["matching_orders"],
        shipment_details=ship_res["shipment_details"],
        order_found=True,
    )
    assert summary_res["order_found"] is True
    order_info = summary_res["orders"][0]
    assert order_info["order_status"] == "PROCESSING"
    assert order_info["carrier"] == "Pending Fulfillment"
    assert order_info["shipment_status"] == "NOT_SHIPPED"


def test_unknown_order_asks_for_another_identifier():
    """Verify Decision Logic: if no order is found, ask for another identifier (clarification)."""
    search_tool = OrderDataSearchTool()
    summarizer_tool = OrderStatusSummarizerTool()

    search_res = search_tool.execute(identifier="ORD-9999", identifier_type="order_id")
    assert search_res["order_found"] is False

    with pytest.raises(ClarificationRequired) as exc:
        summarizer_tool.execute(
            identifier="ORD-9999",
            matching_orders=search_res["matching_orders"],
            order_found=False,
        )
    assert "No order found matching 'ORD-9999'" in str(exc.value)
    assert "Please provide a valid Order ID" in str(exc.value)



def test_missing_files_error_handling(tmp_path: Path):
    """Verify FileNotFoundError when order dataset is missing."""
    with pytest.raises(FileNotFoundError):
        _load_orders_csv(tmp_path / "non_existent_orders.csv")

    with pytest.raises(FileNotFoundError):
        _load_shipments_csv(tmp_path / "non_existent_shipments.csv")


def test_step_by_step_wf005_tools_cascading():
    """Test all 5 step tools executing sequentially and passing context data."""
    val_tool = OrderIdentifierValidatorTool()
    search_tool = OrderDataSearchTool()
    status_tool = OrderStatusRetrieverTool()
    shipment_tool = ShipmentInfoRetrieverTool()
    summary_tool = OrderStatusSummarizerTool()

    # Step 1: Validate identifier
    out1 = val_tool.execute(request="Where is my order ORD-1002?")
    assert out1["is_valid"] is True
    assert out1["identifier"] == "ORD-1002"

    # Step 2: search order data
    out2 = search_tool.execute(
        identifier=out1["identifier"],
        identifier_type=out1["identifier_type"],
    )
    assert out2["order_found"] is True
    assert len(out2["matching_orders"]) == 1

    # Step 3: retrieve order status
    out3 = status_tool.execute(
        matching_orders=out2["matching_orders"],
        order_found=out2["order_found"],
    )
    assert len(out3["order_statuses"]) == 1
    assert out3["order_statuses"][0]["status"] == "DELIVERED"

    # Step 4: retrieve shipment information
    out4 = shipment_tool.execute(matching_orders=out2["matching_orders"])
    assert out4["has_shipment"] is True

    # Step 5: summarize current status
    out5 = summary_tool.execute(
        identifier=out1["identifier"],
        matching_orders=out2["matching_orders"],
        order_statuses=out3["order_statuses"],
        shipment_details=out4["shipment_details"],
        order_found=out2["order_found"],
    )
    assert out5["order_found"] is True
    assert out5["order_id"] == "ORD-1002"
    assert "DELIVERED" in out5["summary"]

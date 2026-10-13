"""Unit tests for WF007 — Marketing Campaign Brief domain tools and generation logic."""

import pytest

from app.tools.base import ClarificationRequired
from app.tools.campaign_brief import (
    CampaignChannelRecommenderTool,
    CampaignChecklistCreatorTool,
    CampaignInputsValidatorTool,
    CampaignMessagingCreatorTool,
    CampaignObjectiveIdentifierTool,
    CampaignProductSummarizerTool,
    extract_and_validate_campaign_inputs,
)


def test_full_campaign_inputs_validation():
    """Verify validation when all campaign parameters are supplied."""
    inputs = extract_and_validate_campaign_inputs(
        campaign_goal="Launch Summer Ergonomic Workspace Collection",
        dates="2026-06-01 to 2026-06-30",
        product_list=["Bamboo Stand", "Mesh Chair"],
        target_audience="Work-from-home professionals",
        promotion="10% off bundles",
    )
    assert inputs.campaign_goal == "Launch Summer Ergonomic Workspace Collection"
    assert inputs.dates == "2026-06-01 to 2026-06-30"
    assert len(inputs.product_list) == 2
    assert inputs.target_audience == "Work-from-home professionals"
    assert inputs.promotion == "10% off bundles"


def test_missing_campaign_goal_requests_clarification():
    """Verify Decision Logic: If campaign goal is missing, request it before generating brief."""
    with pytest.raises(ClarificationRequired, match="Required input 'campaign_goal' is missing"):
        extract_and_validate_campaign_inputs(
            campaign_goal="",
            dates="2026-06-01 to 2026-06-30",
        )

    with pytest.raises(ClarificationRequired, match="Required input 'campaign_goal' is missing"):
        extract_and_validate_campaign_inputs(
            campaign_goal=None,
            dates="2026-06-01 to 2026-06-30",
        )


def test_missing_dates_requests_clarification():
    """Verify Decision Logic: If dates are missing, request them before generating brief."""
    with pytest.raises(ClarificationRequired, match="Required input 'dates' is missing"):
        extract_and_validate_campaign_inputs(
            campaign_goal="Launch Q4 Holiday Promo",
            dates="",
        )

    with pytest.raises(ClarificationRequired, match="Required input 'dates' is missing"):
        extract_and_validate_campaign_inputs(
            campaign_goal="Launch Q4 Holiday Promo",
            dates=None,
        )


def test_no_invented_discounts_or_claims():
    """Verify that when no promotion is provided, discounts are not invented."""
    inputs = extract_and_validate_campaign_inputs(
        campaign_goal="Brand Awareness Push",
        dates="2026-07-01 to 2026-07-15",
        promotion=None,
    )
    assert inputs.promotion is None

    msg_tool = CampaignMessagingCreatorTool()
    out = msg_tool.execute(
        campaign_goal=inputs.campaign_goal,
        target_audience="General Audience",
        promotion=inputs.promotion,
    )
    # Must not contain hallucinated 50% or 20% off
    promo_callout = out["campaign_messaging"]["promotional_callout"]
    assert "No special discount specified" in promo_callout
    assert "50%" not in promo_callout


def test_step_by_step_wf007_tools_cascading():
    """Test all 6 step tools executing sequentially and compiling final campaign brief."""
    val_tool = CampaignInputsValidatorTool()
    obj_tool = CampaignObjectiveIdentifierTool()
    prod_tool = CampaignProductSummarizerTool()
    msg_tool = CampaignMessagingCreatorTool()
    chan_tool = CampaignChannelRecommenderTool()
    check_tool = CampaignChecklistCreatorTool()

    # Step 1: Validate inputs
    out1 = val_tool.execute(
        campaign_goal="Increase Eco-Line Adoption by 25%",
        dates="2026-09-01 to 2026-09-30",
        product_list=["Recycled Felt Desk Mat", "Cork Laptop Sleeve"],
        target_audience="Sustainability-conscious creators",
        promotion="Free shipping with code GREEN",
    )
    assert out1["is_valid"] is True

    # Step 2: identify campaign objective
    out2 = obj_tool.execute(campaign_goal=out1["campaign_goal"])
    assert "target_kpis" in out2["campaign_objectives"]

    # Step 3: summarize products
    out3 = prod_tool.execute(product_list=out1["product_list"])
    assert len(out3["featured_products"]) == 2

    # Step 4: create messaging
    out4 = msg_tool.execute(
        campaign_goal=out1["campaign_goal"],
        target_audience=out1["target_audience"],
        promotion=out1["promotion"],
    )
    assert "primary_headline" in out4["campaign_messaging"]

    # Step 5: create channel recommendations
    out5 = chan_tool.execute(target_audience=out1["target_audience"])
    assert len(out5["recommended_channels"]) >= 3

    # Step 6: create campaign checklist
    out6 = check_tool.execute(
        campaign_goal=out1["campaign_goal"],
        dates=out1["dates"],
        product_list=out1["product_list"],
        target_audience=out1["target_audience"],
        promotion=out1["promotion"],
        campaign_objectives=out2["campaign_objectives"],
        product_summary=out3["product_summary"],
        campaign_messaging=out4["campaign_messaging"],
        recommended_channels=out5["recommended_channels"],
    )
    assert out6["is_simulated"] is True
    assert out6["campaign_goal"] == "Increase Eco-Line Adoption by 25%"
    assert len(out6["execution_checklist"]) >= 4
    assert out6["timeline"] == "2026-09-01 to 2026-09-30"

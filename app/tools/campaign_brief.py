"""WF007 — Marketing Campaign Brief domain logic and execution tools.

Generates structured marketing campaign briefs covering objectives, audience,
messaging, channels, schedule, and execution checklists strictly adhering to the
decision logic in data/workflows.xlsx (refusing generation if goal or dates are absent).
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from app.tools.base import BaseTool, ToolMetadata


class ValidatedCampaignInputs(BaseModel):
    """Container for validated marketing campaign parameters."""

    campaign_goal: str
    dates: str
    product_list: List[str] = Field(default_factory=list)
    target_audience: Optional[str] = None
    promotion: Optional[str] = None


def extract_and_validate_campaign_inputs(
    campaign_goal: Optional[str] = None,
    dates: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    timeline: Optional[str] = None,
    product_list: Optional[Union[List[str], str]] = None,
    products: Optional[Union[List[str], str]] = None,
    target_audience: Optional[str] = None,
    audience: Optional[str] = None,
    promotion: Optional[str] = None,
    discount: Optional[str] = None,
    **kwargs: Any,
) -> ValidatedCampaignInputs:
    """Validate required inputs strictly enforcing WF007 Decision Logic:

    Decision Logic: If campaign goal or dates are missing, request them before generating the brief.
    """
    clean_goal = str(campaign_goal or "").strip()
    if not clean_goal:
        raise ValueError(
            "Required input 'campaign_goal' is missing. "
            "Please provide a specific campaign goal before generating the campaign brief."
        )

    clean_dates = str(dates or timeline or "").strip()
    if not clean_dates and start_date:
        clean_dates = f"{start_date} to {end_date or 'Ongoing'}"

    if not clean_dates:
        raise ValueError(
            "Required input 'dates' is missing. "
            "Please provide campaign dates or a schedule before generating the campaign brief."
        )

    # Parse product list
    parsed_products: List[str] = []
    raw_products = product_list or products
    if isinstance(raw_products, list):
        parsed_products = [str(p).strip() for p in raw_products if str(p).strip()]
    elif isinstance(raw_products, str) and raw_products.strip():
        parsed_products = [p.strip() for p in raw_products.split(",") if p.strip()]

    clean_audience = str(target_audience or audience or "").strip() or None
    clean_promo = str(promotion or discount or "").strip() or None

    return ValidatedCampaignInputs(
        campaign_goal=clean_goal,
        dates=clean_dates,
        product_list=parsed_products,
        target_audience=clean_audience,
        promotion=clean_promo,
    )


# ==============================================================================
# Step Tools for Generic Execution Engine
# ==============================================================================


class CampaignInputsValidatorTool(BaseTool):
    """Step 1 Tool: Validate inputs."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="campaign_inputs_validator",
            description="Validate essential campaign inputs (goal and dates) before generating brief.",
        )

    def execute(
        self,
        campaign_goal: Optional[str] = None,
        dates: Optional[str] = None,
        product_list: Optional[Union[List[str], str]] = None,
        target_audience: Optional[str] = None,
        promotion: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        val = extract_and_validate_campaign_inputs(
            campaign_goal=campaign_goal,
            dates=dates,
            product_list=product_list,
            target_audience=target_audience,
            promotion=promotion,
            **kwargs,
        )
        return {
            "campaign_goal": val.campaign_goal,
            "dates": val.dates,
            "product_list": val.product_list,
            "target_audience": val.target_audience,
            "promotion": val.promotion,
            "is_valid": True,
            "summary": f"Validated campaign inputs for '{val.campaign_goal}' ({val.dates}).",
        }


class CampaignObjectiveIdentifierTool(BaseTool):
    """Step 2 Tool: identify campaign objective."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="campaign_objective_identifier",
            description="Identify primary objectives, secondary objectives, and KPI targets.",
        )

    def execute(
        self,
        campaign_goal: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        goal = campaign_goal or "Campaign Launch"
        objectives = {
            "primary_objective": goal,
            "target_kpis": [
                "Total Revenue & Return on Ad Spend (ROAS)",
                "Conversion Rate (CVR) and Qualified Leads",
                "Brand Reach and Audience Engagement",
            ],
            "measurement_cadence": "Weekly checkpoint and post-campaign retro",
        }
        return {
            "campaign_objectives": objectives,
            "summary": f"Identified primary campaign objective: '{goal}'.",
        }


class CampaignProductSummarizerTool(BaseTool):
    """Step 3 Tool: summarize products."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="campaign_product_summarizer",
            description="Summarize featured products and catalog focus areas.",
        )

    def execute(
        self,
        product_list: Optional[Union[List[str], str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        p_list = product_list or []
        if isinstance(p_list, str):
            p_list = [p.strip() for p in p_list.split(",") if p.strip()]

        summary_text = (
            f"Featured Products ({len(p_list)}): {', '.join(p_list)}"
            if p_list
            else "General Catalog / Brand-Wide Focus (no specific products singled out)"
        )
        return {
            "featured_products": p_list,
            "product_summary": summary_text,
            "summary": f"Summarized {len(p_list)} featured campaign product(s).",
        }


class CampaignMessagingCreatorTool(BaseTool):
    """Step 4 Tool: create messaging."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="campaign_messaging_creator",
            description="Create value propositions and core messaging pillars.",
        )

    def execute(
        self,
        campaign_goal: Optional[str] = None,
        target_audience: Optional[str] = None,
        promotion: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        aud = target_audience or "Valued Customers"
        promo_text = f"Offer: {promotion}" if promotion else "Standard Value Proposition (No special discount specified)"

        messaging = {
            "primary_headline": f"Empowering {aud}: {campaign_goal}",
            "core_value_props": [
                "Uncompromising Quality & Reliability",
                "Customer-Centric Value & Modern Convenience",
            ],
            "promotional_callout": promo_text,
        }
        return {
            "campaign_messaging": messaging,
            "summary": f"Created targeted messaging for audience '{aud}'.",
        }


class CampaignChannelRecommenderTool(BaseTool):
    """Step 5 Tool: create channel recommendations."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="campaign_channel_recommender",
            description="Recommend marketing channels and distribution mix.",
        )

    def execute(
        self,
        target_audience: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        channels = [
            {"channel": "Email Marketing", "role": "Announcements, personalized abandoned-cart and loyalty flows"},
            {"channel": "Organic & Paid Social", "role": "Short-form video showcases, influencer unboxings, visual carousels"},
            {"channel": "Paid Search & SEO", "role": "High-intent product search terms and landing page optimization"},
            {"channel": "On-Site Merchandising", "role": "Hero banner placement, collection showcase, category badges"},
        ]
        return {
            "recommended_channels": channels,
            "summary": f"Recommended {len(channels)} distribution marketing channel(s).",
        }


class CampaignChecklistCreatorTool(BaseTool):
    """Step 6 Tool: create campaign checklist and finalize brief."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="campaign_checklist_creator",
            description="Create milestone checklist and compile final structured campaign brief.",
        )

    def execute(
        self,
        campaign_goal: Optional[str] = None,
        dates: Optional[str] = None,
        product_list: Optional[Union[List[str], str]] = None,
        target_audience: Optional[str] = None,
        promotion: Optional[str] = None,
        campaign_objectives: Optional[Dict[str, Any]] = None,
        product_summary: Optional[str] = None,
        campaign_messaging: Optional[Dict[str, Any]] = None,
        recommended_channels: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        checklist = [
            {"phase": "Pre-Launch (T - 2 weeks)", "task": "Finalize creative assets, product photography, and promotional copy."},
            {"phase": "Pre-Launch (T - 1 week)", "task": "QA tracking links, landing pages, and email distribution lists."},
            {"phase": "Launch Day (T - 0)", "task": "Deploy hero banners, dispatch launch email, and activate paid campaigns."},
            {"phase": "Mid-Campaign (T + 1 week)", "task": "Review conversion metrics, reallocate budget to top-performing channels."},
            {"phase": "Post-Launch", "task": "Analyze final ROAS, customer feedback, and document learnings."},
        ]

        p_list = product_list or []
        if isinstance(p_list, str):
            p_list = [p.strip() for p in p_list.split(",") if p.strip()]

        final_brief = {
            "campaign_goal": campaign_goal,
            "timeline": dates,
            "target_audience": target_audience or "General Audience",
            "promotion": promotion or "None specified",
            "featured_products": p_list,
            "objectives": campaign_objectives or {},
            "messaging": campaign_messaging or {},
            "channels": recommended_channels or [],
            "execution_checklist": checklist,
            "is_simulated": True,
            "provider": "simulated_campaign_brief_generator",
            "summary": f"Generated marketing brief for '{campaign_goal}' ({dates}).",
        }
        return final_brief

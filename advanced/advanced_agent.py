import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from google import genai


MODEL_NAME = "gemini-2.5-flash"

INCIDENT_START = "2026-08-15"

# A hypothesis must explain at least this share of
# candidate impact before we call it dominant.
DOMINANCE_THRESHOLD = 0.60

# Ignore tiny before/after movements as normal noise.
MIN_MECHANISM_CHANGE = 0.03


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def safe_pct_drop(before, after):
    if before == 0:
        return 0.0

    return max(
        0.0,
        (before - after) / abs(before)
    )


def prepare_data(df):
    """
    Standardize columns needed by the evidence tools.
    """

    df = df.copy()

    df["date"] = pd.to_datetime(df["date"])

    # Older benchmark cases did not explicitly store
    # conversion_rate, so reconstruct it when necessary.
    if "conversion_rate" not in df.columns:
        df["conversion_rate"] = (
            df["orders"]
            / df["visitors"].replace(0, np.nan)
        )

    return df


# ---------------------------------------------------------
# Evidence generation
# ---------------------------------------------------------

def analyze_segment(
    df,
    region,
    product,
):
    """
    Test four possible revenue mechanisms for one segment:

    - traffic drop
    - conversion-rate drop
    - price drop
    - inventory shortage

    Returns structured evidence for this segment.
    """

    segment = df[
        (df["region"] == region)
        & (df["product"] == product)
    ].copy()

    before = segment[
        segment["date"] < INCIDENT_START
    ]

    after = segment[
        segment["date"] >= INCIDENT_START
    ]

    if before.empty or after.empty:
        return []

    days_after = after["date"].nunique()

    visitors_before = before["visitors"].mean()
    visitors_after = after["visitors"].mean()

    conversion_before = before["conversion_rate"].mean()
    conversion_after = after["conversion_rate"].mean()

    price_before = before["price"].mean()
    price_after = after["price"].mean()

    revenue_before = before["revenue"].mean()
    revenue_after = after["revenue"].mean()

    units_after = after["units_sold"].mean()

    candidates = []

    # =====================================================
    # 1. Traffic hypothesis
    # =====================================================

    traffic_drop_ratio = safe_pct_drop(
        visitors_before,
        visitors_after,
    )

    if traffic_drop_ratio >= MIN_MECHANISM_CHANGE:

        lost_visitors_per_day = (
            visitors_before
            - visitors_after
        )

        traffic_impact = max(
            0.0,
            lost_visitors_per_day
            * conversion_before
            * price_before
            * days_after
        )

        candidates.append(
            {
                "cause": "traffic_drop",
                "region": region,
                "product": product,
                "impact": float(traffic_impact),
                "mechanism_change_pct": (
                    traffic_drop_ratio * 100
                ),
            }
        )

    # =====================================================
    # 2. Conversion hypothesis
    # =====================================================

    conversion_drop_ratio = safe_pct_drop(
        conversion_before,
        conversion_after,
    )

    if conversion_drop_ratio >= MIN_MECHANISM_CHANGE:

        lost_conversion = (
            conversion_before
            - conversion_after
        )

        conversion_impact = max(
            0.0,
            visitors_after
            * lost_conversion
            * price_before
            * days_after
        )

        candidates.append(
            {
                "cause": "conversion_rate_drop",
                "region": region,
                "product": product,
                "impact": float(conversion_impact),
                "mechanism_change_pct": (
                    conversion_drop_ratio * 100
                ),
            }
        )

    # =====================================================
    # 3. Price hypothesis
    # =====================================================

    price_drop_ratio = safe_pct_drop(
        price_before,
        price_after,
    )

    if price_drop_ratio >= MIN_MECHANISM_CHANGE:

        lost_price = (
            price_before
            - price_after
        )

        price_impact = max(
            0.0,
            units_after
            * lost_price
            * days_after
        )

        candidates.append(
            {
                "cause": "price_drop",
                "region": region,
                "product": product,
                "impact": float(price_impact),
                "mechanism_change_pct": (
                    price_drop_ratio * 100
                ),
            }
        )

    # =====================================================
    # 4. Inventory-shortage hypothesis
    # =====================================================

    # This is stronger than merely checking whether
    # inventory fell.
    #
    # Inventory is causal only when orders exceed inventory,
    # meaning sales were actually constrained.

    constrained_units = np.maximum(
        after["orders"].to_numpy()
        - after["inventory"].to_numpy(),
        0,
    )

    inventory_impact = float(
        np.sum(
            constrained_units
            * after["price"].to_numpy()
        )
    )

    constrained_rows = int(
        np.sum(constrained_units > 0)
    )

    if inventory_impact > 0:

        candidates.append(
            {
                "cause": "inventory_shortage",
                "region": region,
                "product": product,
                "impact": inventory_impact,
                "constrained_rows": constrained_rows,
                "mechanism_change_pct": None,
            }
        )

    # Add segment context to every candidate.

    for candidate in candidates:

        candidate["segment_revenue_before"] = float(
            revenue_before
        )

        candidate["segment_revenue_after"] = float(
            revenue_after
        )

    return candidates


def build_evidence(df):
    """
    Generate and test competing hypotheses across all
    region/product segments.
    """

    regions = sorted(
        df["region"].dropna().unique()
    )

    products = sorted(
        df["product"].dropna().unique()
    )

    candidates = []

    for region in regions:
        for product in products:

            segment_candidates = analyze_segment(
                df=df,
                region=region,
                product=product,
            )

            candidates.extend(
                segment_candidates
            )

    # Ignore negligible estimated impacts.

    candidates = [
        candidate
        for candidate in candidates
        if candidate["impact"] >= 100
    ]

    candidates.sort(
        key=lambda x: x["impact"],
        reverse=True,
    )

    total_candidate_impact = sum(
        candidate["impact"]
        for candidate in candidates
    )

    if total_candidate_impact > 0:

        for candidate in candidates:

            candidate["impact_share"] = (
                candidate["impact"]
                / total_candidate_impact
            )

    else:

        for candidate in candidates:
            candidate["impact_share"] = 0.0

    return candidates


# ---------------------------------------------------------
# Overall KPI evidence
# ---------------------------------------------------------

def calculate_overall_drop(df):

    daily = (
        df.groupby("date")["revenue"]
        .sum()
        .reset_index()
    )

    before = daily[
        daily["date"] < INCIDENT_START
    ]["revenue"].mean()

    after = daily[
        daily["date"] >= INCIDENT_START
    ]["revenue"].mean()

    drop_pct = safe_pct_drop(
        before,
        after,
    ) * 100

    return {
        "before": float(before),
        "after": float(after),
        "drop_pct": float(drop_pct),
    }


# ---------------------------------------------------------
# LLM evidence review
# ---------------------------------------------------------

def get_llm_review(
    scenario_id,
    overall,
    candidates,
):
    """
    Gemini reviews already-computed evidence.

    It does NOT directly control the final decision.
    """

    evidence_json = json.dumps(
        candidates[:8],
        indent=2
    )

    prompt = f"""
You are reviewing evidence for a KPI incident investigation.

Scenario:
{scenario_id}

Overall revenue changed from
{overall["before"]:.2f}
to
{overall["after"]:.2f}.

Overall revenue decline:
{overall["drop_pct"]:.2f}%

The following candidate explanations were generated by
deterministic evidence tools.

CANDIDATES:
{evidence_json}

Your job is NOT to invent additional causes.

IMPORTANT INTERPRETATION NOTE:
Candidate "impact" values are estimated cumulative revenue impact across the
full post-incident period. The overall revenue before/after values are average
daily revenue. These quantities use different time scales and should NOT be
directly compared as if they were the same unit. Do not flag a candidate merely
because cumulative impact is larger than the average daily revenue decline.
Focus on mechanism evidence, relative impact shares, and dominance.

Briefly answer:

1. Which hypotheses have meaningful executable evidence?
2. Are multiple explanations comparable?
3. Does one explanation clearly dominate?
4. Should the system be cautious or abstain?

Keep the response under 150 words.
"""

    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"]
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    usage = response.usage_metadata

    input_tokens = getattr(usage, "prompt_token_count", 0) or 0
    output_tokens = getattr(usage, "candidates_token_count", 0) or 0
    thinking_tokens = getattr(usage, "thoughts_token_count", 0) or 0

    print()
    print("TOKEN USAGE")
    print("-----------")
    print(f"Input tokens: {input_tokens}")
    print(f"Output tokens: {output_tokens}")
    print(f"Thinking tokens: {thinking_tokens}")

    return response.text.strip()


# ---------------------------------------------------------
# Deterministic verifier
# ---------------------------------------------------------

def verify_decision(
    overall,
    candidates,
):
    """
    Final safety/verification layer.

    A dominant explanation is accepted only when its
    evidence materially exceeds competing hypotheses.

    Otherwise the workflow abstains.
    """

    if not candidates:

        return {
            "should_abstain": True,
            "reason": (
                "No materially supported hypotheses."
            ),
            "winner": None,
        }

    top = candidates[0]

    top_share = top.get(
        "impact_share",
        0.0
    )

    overall_drop = overall["drop_pct"]

    # -----------------------------------------------------
    # Dominance rule
    # -----------------------------------------------------
    #
    # Normally:
    #   candidate must explain >= 60% of modeled impact.
    #
    # If the overall KPI movement is very small (<5%),
    # we demand extremely strong evidence (>=80%) before
    # attributing one dominant cause.
    #
    # This prevents normal noise from being turned into
    # a confident causal story.
    # -----------------------------------------------------

    if overall_drop < 5.0:

        dominant = (
            top_share >= 0.80
        )

    else:

        dominant = (
            top_share >= DOMINANCE_THRESHOLD
        )

    if dominant:

        return {
            "should_abstain": False,
            "reason": (
                f"Top hypothesis explains "
                f"{top_share * 100:.2f}% "
                f"of modeled candidate impact."
            ),
            "winner": top,
        }

    return {
        "should_abstain": True,
        "reason": (
            f"No hypothesis dominates. "
            f"Top candidate explains only "
            f"{top_share * 100:.2f}% "
            f"of modeled candidate impact."
        ),
        "winner": None,
    }


# ---------------------------------------------------------
# Advanced agent
# ---------------------------------------------------------

def run_advanced(
    data_path,
    scenario_id,
    output_path,
):

    # 1. Observe

    df = pd.read_csv(
        data_path
    )

    df = prepare_data(df)

    overall = calculate_overall_drop(
        df
    )

    # 2. Generate + test competing hypotheses

    candidates = build_evidence(
        df
    )

    print()
    print("TOP EVIDENCE CANDIDATES")
    print("-----------------------")

    for candidate in candidates[:5]:

        print(
            candidate["cause"],
            "|",
            candidate["region"],
            "/",
            candidate["product"],
            "| impact:",
            round(
                candidate["impact"],
                2
            ),
            "| share:",
            round(
                candidate["impact_share"] * 100,
                2
            ),
            "%",
        )

    # 3. Agent reviews evidence

    llm_review = get_llm_review(
        scenario_id=scenario_id,
        overall=overall,
        candidates=candidates,
    )

    print()
    print("GEMINI EVIDENCE REVIEW")
    print("----------------------")
    print(llm_review)

    # 4. Verify

    verification = verify_decision(
        overall=overall,
        candidates=candidates,
    )

    # 5. Produce final structured result

    if verification["should_abstain"]:

        prediction = {
            "scenario_id": scenario_id,
            "should_abstain": True,
            "dominant_cause": None,
            "affected_region": None,
            "affected_product": None,
            "estimated_impact": None,
            "explanation": (
                verification["reason"]
                + " "
                + llm_review
            ),
            "evidence_candidates": candidates[:5],
        }

    else:

        winner = verification["winner"]

        prediction = {
            "scenario_id": scenario_id,
            "should_abstain": False,
            "dominant_cause": winner["cause"],
            "affected_region": winner["region"],
            "affected_product": winner["product"],
            "estimated_impact": winner["impact"],
            "explanation": (
                verification["reason"]
                + " "
                + llm_review
            ),
            "evidence_candidates": candidates[:5],
        }

    # 6. Save

    output = Path(
        output_path
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(output, "w") as f:

        json.dump(
            prediction,
            f,
            indent=4,
        )

    print()
    print("FINAL VERIFIED DECISION")
    print("-----------------------")
    print(
        json.dumps(
            {
                "scenario_id": (
                    prediction["scenario_id"]
                ),
                "should_abstain": (
                    prediction["should_abstain"]
                ),
                "dominant_cause": (
                    prediction["dominant_cause"]
                ),
                "affected_region": (
                    prediction["affected_region"]
                ),
                "affected_product": (
                    prediction["affected_product"]
                ),
                "estimated_impact": (
                    prediction["estimated_impact"]
                ),
            },
            indent=4,
        )
    )

    print()
    print(
        f"Prediction saved to: {output}"
    )


# ---------------------------------------------------------
# CLI
# ---------------------------------------------------------

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--data",
        required=True,
    )

    parser.add_argument(
        "--scenario-id",
        required=True,
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    args = parser.parse_args()

    run_advanced(
        data_path=args.data,
        scenario_id=args.scenario_id,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
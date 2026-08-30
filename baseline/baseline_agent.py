import argparse
import json
import os
from pathlib import Path

import pandas as pd
from google import genai


MODEL_NAME = "gemini-2.5-flash"


def run_baseline(
    data_path: str,
    scenario_id: str,
    output_path: str,
):
    """
    Simple baseline:

    Dataset + question
        ->
    One LLM call
        ->
    Structured prediction

    No retries.
    No verifier.
    No hypothesis-testing loop.
    """

    # -----------------------------------------------------
    # Load dataset
    # -----------------------------------------------------

    df = pd.read_csv(data_path)

    # Convert the complete benchmark dataset to CSV text
    dataset_text = df.to_csv(index=False)

    question = (
        "Why did overall revenue drop after 2026-08-15?"
    )

    # -----------------------------------------------------
    # Simple baseline prompt
    # -----------------------------------------------------

    prompt = f"""
You are a business data analyst.

Your task is to investigate the following question:

{question}

You are given the complete dataset below.

DATASET:
{dataset_text}

Analyze the data once and provide your best explanation.

You must decide whether:

1. There is one dominant cause of the revenue decline, OR
2. The evidence does not support one dominant cause.

Possible cause labels include:

- inventory_shortage
- conversion_rate_drop
- traffic_drop
- price_drop

If there is no clearly supported dominant cause,
set should_abstain to true.

Return ONLY valid JSON using exactly this structure:

{{
    "scenario_id": "{scenario_id}",
    "should_abstain": true or false,
    "dominant_cause": "cause label or null",
    "affected_region": "region or null",
    "affected_product": "product or null",
    "estimated_impact": number or null,
    "explanation": "short explanation"
}}

Do not include markdown.
Do not include ```json.
Do not include any text outside the JSON.
"""

    # -----------------------------------------------------
    # Call Gemini ONCE
    # -----------------------------------------------------

    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"]
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    raw_text = response.text.strip()

    print()
    print("RAW BASELINE RESPONSE")
    print("---------------------")
    print(raw_text)

    # -----------------------------------------------------
    # Parse response
    # -----------------------------------------------------

    try:
        prediction = json.loads(raw_text)

    except json.JSONDecodeError:

        print()
        print("ERROR: Gemini did not return valid JSON.")

        prediction = {
            "scenario_id": scenario_id,
            "should_abstain": False,
            "dominant_cause": None,
            "affected_region": None,
            "affected_product": None,
            "estimated_impact": None,
            "explanation": (
                "Baseline returned invalid JSON."
            ),
        }

    # -----------------------------------------------------
    # Save prediction
    # -----------------------------------------------------

    output = Path(output_path)
    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(output, "w") as f:
        json.dump(
            prediction,
            f,
            indent=4
        )

    print()
    print(f"Prediction saved to: {output}")


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

    run_baseline(
        data_path=args.data,
        scenario_id=args.scenario_id,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
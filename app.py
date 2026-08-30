import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st


# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Evidence-Backed KPI Investigator",
    page_icon="🔎",
    layout="wide",
)

INCIDENT_START = pd.Timestamp("2026-08-15")

PROJECT_ROOT = Path(__file__).parent

CASE_DIR = PROJECT_ROOT / "benchmark" / "cases"
BASELINE_DIR = PROJECT_ROOT / "benchmark" / "predictions" / "baseline"


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_revenue_metrics(df):
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])

    daily = (
        df.groupby("date", as_index=False)["revenue"]
        .sum()
        .sort_values("date")
    )

    before = daily[daily["date"] < INCIDENT_START]
    after = daily[daily["date"] >= INCIDENT_START]

    before_avg = before["revenue"].mean()
    after_avg = after["revenue"].mean()

    if before_avg:
        drop_pct = ((before_avg - after_avg) / before_avg) * 100
    else:
        drop_pct = 0.0

    return daily, before_avg, after_avg, drop_pct


def extract_review(stdout):
    start_marker = "GEMINI EVIDENCE REVIEW"
    end_marker = "FINAL VERIFIED DECISION"

    if start_marker not in stdout:
        return None

    start = stdout.find(start_marker)
    end = stdout.find(end_marker)

    if end == -1:
        return stdout[start:]

    review = stdout[start:end]

    lines = review.splitlines()

    cleaned = []

    for line in lines:
        if line.strip() in {
            "GEMINI EVIDENCE REVIEW",
            "----------------------",
        }:
            continue

        cleaned.append(line)

    return "\n".join(cleaned).strip()


def run_live_investigation(case_id):
    data_path = CASE_DIR / case_id / "data.csv"

    temp_path = (
        Path(tempfile.gettempdir())
        / f"kpi_investigator_{case_id}.json"
    )

    command = [
        sys.executable,
        str(PROJECT_ROOT / "advanced" / "advanced_agent.py"),
        "--data",
        str(data_path),
        "--scenario-id",
        case_id,
        "--output",
        str(temp_path),
    ]

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        env=os.environ.copy(),
    )

    if result.returncode != 0:
        return None, result.stdout, result.stderr

    prediction = load_json(temp_path)

    try:
        temp_path.unlink()
    except Exception:
        pass

    return prediction, result.stdout, result.stderr


def format_cause(value):
    if value is None:
        return "None"

    return str(value).replace("_", " ").title()


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("🔎 Evidence-Backed KPI Incident Investigator")

st.caption(
    "Turn plausible KPI explanations into evidence-backed decisions — "
    "and abstain when the evidence does not justify a dominant cause."
)

st.divider()


# ---------------------------------------------------------
# BENCHMARK SCORE
# ---------------------------------------------------------

st.subheader("Measured Improvement")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "One-Shot Gemini Baseline",
        "66.67%",
        help="8 correct decisions out of 12 benchmark cases",
    )

with col2:
    st.metric(
        "Evidence-Backed Workflow",
        "100.00%",
        delta="+33.33 pp",
        help="12 correct decisions out of 12 benchmark cases",
    )

with col3:
    st.metric(
        "Baseline Errors Corrected",
        "4 / 4",
        help="Cases 004, 005, 009 and 012",
    )

st.caption(
    "Results are measured on the same controlled 12-case synthetic benchmark "
    "using Gemini 2.5 Flash in both workflows."
)

st.divider()


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.header("Investigation")

case_options = [f"case_{i:03d}" for i in range(1, 13)]

selected_case = st.sidebar.selectbox(
    "Select benchmark incident",
    case_options,
    index=3,
)

st.sidebar.markdown(
    """
### Workflow

1. Detect KPI movement
2. Generate hypotheses
3. Execute mechanism tests
4. Rank evidence
5. Gemini evidence review
6. Deterministic verification
7. Diagnose or abstain
"""
)


# ---------------------------------------------------------
# LOAD SELECTED CASE
# ---------------------------------------------------------

data_path = CASE_DIR / selected_case / "data.csv"
ground_truth_path = CASE_DIR / selected_case / "ground_truth.json"
baseline_path = BASELINE_DIR / f"{selected_case}.json"

df = pd.read_csv(data_path)

daily, before_avg, after_avg, drop_pct = calculate_revenue_metrics(df)


# ---------------------------------------------------------
# INCIDENT OVERVIEW
# ---------------------------------------------------------

st.subheader(f"Incident: {selected_case}")

m1, m2, m3 = st.columns(3)

with m1:
    st.metric(
        "Avg. Daily Revenue Before",
        f"{before_avg:,.2f}",
    )

with m2:
    st.metric(
        "Avg. Daily Revenue After",
        f"{after_avg:,.2f}",
    )

with m3:
    st.metric(
        "Revenue Change",
        f"-{drop_pct:.2f}%",
    )


# ---------------------------------------------------------
# CHART
# ---------------------------------------------------------

st.markdown("### Revenue Timeline")

chart_data = daily.set_index("date")[["revenue"]]

st.line_chart(chart_data)

st.caption(
    "Incident boundary used by the benchmark: 15 August 2026"
)


# ---------------------------------------------------------
# BASELINE
# ---------------------------------------------------------

st.divider()

st.subheader("1. One-Shot LLM Baseline")

if baseline_path.exists():

    baseline = load_json(baseline_path)

    baseline_abstain = baseline.get("should_abstain")

    if baseline_abstain:

        st.info("Baseline decision: ABSTAIN")

    else:

        baseline_cause = format_cause(
            baseline.get("dominant_cause")
        )

        baseline_region = baseline.get(
            "affected_region",
            "Unknown",
        )

        baseline_product = baseline.get(
            "affected_product",
            "Unknown",
        )

        st.write(
            f"**Baseline diagnosis:** "
            f"{baseline_cause} — "
            f"{baseline_region} / {baseline_product}"
        )

    with st.expander("View baseline prediction JSON"):
        st.json(baseline)

else:
    st.warning("Baseline prediction file not found.")


# ---------------------------------------------------------
# ADVANCED WORKFLOW
# ---------------------------------------------------------

st.divider()

st.subheader("2. Evidence-Backed Investigation")

st.write(
    "Run the investigation to generate hypotheses, execute mechanism tests, "
    "compare competing evidence, request an LLM evidence review, and apply "
    "the deterministic verifier."
)


run_button = st.button(
    "🔎 Run Evidence-Backed Investigation",
    type="primary",
    width="stretch",
)


# ---------------------------------------------------------
# LIVE RUN
# ---------------------------------------------------------

if run_button:

    if not os.getenv("GEMINI_API_KEY"):

        st.error(
            "GEMINI_API_KEY is not available in this terminal session."
        )

    else:

        with st.spinner(
            "Executing hypotheses and verifying evidence..."
        ):

            prediction, stdout, stderr = run_live_investigation(
                selected_case
            )

        if prediction is None:

            st.error("Live investigation failed.")

            if stderr:
                st.code(stderr)

        else:

            st.session_state["prediction"] = prediction
            st.session_state["stdout"] = stdout
            st.session_state["active_case"] = selected_case


# ---------------------------------------------------------
# DISPLAY LIVE RESULT
# ---------------------------------------------------------

prediction = None
stdout = None

if (
    st.session_state.get("active_case")
    == selected_case
):

    prediction = st.session_state.get("prediction")
    stdout = st.session_state.get("stdout")


# Do not show an advanced result until a live investigation is run.
# Stored predictions remain available in the repository as benchmark evidence.


if prediction is not None:

    st.markdown("### Final Verified Decision")

    should_abstain = prediction.get(
        "should_abstain",
        False,
    )

    if should_abstain:

        st.warning(
            "⚠️ ABSTAIN — Evidence does not justify "
            "one dominant cause."
        )

        st.write(
            "The workflow found competing or insufficient evidence "
            "and refused to force a single explanation."
        )

    else:

        cause = format_cause(
            prediction.get("dominant_cause")
        )

        region = prediction.get(
            "affected_region",
            "Unknown",
        )

        product = prediction.get(
            "affected_product",
            "Unknown",
        )

        impact = prediction.get(
            "estimated_impact"
        )

        st.success(
            f"✅ DOMINANT CAUSE: {cause}"
        )

        d1, d2, d3 = st.columns(3)

        with d1:
            st.metric(
                "Region",
                region,
            )

        with d2:
            st.metric(
                "Product",
                product,
            )

        with d3:

            if impact is not None:

                st.metric(
                    "Estimated Impact",
                    f"{impact:,.2f}",
                )

            else:

                st.metric(
                    "Estimated Impact",
                    "N/A",
                )


    # -----------------------------------------------------
    # EVIDENCE
    # -----------------------------------------------------

    candidates = prediction.get(
        "evidence_candidates",
        [],
    )

    if candidates:

        st.markdown("### Ranked Evidence")

        evidence_df = pd.DataFrame(candidates)

        display_columns = []

        possible_columns = [
            "cause",
            "region",
            "product",
            "impact",
            "impact_share",
            "mechanism_change_pct",
            "constrained_rows",
        ]

        for column in possible_columns:

            if column in evidence_df.columns:
                display_columns.append(column)

        if display_columns:

            evidence_display = evidence_df[
                display_columns
            ].copy()

            if "impact_share" in evidence_display.columns:

                evidence_display["impact_share"] = (
                    evidence_display["impact_share"] * 100
                ).round(2)

                evidence_display = evidence_display.rename(
                    columns={
                        "impact_share": "impact_share_pct"
                    }
                )

            st.dataframe(
                evidence_display,
                width="stretch",
                hide_index=True,
            )


    # -----------------------------------------------------
    # LLM REVIEW
    # -----------------------------------------------------

    if stdout:

        review = extract_review(stdout)

        if review:

            st.markdown("### Gemini Evidence Review")

            st.info(
                "The LLM review is advisory. "
                "It cannot override the deterministic verifier."
            )

            st.markdown(review)


    # -----------------------------------------------------
    # JSON
    # -----------------------------------------------------

    with st.expander(
        "View final verified prediction JSON"
    ):
        st.json(prediction)


# ---------------------------------------------------------
# GROUND TRUTH
# ---------------------------------------------------------

st.divider()

with st.expander(
    "Benchmark ground truth — evaluation only"
):

    if ground_truth_path.exists():

        ground_truth = load_json(
            ground_truth_path
        )

        st.warning(
            "Ground truth is never passed to the investigator. "
            "It is used only by the benchmark evaluator."
        )

        st.json(ground_truth)


# ---------------------------------------------------------
# DESIGN PRINCIPLE
# ---------------------------------------------------------

st.divider()

st.subheader("Design Principle")

stblockquote = """
**Correlation should generate a hypothesis, not a conclusion.**

The workflow only promotes a KPI movement into an explanation when the
corresponding business mechanism is supported by executable evidence.
When no explanation dominates, abstention is considered a successful
analytical outcome.
"""

st.markdown(stblockquote)


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.caption(
    "Evidence-Backed KPI Incident Investigator · "
    "Gemini 2.5 Flash · Synthetic controlled benchmark"
)
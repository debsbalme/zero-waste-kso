# app.py (updated) — adds an Executive Summary step that uses
# summarize_maturity_gaps_to_bullets() and summarize_recommendations_to_themes()

import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import base64


# Import your existing functions plus the two new helpers
from recommendations import (
    run_recommendation_analysis,
    generate_category_summary,
    generate_bullet_summary,
    identify_top_maturity_gaps,
    identify_top_maturity_drivers,
    matched_recs_to_df,
    summarize_maturity_gaps_to_bullets,
    summarize_recommendations_to_themes
)


# ---------- UI helpers ----------

def display_breadcrumb(step: int):
    steps = [
        "0️⃣ Executive Summary",
        "1️⃣ Category Summary",
        "2️⃣ Bullet Summary",
        "3️⃣ Maturity Gaps",
        "4️⃣ Maturity Drivers",
        "5️⃣ Service Recommendations",
    ]
    breadcrumb = " ➤ ".join([
        f"**{label}**" if i == step else label
        for i, label in enumerate(steps)
    ])
    st.markdown(f"#### Progress: {breadcrumb}")


# ---------- App ----------

def main():
    now = datetime.now()
    formatted_date_time = now.strftime("%Y-%m-%d")

    st.image('acx_logo.png', width=100)
    st.title("Maturity Matrix / Zero Waste Assessment Analysis")
    st.write(f"The current date is: **{formatted_date_time}**")
    st.write(
        "Upload a CSV of the Assessment results and step through: executive summary, category summary, bullets, gaps, drivers, and recommendations."
    )

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            required_columns = ['Category', 'Question', 'Answer', 'Score', 'MaxWeight']
            if not all(col in df.columns for col in required_columns):
                st.error(
                    "The uploaded CSV must contain the following columns: **{}**".format(
                        ", ".join(required_columns)
                    )
                )
                return

            st.success("CSV loaded! Preview below.")
            st.dataframe(df.head(), use_container_width=True)

            if "step" not in st.session_state:
                st.session_state.step = 0

            display_breadcrumb(st.session_state.step)

            # -------------------- STEP 0: EXECUTIVE SUMMARY --------------------
            if st.session_state.step == 0:
                if st.button("0️⃣ Generate Executive Summary"):
                    # Recommendations → themes
                    rec_results = run_recommendation_analysis(df)
                    recs_df = matched_recs_to_df(rec_results)
                    themes_df, themes_md = summarize_recommendations_to_themes(recs_df)

                    # Gaps → bullets
                    gaps_df = identify_top_maturity_gaps(df)
                    gaps_md = summarize_maturity_gaps_to_bullets(gaps_df, per_category_limit=5)

                    # Persist in session
                    st.session_state.exec_rec_results = rec_results
                    st.session_state.exec_recs_df = recs_df
                    st.session_state.exec_themes_df = themes_df
                    st.session_state.exec_themes_md = themes_md
                    st.session_state.exec_gaps_df = gaps_df
                    st.session_state.exec_gaps_md = gaps_md

                    # High-level KPIs
                    st.session_state.exec_total_recs = rec_results.get('total_matched_recommendations', 0)
                    st.session_state.exec_total_score = rec_results.get('total_score', 0.0)
                    st.session_state.exec_total_max = rec_results.get('total_max_score', 0.0)

                    st.session_state.step = 1
                    st.rerun()

            if st.session_state.step >= 0 and "exec_themes_md" in st.session_state:
                st.subheader("0️⃣ Executive Summary")
                kpi_cols = st.columns(3)
                with kpi_cols[0]:
                    st.metric("Total Recs", st.session_state.get("exec_total_recs", 0))
                with kpi_cols[1]:
                    st.metric("Total Score", f"{st.session_state.get('exec_total_score', 0.0):.2f}")
                with kpi_cols[2]:
                    st.metric("Total Max", f"{st.session_state.get('exec_total_max', 0.0):.2f}")

                st.markdown("**Key Recommendation Themes**")
                st.markdown(st.session_state.exec_themes_md)
                with st.expander("Theme Details (table)"):
                    st.dataframe(st.session_state.exec_themes_df, use_container_width=True)

                st.markdown("**Top Maturity Gaps (bulleted)**")
                st.markdown(st.session_state.exec_gaps_md)
                with st.expander("Gaps (raw table)"):
                    st.dataframe(st.session_state.exec_gaps_df, use_container_width=True)

            # -------------------- STEP 1: CATEGORY SUMMARY --------------------
            if st.session_state.step == 1:
                if st.button("1️⃣ Generate Category Summary"):
                    st.session_state.summary_text = generate_category_summary(df)
                    st.session_state.step = 2
                    st.rerun()

            if st.session_state.step >= 2:
                st.subheader("1️⃣ Category Summary")
                st.write(st.session_state.get("summary_text", ""))

            # -------------------- STEP 2: BULLET SUMMARY --------------------
            if st.session_state.step == 2:
                if st.button("2️⃣ Generate Bullet Summary"):
                    st.session_state.bullet_summary = generate_bullet_summary(df)
                    st.session_state.step = 3
                    st.rerun()

            if st.session_state.step >= 3:
                st.subheader("2️⃣ Bullet Point Summary")
                st.write("Copy the text below into your email or document.")
                st.write(st.session_state.get("bullet_summary", ""))

            # -------------------- STEP 3: MATURITY GAPS --------------------
            if st.session_state.step == 3:
                if st.button("3️⃣ Identify Maturity Gaps"):
                    st.session_state.maturity_gap_df = identify_top_maturity_gaps(df)
                    st.session_state.step = 4
                    st.rerun()

            if st.session_state.step >= 4:
                st.subheader("3️⃣ Maturity Gaps")
                st.dataframe(st.session_state.get("maturity_gap_df", pd.DataFrame()), use_container_width=True)

            # -------------------- STEP 4: MATURITY DRIVERS --------------------
            if st.session_state.step == 4:
                if st.button("4️⃣ Identify Maturity Drivers"):
                    st.session_state.maturity_drivers_df = identify_top_maturity_drivers(df)
                    st.session_state.step = 5
                    st.rerun()

            if st.session_state.step >= 5:
                st.subheader("4️⃣ Maturity Drivers")
                st.dataframe(st.session_state.get("maturity_drivers_df", pd.DataFrame()), use_container_width=True)

            # -------------------- STEP 5: SERVICE RECOMMENDATIONS --------------------
            if st.session_state.step == 5:
                if st.button("5️⃣ Compute Service Recommendations"):
                    # Full analysis then flatten to a tidy table
                    results = run_recommendation_analysis(df)
                    st.session_state.recommendations_df = matched_recs_to_df(results)
                    st.session_state.recommendation_results = results
                    st.session_state.step = 6
                    st.rerun()

            if st.session_state.step >= 6:
                st.subheader("5️⃣ Capability / Service Recommendations")
                rec_df = st.session_state.get("recommendations_df", pd.DataFrame())
                if not rec_df.empty:
                    st.dataframe(rec_df, hide_index=True, use_container_width=True)
                    st.write(
                        f"**Total Recommendations:** {st.session_state.get('recommendation_results', {}).get('total_matched_recommendations', len(rec_df))}"
                    )
                else:
                    st.info("No recommendations matched based on the provided data.")

        except Exception as e:
            st.error(f"An error occurred while processing the CSV file: {e}")

    # Reset
    if "step" in st.session_state and st.session_state.step > 0:
        if st.button("🔄 Start Over"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


if __name__ == "__main__":
    main()

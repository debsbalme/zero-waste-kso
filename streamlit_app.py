# app.py — Executive Summary + full flow with Markdown gaps rendering

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

# ---------- Imports from your analysis module ----------
from recommendations import (
    run_recommendation_analysis,
    generate_category_summary,
    generate_bullet_summary,
    identify_top_maturity_gaps,
    identify_top_maturity_drivers,
    matched_recs_to_df,
    summarize_maturity_gaps_to_df,
    summarize_recommendations_to_themes,
    gaps_summary_df_to_markdown,
    align_recommendations_to_gaps,
    alignment_df_to_markdown     # <-- Make sure this helper exists in recommendations.py
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

            # 🔁 Updated: remove Score/MaxWeight from required columns
            required_columns = ['Category', 'Question', 'Answer']
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
                    with st.spinner("Generating Executive Summary..."):
                        # Recommendations → themes
                        rec_results = run_recommendation_analysis(df)
                        recs_df = matched_recs_to_df(rec_results)
                        themes_df, themes_md = summarize_recommendations_to_themes(recs_df)

                        # Gaps → DF then Markdown (Option A)
                        gaps_df = identify_top_maturity_gaps(df)
                        gaps_summary_df = summarize_maturity_gaps_to_df(gaps_df, per_category_limit=5)
                        gaps_md = gaps_summary_df_to_markdown(gaps_summary_df)

                        # Persist in session
                        st.session_state.exec_rec_results = rec_results
                        st.session_state.exec_recs_df = recs_df
                        st.session_state.exec_themes_df = themes_df
                        st.session_state.exec_themes_md = themes_md
                        st.session_state.exec_gaps_df = gaps_df
                        st.session_state.exec_gaps_summary_df = gaps_summary_df
                        st.session_state.exec_gaps_md = gaps_md

                        # Advance
                        st.session_state.step = 1
                    st.rerun()

            if st.session_state.step >= 0 and "exec_themes_md" in st.session_state:
                st.subheader("0️⃣ Executive Summary")

                # Themes (Markdown + table)
                st.markdown(st.session_state.exec_themes_md)
                with st.expander("Theme Details (table)"):
                    st.dataframe(st.session_state.exec_themes_df, use_container_width=True)

                # Gaps (Markdown + parsed summary table + raw table)
                st.markdown("**Top Maturity Gaps (Markdown View)**")
                st.markdown(st.session_state.exec_gaps_md)

                with st.expander("Gaps (parsed summary table)"):
                    st.dataframe(st.session_state.exec_gaps_summary_df, use_container_width=True)

                with st.expander("Gaps (raw table)"):
                    st.dataframe(st.session_state.exec_gaps_df, use_container_width=True)

            # -------------------- STEP 1: CATEGORY SUMMARY --------------------
            if st.session_state.step == 1:
                if st.button("1️⃣ Generate Category Summary"):
                    with st.spinner("Generating Category Summary..."):
                        st.session_state.summary_text = generate_category_summary(df)
                        st.session_state.step = 2
                    st.rerun()

            if st.session_state.step >= 2:
                st.subheader("1️⃣ Category Summary")
                st.write(st.session_state.get("summary_text", ""))

            # -------------------- STEP 2: BULLET SUMMARY --------------------
            if st.session_state.step == 2:
                if st.button("2️⃣ Generate Bullet Summary"):
                    with st.spinner("Generating Bullet Summary..."):
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
                    with st.spinner("Identifying Maturity Gaps..."):
                        st.session_state.maturity_gap_df = identify_top_maturity_gaps(df)
                        st.session_state.step = 4
                    st.rerun()

            if st.session_state.step >= 4:
                st.subheader("3️⃣ Maturity Gaps")
                st.dataframe(st.session_state.get("maturity_gap_df", pd.DataFrame()), use_container_width=True)

                # Optional: show the Markdown-parsed themes here as well
                mg_df = st.session_state.get("maturity_gap_df", pd.DataFrame())
                if not mg_df.empty:
                    parsed_df = summarize_maturity_gaps_to_df(mg_df, per_category_limit=5)
                    st.markdown("**Maturity Gap Themes (Markdown View)**")
                    st.markdown(gaps_summary_df_to_markdown(parsed_df))

            # -------------------- STEP 4: MATURITY DRIVERS --------------------
            if st.session_state.step == 4:
                if st.button("4️⃣ Identify Maturity Drivers"):
                    with st.spinner("Identifying Maturity Drivers..."):
                        st.session_state.maturity_drivers_df = identify_top_maturity_drivers(df)
                        st.session_state.step = 5
                    st.rerun()

            if st.session_state.step >= 5:
                st.subheader("4️⃣ Maturity Drivers")
                st.dataframe(st.session_state.get("maturity_drivers_df", pd.DataFrame()), use_container_width=True)

            # -------------------- STEP 5: SERVICE RECOMMENDATIONS --------------------
# -------------------- STEP 5: SERVICE RECOMMENDATIONS (Alignment Only) --------------------
            if st.session_state.step == 5:
                if st.button("5️⃣ Compute Service Recommendations → Gap Alignment"):
                    with st.spinner("Aligning recommendations to maturity gaps..."):
                        # 1) Compute recommendations (no-score version)
                        rec_results = run_recommendation_analysis(df)

                        # 2) Ensure gaps exist (prefer the Exec Summary gaps if already computed)
                        gaps_df = st.session_state.get("exec_gaps_df")
                        if gaps_df is None or gaps_df.empty:
                            gaps_df = identify_top_maturity_gaps(df)

                        # 3) Align recommendations to gaps
                        align_df = align_recommendations_to_gaps(
                            rec_results=rec_results,
                            gaps_df=gaps_df
                        )

                        # 4) Persist for display
                        st.session_state.alignment_df = align_df
                        st.session_state.step = 6
                    st.rerun()


                if st.session_state.step >= 6:
                    st.subheader("5️⃣ Recommendation → Gap Alignment")

                    align_df = st.session_state.get("alignment_df", pd.DataFrame())
                    if align_df is None or align_df.empty:
                        st.info("No alignment results available. Try recomputing after generating gaps and recommendations.")
                    else:
                        # Tabular view
                        st.dataframe(align_df, use_container_width=True, hide_index=True)

                        # Readable Markdown view
                        st.markdown("**Readable Alignment (Markdown View)**")
                        st.markdown(alignment_df_to_markdown(align_df))


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

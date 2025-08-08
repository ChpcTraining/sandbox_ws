
import os
import pandas as pd
import streamlit as st
from pathlib import Path
from io import StringIO

st.set_page_config(page_title="Admin Viewer", layout="wide")
st.title("📂 Admin: View Student Submissions")

# Directory to look for CSV submissions (one folder up from /pages)
SUBMISSION_DIR = Path(__file__).resolve().parent.parent
csv_files = sorted([f for f in os.listdir(SUBMISSION_DIR) if f.endswith("_results.csv")])

APP_DIR = Path(__file__).resolve().parent.parent  # one up from /pages

if not csv_files:
    st.warning("No submission CSV files found.")
else:
    selected_file = st.selectbox("📄 Select a submission file:", csv_files)

    if selected_file:
        st.markdown(f"### Showing: `{selected_file}`")

        # Read the file and split metadata + results
        with open(SUBMISSION_DIR / selected_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Parse metadata
        meta = {}
        results_start = 0
        for i, line in enumerate(lines):
            if line.strip() == "":
                results_start = i + 1
                break
            key, val = line.strip().split(",", 1)
            meta[key] = val

        # Load and show results table
        result_csv_str = "".join(lines[results_start:])
        df = pd.read_csv(StringIO(result_csv_str))
        st.subheader("📊 Results Table")
        st.dataframe(df, use_container_width=True)

        # --- Score input for Results Table ---
        score_results_table = st.number_input(
            "Score: Results Table",
            min_value=0.0, step=0.5, value=0.0, key="score_results_table"
        )

        # Show metadata with previews and scoring inputs
        st.subheader("📌 Metadata")

        # Keep references to scores we want to sum
        score_q1 = score_q1_expl = score_q2 = score_q3 = 0.0
        score_time_plot = score_speedup_plot = 0.0

        # Render metadata nicely + images + scoring inputs after the relevant rows
        for key, val in meta.items():
            if key.endswith("_path") and val:
                rel_path = val.replace("\\", "/")
                abs_path = (APP_DIR / rel_path).resolve()
                st.markdown(f"- **{key}**: [Open File]({abs_path})")

                # Show preview if it's an image
                if abs_path.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                    st.image(abs_path, caption=key, use_column_width=True)

                # Add scoring inputs for the two plot paths
                if key == "time_vs_p_plot_path":
                    score_time_plot = st.number_input(
                        "Score: time_vs_p_plot_path",
                        min_value=0.0, step=0.5, value=0.0, key="score_time_vs_plot_path"
                    )
                if key == "speedup_vs_p_plot_path":
                    score_speedup_plot = st.number_input(
                        "Score: speedup_vs_p_plot_path",
                        min_value=0.0, step=0.5, value=0.0, key="score_speedup_vs_plot_path"
                    )
            else:
                # Regular text metadata
                st.markdown(f"- **{key}**: {val}")

                # Add scoring inputs for q1 / q1_expl / q2 / q3 after each appears
                if key == "q1":
                    score_q1 = st.number_input(
                        "Score: q1",
                        min_value=0.0, step=0.5, value=0.0, key="score_q1"
                    )
                elif key == "q1_expl":
                    score_q1_expl = st.number_input(
                        "Score: q1_expl",
                        min_value=0.0, step=0.5, value=0.0, key="score_q1_expl"
                    )
                elif key == "q2":
                    score_q2 = st.number_input(
                        "Score: q2",
                        min_value=0.0, step=0.5, value=0.0, key="score_q2"
                    )
                elif key == "q3":
                    score_q3 = st.number_input(
                        "Score: q3",
                        min_value=0.0, step=0.5, value=0.0, key="score_q3"
                    )

        # --- Calculate total button ---
# --- Calculate total button ---
        total = None
        if st.button("🧮 Calculate Total"):
            total = (
                score_results_table
                + score_q1 + score_q1_expl + score_q2 + score_q3
                + score_time_plot + score_speedup_plot
            )
            st.success(f"Total Score: **{total}**")
            person_email = meta.get("email", "unknown")
            # If file exists, load and append
            if os.path.exists("student_grades.csv"):
                grades_df = pd.read_csv("student_grades.csv")
                next_id = int(grades_df["#"].max()) + 1 if not grades_df.empty else 1
            else:
                grades_df = pd.DataFrame(columns=["#", "person", "grade"])
                next_id = 1

            # Append new row
            grades_df = pd.concat([
                grades_df,
                pd.DataFrame([{"#": next_id, "person": person_email, "grade": total}])
            ], ignore_index=True)

            # Save updated file
            grades_df.to_csv("student_grades.csv", index=False)
            st.success(f"Saved Score: **{total}**")

  

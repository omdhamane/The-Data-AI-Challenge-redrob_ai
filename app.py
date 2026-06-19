from __future__ import annotations

import csv
import tempfile
from pathlib import Path

import streamlit as st

from rank import rank_candidates, write_submission


st.set_page_config(page_title="Redrob Candidate Ranker", layout="wide")
st.title("Redrob Candidate Ranker")

uploaded = st.file_uploader("Upload candidates.jsonl or candidates.jsonl.gz", type=["jsonl", "gz"])
limit = st.slider("Rows to rank", min_value=10, max_value=100, value=25, step=5)

if uploaded:
    suffix = ".jsonl.gz" if uploaded.name.endswith(".gz") else ".jsonl"
    with tempfile.TemporaryDirectory() as tmp:
        candidates_path = Path(tmp) / f"candidates{suffix}"
        out_path = Path(tmp) / "ranked_candidates.csv"
        candidates_path.write_bytes(uploaded.getvalue())

        rows = rank_candidates(candidates_path, limit=limit)
        write_submission(rows, out_path)

        with out_path.open("r", encoding="utf-8", newline="") as handle:
            preview = list(csv.DictReader(handle))

        st.dataframe(preview, use_container_width=True, hide_index=True)
        st.download_button(
            "Download ranked CSV",
            data=out_path.read_bytes(),
            file_name="ranked_candidates.csv",
            mime="text/csv",
        )
else:
    st.info("Upload a small candidate sample to run the same deterministic ranker used for the full submission.")

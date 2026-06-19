#!/usr/bin/env python3
"""Print raw profile facts for candidates selected in a submission CSV."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
from pathlib import Path
from typing import Any, Iterable


def open_records(path: Path) -> Iterable[dict[str, Any]]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--submission", required=True, type=Path)
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()

    with args.submission.open("r", encoding="utf-8", newline="") as handle:
        selected = list(csv.DictReader(handle))[: args.top]

    ids = {row["candidate_id"] for row in selected}
    records = {row["candidate_id"]: row for row in open_records(args.candidates) if row["candidate_id"] in ids}

    for row in selected:
        record = records[row["candidate_id"]]
        profile = record["profile"]
        signals = record["redrob_signals"]
        skills = ", ".join(skill["name"] for skill in record.get("skills", [])[:8])
        print(
            f"{row['rank']:>3} {row['candidate_id']} {row['score']} | "
            f"{profile['current_title']} | {profile['years_of_experience']} yrs | "
            f"{profile['current_company']} / {profile['current_industry']} | {profile['location']} | "
            f"response={signals['recruiter_response_rate']} notice={signals['notice_period_days']} "
            f"github={signals['github_activity_score']} | skills: {skills}"
        )


if __name__ == "__main__":
    main()

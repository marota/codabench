#!/usr/bin/env python3
# Copyright (c) 2025-2026, RTE (https://www.rte-france.com)
# SPDX-License-Identifier: MPL-2.0
"""Run the Co-Study4Grid scoring program locally, the way Codabench's compute
worker would.

It lays out a temporary ``input/`` with ``res/`` (the submission) and ``ref/``
(reference data), invokes ``ingestion_program/ingestion.py`` then
``scoring_program/score.py``, and prints the resulting ``scores.json``.

Usage:
    python3 run_local.py <game_session.json> [--no-ingestion]
    python3 run_local.py            # defaults to the starting-kit sample
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
DEFAULT_SUB = os.path.join(BUNDLE, "starting_kit", "sample_submission", "game_session.json")
REFERENCE = os.path.join(BUNDLE, "reference_data", "reference.json")
SCORE_PY = os.path.join(BUNDLE, "scoring_program", "score.py")
INGEST_PY = os.path.join(BUNDLE, "ingestion_program", "ingestion.py")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("submission", nargs="?", default=DEFAULT_SUB)
    ap.add_argument("--no-ingestion", action="store_true",
                    help="score the submission directly without the ingestion pass")
    args = ap.parse_args()

    if not os.path.isfile(args.submission):
        sys.exit(f"submission not found: {args.submission}")

    work = tempfile.mkdtemp(prefix="cs4g_codabench_")
    try:
        input_dir = os.path.join(work, "input")
        res_dir = os.path.join(input_dir, "res")
        ref_dir = os.path.join(input_dir, "ref")
        out_dir = os.path.join(work, "output")
        for d in (res_dir, ref_dir, out_dir):
            os.makedirs(d, exist_ok=True)

        shutil.copy(args.submission, os.path.join(res_dir, "game_session.json"))
        if os.path.isfile(REFERENCE):
            shutil.copy(REFERENCE, os.path.join(ref_dir, "reference.json"))

        if not args.no_ingestion:
            ingest_out = os.path.join(work, "ingested")
            os.makedirs(ingest_out, exist_ok=True)
            print("=== ingestion ===")
            subprocess.run(
                [sys.executable, INGEST_PY, ref_dir, ingest_out, "", res_dir],
                check=True,
            )
            # Feed the ingested prediction back in as the submission.
            shutil.copy(os.path.join(ingest_out, "game_session.json"),
                        os.path.join(res_dir, "game_session.json"))

        print("=== scoring ===")
        subprocess.run([sys.executable, SCORE_PY, input_dir, out_dir], check=True)

        scores_path = os.path.join(out_dir, "scores.json")
        with open(scores_path, encoding="utf-8") as fh:
            scores = json.load(fh)
        print("=== scores.json ===")
        print(json.dumps(scores, indent=2))
        html = os.path.join(out_dir, "detailed_results.html")
        if os.path.isfile(html):
            print(f"detailed_results.html written ({os.path.getsize(html)} bytes)")
        return scores
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()

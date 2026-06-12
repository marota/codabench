#!/usr/bin/env python3
# Copyright (c) 2025-2026, RTE (https://www.rte-france.com)
# SPDX-License-Identifier: MPL-2.0
"""Codabench ingestion program for the Co-Study4Grid Game Mode competition.

This competition is primarily a **result submission**: the participant uploads
the ``game_session.json`` their Co-Study4Grid Game Mode session produced. There
is no agent to execute, so ingestion is a light validation + normalisation pass
that hands a clean prediction file to the scoring program.

Codabench invocation (see metadata.yaml):
    python3 ingestion.py /app/input_data/ /app/output/ /app/program /app/ingested_program

For a code-submission variant (an automated agent playing the studies), this is
where you would import the participant's module and drive it against the
official study manifest in ``input_data``. That path is intentionally left as a
documented extension point below.
"""
import json
import os
import sys


def _looks_like_session(obj):
    return isinstance(obj, dict) and "studies" in obj and (
        "schemaVersion" in obj or "sessionName" in obj
    )


def find_session(*search_dirs):
    for base in search_dirs:
        if not base or not os.path.isdir(base):
            continue
        for root, _dirs, files in os.walk(base):
            for fn in sorted(files):
                if fn.endswith(".json"):
                    try:
                        with open(os.path.join(root, fn), encoding="utf-8") as fh:
                            obj = json.load(fh)
                    except (ValueError, OSError):
                        continue
                    if _looks_like_session(obj):
                        return obj
    return None


def main():
    input_data = sys.argv[1] if len(sys.argv) > 1 else "/app/input_data"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "/app/output"
    submission_dir = sys.argv[4] if len(sys.argv) > 4 else "/app/ingested_program"
    os.makedirs(output_dir, exist_ok=True)

    # The submission file may be mounted as the program (code submission) or
    # provided directly as the result file; search both.
    session = find_session(submission_dir, input_data, os.environ.get("SUBMISSION_DIR"))
    if session is None:
        sys.stderr.write("ingestion: no game_session.json found; writing empty prediction\n")
        session = {"schemaVersion": "1.0", "sessionName": "empty", "studies": []}

    n = len(session.get("studies", []))
    print(f"ingestion: validated session '{session.get('sessionName')}' with {n} studies")

    out = os.path.join(output_dir, "game_session.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(session, fh)
    print(f"ingestion: wrote prediction -> {out}")


if __name__ == "__main__":
    main()

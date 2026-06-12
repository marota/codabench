#!/usr/bin/env python3
# Copyright (c) 2025-2026, RTE (https://www.rte-france.com)
# SPDX-License-Identifier: MPL-2.0
"""Codabench scoring program for the Co-Study4Grid Game Mode competition.

A submission is a ``game_session.json`` exported by the Co-Study4Grid Game
Mode UI (schema in ``frontend/src/game/types.ts`` / ``gameLog.ts``). Each
session records, per study, the contingency the player faced, the remedial
actions they committed (max 3), the worst line loading they achieved, and how
long they took.

This scorer is the Python twin of ``frontend/src/game/scoring.ts`` — the two
MUST stay numerically identical. Per study (0..100):

    physical = 60 * remediation_fraction
    actions  = 25 * remediation_fraction * action_efficiency
    time     = 15 * remediation_fraction * time_efficiency

Session score = mean of per-study scores.

Codabench invocation (see metadata.yaml):
    python3 score.py /app/input/ /app/output/

``/app/input`` contains ``res/`` (the participant submission) and ``ref/``
(reference data). The scorer also runs standalone for local testing:
    python3 score.py <input_dir> <output_dir>
"""
import json
import os
import sys

WEIGHTS = {"physical": 60.0, "actions": 25.0, "time": 15.0}


def clamp01(x):
    return max(0.0, min(1.0, x))


# --- per-study metrics (mirror of scoring.ts) ------------------------------

def remediation_fraction(s):
    final = s.get("finalMaxRho")
    if final is None:
        return 0.0
    if s.get("solved") or final < 1.0:
        return 1.0
    baseline = s.get("baselineMaxRho")
    if baseline is None or baseline <= 1.0:
        return 1.0 if s.get("solved") else 0.0
    return clamp01((baseline - final) / (baseline - 1.0))


def action_efficiency(s):
    n = s.get("numActions", 0)
    if n < 1:
        return 0.0
    span = max(1, s.get("maxActions", 3))
    return clamp01(1.0 - (n - 1) / span)


def time_efficiency(s):
    limit_ms = s.get("timeLimitSeconds", 0) * 1000.0
    if limit_ms <= 0:
        return 0.0
    return clamp01(1.0 - s.get("durationMs", 0) / limit_ms)


def score_study(s):
    frac = remediation_fraction(s)
    physical = WEIGHTS["physical"] * frac
    actions = WEIGHTS["actions"] * frac * action_efficiency(s)
    time = WEIGHTS["time"] * frac * time_efficiency(s)
    return {
        "studyId": s.get("studyId"),
        "physical": physical,
        "actions": actions,
        "time": time,
        "total": physical + actions + time,
        "remediationFraction": frac,
        "solved": bool(s.get("solved")),
    }


# --- submission validation against reference -------------------------------

def apply_reference(session, reference):
    """Cross-check the submission against the official manifest.

    The reference pins the allowed action cap and the official baseline per
    study, so a participant cannot inflate their score by under-reporting the
    contingency severity or over-spending actions. Returns a list of
    integrity warnings (non-fatal).
    """
    warnings = []
    if not reference:
        return warnings

    max_allowed = reference.get("maxActionsAllowed")
    ref_by_id = {st["studyId"]: st for st in reference.get("studies", [])}

    for s in session.get("studies", []):
        # Clamp committed actions to the official cap.
        if max_allowed is not None and s.get("maxActions", 0) > max_allowed:
            warnings.append(
                f"study {s.get('studyId')}: maxActions {s.get('maxActions')} "
                f"exceeds official cap {max_allowed}; clamped"
            )
            s["maxActions"] = max_allowed
        if max_allowed is not None and s.get("numActions", 0) > max_allowed:
            s["numActions"] = max_allowed

        # Trust the official baseline when the submission omits / lowballs it.
        ref = ref_by_id.get(s.get("studyId"))
        if ref and ref.get("baselineMaxLoadingPct") is not None:
            ref_baseline = ref["baselineMaxLoadingPct"] / 100.0
            if s.get("baselineMaxRho") is None or s["baselineMaxRho"] < ref_baseline:
                s["baselineMaxRho"] = ref_baseline
    return warnings


# --- IO helpers ------------------------------------------------------------

def _looks_like_session(obj):
    return isinstance(obj, dict) and "studies" in obj and (
        "schemaVersion" in obj or "sessionName" in obj
    )


def find_submission(input_dir):
    """Locate the participant's game_session.json under the input dir."""
    candidates = [
        os.path.join(input_dir, "res"),
        input_dir,
        os.path.join(input_dir, "input", "res"),
    ]
    for base in candidates:
        if not os.path.isdir(base):
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
                        return obj, os.path.join(root, fn)
    return None, None


def find_reference(input_dir):
    """Locate reference.json under input/ref, or the bundled fallback."""
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(input_dir, "ref", "reference.json"),
        os.path.join(input_dir, "reference.json"),
        os.path.join(here, "..", "reference_data", "reference.json"),
        os.path.join(here, "reference.json"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as fh:
                return json.load(fh)
    return None


HTML_TEMPLATE = """<!doctype html><html><head><meta charset="utf-8">
<title>Co-Study4Grid Game — results</title>
<style>body{{font-family:system-ui,sans-serif;margin:24px;color:#222}}
h1{{color:#0a6}}table{{border-collapse:collapse;width:100%}}
th,td{{border:1px solid #ddd;padding:6px 10px;font-size:14px;text-align:left}}
th{{background:#f3f3f3}}.big{{font-size:40px;font-weight:800;color:#0a6}}</style>
</head><body>
<h1>Session: {session}</h1>
<p>Player: <b>{player}</b> · Final score: <span class="big">{final:.1f}</span> / 100
 · Solved {solved}/{n} studies</p>
<table><tr><th>#</th><th>Study</th><th>Solved</th><th>Baseline→Final</th>
<th>Actions</th><th>Time</th><th>Score</th></tr>{rows}</table>
{warn}</body></html>"""


def render_html(session, per_study, agg, warnings):
    rows = []
    studies = session.get("studies", [])
    for i, (s, sc) in enumerate(zip(studies, per_study)):
        def pct(v):
            return "—" if v is None else f"{v * 100:.0f}%"
        rows.append(
            "<tr><td>{i}</td><td>{label}</td><td>{solved}</td>"
            "<td>{b}&rarr;{f}</td><td>{na}/{ma}</td><td>{t:.0f}s/{tl}s</td>"
            "<td><b>{score:.1f}</b></td></tr>".format(
                i=i + 1, label=s.get("label", s.get("studyId", "?")),
                solved="✓" if s.get("solved") else "✗",
                b=pct(s.get("baselineMaxRho")), f=pct(s.get("finalMaxRho")),
                na=s.get("numActions", 0), ma=s.get("maxActions", 0),
                t=s.get("durationMs", 0) / 1000.0, tl=s.get("timeLimitSeconds", 0),
                score=sc["total"],
            )
        )
    warn = ""
    if warnings:
        warn = "<h3>Integrity notes</h3><ul>" + "".join(
            f"<li>{w}</li>" for w in warnings) + "</ul>"
    return HTML_TEMPLATE.format(
        session=session.get("sessionName", "session"),
        player=session.get("player") or "anonymous",
        final=agg["final_score"], solved=agg["solved_count"],
        n=agg["n_studies"], rows="".join(rows), warn=warn,
    )


def main():
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "/app/input"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "/app/output"
    os.makedirs(output_dir, exist_ok=True)

    session, sub_path = find_submission(input_dir)
    if session is None:
        sys.stderr.write(f"ERROR: no game_session.json found under {input_dir}\n")
        # Emit a zero score so the leaderboard still records the attempt.
        with open(os.path.join(output_dir, "scores.json"), "w", encoding="utf-8") as fh:
            json.dump({"final_score": 0, "solved_count": 0,
                       "avg_actions": 0, "avg_time_s": 0}, fh)
        sys.exit(1)

    print(f"Scoring submission: {sub_path}")
    reference = find_reference(input_dir)
    warnings = apply_reference(session, reference)

    studies = session.get("studies", [])
    per_study = [score_study(s) for s in studies]
    n = len(per_study)
    final_score = sum(p["total"] for p in per_study) / n if n else 0.0
    solved_count = sum(1 for s in studies if s.get("solved"))
    avg_actions = sum(s.get("numActions", 0) for s in studies) / n if n else 0.0
    avg_time_s = sum(s.get("durationMs", 0) for s in studies) / 1000.0 / n if n else 0.0

    agg = {
        "final_score": round(final_score, 4),
        "solved_count": solved_count,
        "n_studies": n,
        "avg_actions": round(avg_actions, 3),
        "avg_time_s": round(avg_time_s, 2),
    }

    with open(os.path.join(output_dir, "scores.json"), "w", encoding="utf-8") as fh:
        json.dump({
            "final_score": agg["final_score"],
            "solved_count": agg["solved_count"],
            "avg_actions": agg["avg_actions"],
            "avg_time_s": agg["avg_time_s"],
        }, fh)

    with open(os.path.join(output_dir, "detailed_results.html"), "w", encoding="utf-8") as fh:
        fh.write(render_html(session, per_study, agg, warnings))

    for w in warnings:
        print(f"WARNING: {w}")
    print(f"final_score={agg['final_score']} solved={solved_count}/{n} "
          f"avg_actions={agg['avg_actions']} avg_time_s={agg['avg_time_s']}")


if __name__ == "__main__":
    main()

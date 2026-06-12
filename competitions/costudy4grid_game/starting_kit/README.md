# Starting kit — Co-Study4Grid N-1 Remediation Challenge

This kit shows you exactly what to submit and how it is scored.

## What you submit

A single `game_session.json` exported from Co-Study4Grid **Game Mode**:

1. Run the Co-Study4Grid app with `?game=1`.
2. Play the session (solve each N-1 study with ≤ 3 actions before the timer).
3. On the results screen click **⬇ JSON (Codabench)**.
4. Upload that file as your submission.

A working example is in [`sample_submission/game_session.json`](sample_submission/game_session.json).

## Try the scoring locally

From the bundle root:

```bash
python3 local_harness/run_local.py starting_kit/sample_submission/game_session.json
```

You should see:

```json
{ "final_score": 69.1111, "solved_count": 2, "avg_actions": 1.333, "avg_time_s": 133.33 }
```

## How it's scored

Per study (0–100): **60 %** physical result · **25 %** action economy · **15 %**
speed; session score is the mean. Full formula in
[`../evaluation.md`](../evaluation.md). The Python scorer
(`../scoring_program/score.py`) is the exact twin of the in-app preview
(`frontend/src/game/scoring.ts`).

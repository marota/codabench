# Evaluation

Each study is scored from **0 to 100** and the session score is the **mean**
across all studies. The exact computation lives in
`scoring_program/score.py` and is mirrored byte-for-byte by the UI preview
(`frontend/src/game/scoring.ts`).

## Per-study score

```
score = 60 · R  +  25 · R · A  +  15 · R · T
```

where:

### R — remediation fraction (the physical result)
How much of the overload you removed.

- `R = 1.0` if the worst monitored line is back **under 100 %** (`finalMaxRho < 1.0`).
- Otherwise partial credit, linear between the baseline overload and the 100 %
  target: `R = clamp01((baselineMaxRho − finalMaxRho) / (baselineMaxRho − 1.0))`.
- `R = 0` if you took no action or made things worse.

This is the dominant term (max 60 pts): an unsolved study can score points for
partial relief, but only a real fix earns the full physical weight.

### A — action efficiency
Rewards using **fewer** of your allowed actions.

```
A = clamp01(1 − (numActions − 1) / maxActions)
```

1 action → `A = 1`; using all 3 → `A ≈ 0.33`.

### T — time efficiency
Rewards finishing well inside the time limit.

```
T = clamp01(1 − durationMs / (timeLimitSeconds · 1000))
```

A timed-out study has `T ≈ 0`.

Note that `A` and `T` are **multiplied by R**: speed and economy only count when
you actually relieved the constraint.

## Integrity checks

The reference manifest pins the official **action cap (3)** and the **baseline
overload** per study. The scorer clamps any over-cap action count and trusts the
official baseline if a submission under-reports it, so the leaderboard can't be
gamed by editing the exported JSON.

## Leaderboard columns

| Column | Key | Sort |
|---|---|---|
| Final score | `final_score` | desc |
| Studies solved | `solved_count` | desc |
| Avg actions | `avg_actions` | asc |
| Avg time (s) | `avg_time_s` | asc |

# Co-Study4Grid — N-1 Remediation Challenge (Codabench bundle)

A [Codabench](https://www.codabench.org/) competition that scores recorded
**Co-Study4Grid Game Mode** sessions: players (human or agent) remediate N-1
contingencies on the PyPSA-EUR France 225/400 kV grid with ≤ 3 remedial actions
under a time limit. See [`overview.md`](overview.md), [`evaluation.md`](evaluation.md),
and [`data.md`](data.md) for the participant-facing pages.

## Layout

```
costudy4grid_game/
├── competition.yaml          # Codabench bundle manifest (phases, tasks, leaderboard)
├── overview.md / evaluation.md / data.md / terms.md
├── logo.png
├── scoring_program/
│   ├── score.py              # scorer — twin of frontend/src/game/scoring.ts
│   ├── metadata.yaml         # command: python3 score.py /app/input /app/output
│   └── test_score.py         # pytest unit tests for the formula
├── ingestion_program/
│   ├── ingestion.py          # validates + normalises the submitted session
│   └── metadata.yaml
├── reference_data/
│   └── reference.json        # official study manifest (cap + baselines)
├── starting_kit/
│   ├── README.md
│   └── sample_submission/game_session.json
├── local_harness/
│   └── run_local.py          # run ingestion+scoring exactly like the compute worker
├── package.sh                # build the uploadable bundle zip
└── pytest.ini
```

## Build the uploadable bundle

```bash
./package.sh        # → dist/costudy4grid_game_bundle.zip
```

Upload `dist/costudy4grid_game_bundle.zip` via **Benchmark → Management → Upload**
on a Codabench instance.

## Test it locally (no Codabench server needed)

```bash
# Score the bundled sample submission the way the compute worker would:
python3 local_harness/run_local.py
# → final_score=69.1111, solved_count=2 ...

# Run the scorer unit tests:
python3 -m pytest         # uses the local pytest.ini
```

The scoring formula (`score.py`) is kept numerically identical to the in-app
preview (`frontend/src/game/scoring.ts` in the Co-Study4Grid repo); both are
locked by unit tests.

## Submission format

A `game_session.json` exported from Co-Study4Grid Game Mode (`?game=1` → play →
**⬇ JSON (Codabench)**). Schema documented in [`data.md`](data.md).

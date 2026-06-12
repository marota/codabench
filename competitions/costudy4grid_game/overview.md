# Co-Study4Grid — N-1 Remediation Challenge

This competition ranks **grid operators** (human or agent) on how well they
remediate **N-1 contingencies** on a real European transmission grid, using the
[Co-Study4Grid](https://github.com/marota/Expert_op4grid_recommender) study tool
in **Game Mode**.

## The task

Each *study* trips a single line on the **PyPSA-EUR France 225/400 kV** network.
Losing that line overloads at least one monitored line beyond **100 %** of its
thermal limit. Your job, for every study:

1. Read the post-contingency overflow.
2. Pick **at most 3 remedial actions** (topology change, line opening, PST tap,
   curtailment, load shedding) to bring every monitored line back **under 100 %**.
3. Do it **before the timer runs out**.

## How to play

1. Launch Co-Study4Grid in **Game Mode**: open the app with `?game=1`.
2. Configure or accept the official session, then solve each study.
3. When the session ends, click **⬇ JSON (Codabench)** to download your
   `game_session.json`.
4. Submit that file here.

## Scoring (0–100, higher is better)

Per study: **60 %** physical result · **25 %** action economy · **15 %** speed.
Your session score is the mean across studies. See **Evaluation** for the exact
formula.

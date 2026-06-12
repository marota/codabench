# Data

## Network

**PyPSA-EUR France 225/400 kV** (`data/pypsa_eur_fr225_400/network.xiidm` in the
Co-Study4Grid repo). A realistic reduced model of the French transmission grid
with 225 kV and 400 kV levels, OpenStreetMap-derived geography, and a curated
remedial-action catalogue (`actions.json`).

## Official study set

8 single-line N-1 contingencies, each producing a worst-case **130 %** line
loading. They are listed in `reference_data/reference.json`:

| # | Contingency | Region |
|---|---|---|
| s1 | BATZEL61MARL6 | Marlenheim 225 kV |
| s2 | Champagnier - Prunières | Champagnier 225 kV |
| s3 | Belle-Épine - Domloup | B.Épine 225 kV |
| s4 | way/121500507 | Biancon 225 kV |
| s5 | B.MONL61VALE8 | Valence 225 kV |
| s6 | CUPERL61VESLE | Vesle 225 kV |
| s7 | Le Cheylas - Grande Île 1 | Cheylas 400 kV |
| s8 | Liers - Villejust | Villejust 225 kV |

These are drawn from `data/pypsa_eur_fr225_400/n1_overload_contingencies.json`,
the pre-computed catalogue of overload-producing N-1 events on this grid.

## Submission format

A single `game_session.json` exported by Co-Study4Grid Game Mode. Schema (see
`frontend/src/game/types.ts`):

```json
{
  "schemaVersion": "1.0",
  "sessionName": "…",
  "player": "…",
  "config": { "timerSeconds": 180, "maxActions": 3, "nStudies": 3 },
  "studies": [
    {
      "studyId": "s1",
      "contingencyElementId": "relation_9259308_b-225",
      "durationMs": 65000,
      "timedOut": false,
      "timeLimitSeconds": 180,
      "maxActions": 3,
      "numActions": 1,
      "baselineMaxRho": 1.30,
      "finalMaxRho": 0.94,
      "solved": true,
      "actionsChosen": [ { "actionId": "…", "maxRho": 0.94, "solved": true } ]
    }
  ]
}
```

`maxRho` / `finalMaxRho` / `baselineMaxRho` are **per-unit** line loadings
(`1.0 == 100 %`). A sample submission lives in `starting_kit/sample_submission/`.

# Copyright (c) 2025-2026, RTE (https://www.rte-france.com)
# SPDX-License-Identifier: MPL-2.0
"""Unit tests locking the Co-Study4Grid scoring formula.

Run with:  python3 -m pytest competitions/costudy4grid_game/scoring_program/
"""
import importlib.util
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("score", os.path.join(HERE, "score.py"))
score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)


def study(**kw):
    base = dict(
        studyId="s", numActions=1, maxActions=3, durationMs=0,
        timeLimitSeconds=180, baselineMaxRho=1.30, finalMaxRho=0.9, solved=True,
    )
    base.update(kw)
    return base


def test_perfect_study_scores_100():
    s = study(finalMaxRho=0.9, solved=True, numActions=1, durationMs=0)
    sc = score.score_study(s)
    assert sc["total"] == pytest.approx(100.0)


def test_no_action_scores_zero():
    s = study(numActions=0, finalMaxRho=None, solved=False)
    sc = score.score_study(s)
    assert sc["total"] == pytest.approx(0.0)


def test_partial_relief_gets_physical_credit_only_when_unsolved():
    # baseline 1.30, final 1.18 -> R = 0.12/0.30 = 0.4
    s = study(solved=False, finalMaxRho=1.18, numActions=1, durationMs=180000,
              timeLimitSeconds=180)
    sc = score.score_study(s)
    assert sc["remediationFraction"] == pytest.approx(0.4)
    # 60*0.4 + 25*0.4*1 + 15*0.4*0 = 24 + 10 + 0
    assert sc["total"] == pytest.approx(34.0)


def test_action_economy_penalizes_more_actions():
    one = score.score_study(study(numActions=1, durationMs=0))
    three = score.score_study(study(numActions=3, durationMs=0))
    assert one["actions"] == pytest.approx(25.0)
    assert three["actions"] == pytest.approx(25.0 * (1 - 2 / 3))
    assert one["total"] > three["total"]


def test_time_efficiency_penalizes_slow_solves():
    fast = score.score_study(study(durationMs=0))
    slow = score.score_study(study(durationMs=180000, timeLimitSeconds=180))
    assert fast["time"] == pytest.approx(15.0)
    assert slow["time"] == pytest.approx(0.0)


def test_reference_clamps_over_cap_actions():
    session = {"studies": [study(numActions=5, maxActions=5)]}
    ref = {"maxActionsAllowed": 3, "studies": []}
    warnings = score.apply_reference(session, ref)
    assert session["studies"][0]["maxActions"] == 3
    assert session["studies"][0]["numActions"] == 3
    assert any("exceeds official cap" in w for w in warnings)


def test_reference_trusts_official_baseline():
    session = {"studies": [study(studyId="s1", baselineMaxRho=1.05)]}
    ref = {"maxActionsAllowed": 3,
           "studies": [{"studyId": "s1", "baselineMaxLoadingPct": 130.0}]}
    score.apply_reference(session, ref)
    assert session["studies"][0]["baselineMaxRho"] == pytest.approx(1.30)

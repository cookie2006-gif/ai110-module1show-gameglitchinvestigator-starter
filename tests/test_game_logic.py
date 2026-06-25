import sys
from pathlib import Path

# Make the repo root importable so `logic_utils` resolves regardless of
# how pytest is invoked (e.g. `pytest tests/...` vs `python -m pytest`).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from logic_utils import (
    DIFFICULTY_SETTINGS,
    get_range_for_difficulty,
    get_attempts_for_difficulty,
    parse_guess,
    validate_in_range,
    check_guess,
    fresh_game_state,
)


# ---------- Difficulty config ----------

@pytest.mark.parametrize(
    "difficulty, expected_low, expected_high, expected_attempts",
    [
        ("Easy",   1,  20, 6),
        ("Normal", 1, 100, 8),
        ("Hard",   1,  50, 5),
    ],
)
def test_difficulty_config(difficulty, expected_low, expected_high, expected_attempts):
    low, high = get_range_for_difficulty(difficulty)
    attempts = get_attempts_for_difficulty(difficulty)
    assert (low, high) == (expected_low, expected_high)
    assert attempts == expected_attempts
    assert DIFFICULTY_SETTINGS[difficulty] == {
        "low": expected_low,
        "high": expected_high,
        "attempts": expected_attempts,
    }


def test_unknown_difficulty_falls_back_to_normal():
    assert get_range_for_difficulty("Bogus") == (1, 100)
    assert get_attempts_for_difficulty("Bogus") == 8


# ---------- High/low hint logic ----------

def test_check_guess_win():
    outcome, message = check_guess(50, 50)
    assert outcome == "Win"
    assert "Correct" in message


def test_check_guess_too_high_returns_go_lower():
    outcome, message = check_guess(75, 50)
    assert outcome == "Too High"
    assert "LOWER" in message


def test_check_guess_too_low_returns_go_higher():
    outcome, message = check_guess(25, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message


def test_check_guess_does_not_compare_lexicographically():
    # Regression: the old bug compared strings, so "9" > "10" lexicographically.
    outcome, _ = check_guess(9, 10)
    assert outcome == "Too Low"


# ---------- Out-of-range rejection (does NOT consume an attempt) ----------

def test_validate_in_range_accepts_boundaries():
    ok_low, err_low = validate_in_range(1, 1, 20)
    ok_high, err_high = validate_in_range(20, 1, 20)
    assert ok_low and err_low is None
    assert ok_high and err_high is None


def test_validate_in_range_rejects_below():
    ok, err = validate_in_range(0, 1, 20)
    assert ok is False
    assert "between 1 and 20" in err


def test_validate_in_range_rejects_above():
    ok, err = validate_in_range(21, 1, 20)
    assert ok is False
    assert "between 1 and 20" in err


def test_out_of_range_guess_does_not_consume_attempt():
    # Mirrors the app.py submit flow: a guess that fails validate_in_range
    # must not increment the attempt counter.
    state = {"attempts": 0, "history": []}
    low, high = get_range_for_difficulty("Easy")  # 1..20

    ok, guess_int, _ = parse_guess("999")
    assert ok and guess_int == 999

    in_range, _ = validate_in_range(guess_int, low, high)
    if not in_range:
        state["history"].append(guess_int)  # app.py logs it...
        # ...but does NOT do: state["attempts"] += 1
    else:
        state["attempts"] += 1

    assert state["attempts"] == 0
    assert state["history"] == [999]


def test_unparseable_guess_does_not_consume_attempt():
    state = {"attempts": 0, "history": []}
    ok, guess_int, err = parse_guess("not a number")
    assert ok is False
    assert guess_int is None
    assert err  # non-empty error message
    # app.py logs the raw string but does not increment attempts
    if not ok:
        state["history"].append("not a number")
    assert state["attempts"] == 0


# ---------- New Game reset behavior ----------

def test_fresh_game_state_shape_and_values():
    state = fresh_game_state(1, 20)
    assert set(state.keys()) == {"secret", "attempts", "score", "status", "history"}
    assert state["attempts"] == 0
    assert state["score"] == 0
    assert state["status"] == "playing"
    assert state["history"] == []
    assert 1 <= state["secret"] <= 20


def test_fresh_game_state_respects_difficulty_range():
    low, high = get_range_for_difficulty("Hard")  # 1..50
    for _ in range(50):
        state = fresh_game_state(low, high)
        assert low <= state["secret"] <= high


def test_new_game_clears_prior_progress():
    # Simulate a game in progress, then reset it the way app.py does.
    session = {
        "secret": 7,
        "attempts": 4,
        "score": 35,
        "status": "lost",
        "history": [10, 15, 3, 8],
    }
    low, high = get_range_for_difficulty("Normal")
    for k, v in fresh_game_state(low, high).items():
        session[k] = v

    assert session["attempts"] == 0
    assert session["score"] == 0
    assert session["status"] == "playing"
    assert session["history"] == []
    assert low <= session["secret"] <= high

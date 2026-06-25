"""
Pure-logic helpers for Glitchy Guesser.

Single source of truth for difficulty settings and gameplay rules. app.py
imports from here; nothing in this module imports Streamlit, so everything
here is testable in isolation.
"""

import random


# FIX: Unified difficulty settings so UI and gameplay use the same values.
# Every difficulty-aware piece of the app (UI text, secret generation, input
# validation, attempt counter) reads from this dict.
DIFFICULTY_SETTINGS = {
    "Easy":   {"low": 1, "high":  20, "attempts": 6},
    "Normal": {"low": 1, "high": 100, "attempts": 8},
    "Hard":   {"low": 1, "high":  50, "attempts": 5},
}


def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    s = DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS["Normal"])
    return s["low"], s["high"]


def get_attempts_for_difficulty(difficulty: str):
    """Return the maximum number of attempts allowed for a given difficulty."""
    s = DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS["Normal"])
    return s["attempts"]


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None or raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except (ValueError, TypeError):
        return False, None, "That is not a number."

    return True, value, None


# FIX: Added range validation tied to selected difficulty.
def validate_in_range(guess: int, low: int, high: int):
    """
    Confirm guess is within [low, high] inclusive.

    Returns: (ok: bool, error_message: str | None)
    """
    if low <= guess <= high:
        return True, None
    return False, f"Out of range — pick a whole number between {low} and {high}."


def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome is one of: "Win", "Too High", "Too Low".
    """
    if guess == secret:
        return "Win", "🎉 Correct!"

    # FIX: Corrected reversed high/low hint logic after reviewing AI suggestion.
    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and which attempt this was (1-indexed)."""
    # FIX: Removed off-by-one (was attempt_number + 1) and the parity-dependent
    # bonus that added +5 for a wrong "Too High" guess on even attempts.
    if outcome == "Win":
        points = max(10, 100 - 10 * attempt_number)
        return current_score + points

    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score


# FIX: Reset full game state when starting a new round.
def fresh_game_state(low: int, high: int):
    """
    Return the dict of session-state values that define a fresh round.

    Pure function so the reset is testable outside Streamlit. app.py writes
    each entry into st.session_state.
    """
    return {
        "secret":   random.randint(low, high),
        "attempts": 0,
        "score":    0,
        "status":   "playing",
        "history":  [],
    }

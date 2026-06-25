# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip3 install -r requirements.txt`
2. Run the broken app: `python3 -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

**Game's purpose.** A Streamlit number-guessing game. The player picks a difficulty (Easy 1–20, Normal 1–100, Hard 1–50) and guesses the secret number with higher/lower hints.

**Bugs found.**
- The secret number changed on every submit.
- The higher/lower hints were reversed.
- On some turns the hint was wrong because numbers were compared as text (so 9 looked bigger than 10).
- The difficulty range and number of attempts didn't match what the sidebar showed.
- Out-of-range or non-numeric guesses still used up an attempt.
- New Game didn't fully reset the game, so the player was stuck on the win/lose screen.
- Developer debug info was visible to the player.
- The score formula was off and gave random bonus points.

**Fixes applied.**
- Moved the game logic into `logic_utils.py` and used one `DIFFICULTY_SETTINGS` dict for ranges and attempts.
- Stored the secret in `st.session_state` and used `fresh_game_state()` for both the first load and New Game.
- Fixed `check_guess` so it compares numbers and returns the correct hint.
- Added input validation: invalid guesses show an error but don't use up an attempt.
- Hid the debug panel behind a `GLITCHY_DEBUG=1` environment variable.
- Cleaned up the score calculation.
- Added pytest tests in `tests/test_game_logic.py`.

## 🕹️ Demo Walkthrough

A step-by-step playthrough of the fixed game so a reader can follow along without a video. Assume the player selects **Normal** difficulty (range 1–100, 8 attempts) and the hidden secret happens to be **47**.

1. The app opens showing Range: 1 to 100 and Attempts allowed: 8. The main banner says “Guess a number between 1 and 100. Attempts left: 8.” The Developer Debug Info is hidden from players.

2. First guess 50 → hint says “Go LOWER!” and attempts drop to 7.

3. Second guess 25 → hint says “Go HIGHER!” and attempts drop to 6.

4. Out-of-range guess 150 → red error “Out of range — pick a whole number between 1 and 100.” Attempts stay at 6.

5. Next guesses 40 (Go HIGHER!, 5 attempts) and 48 (Go LOWER!, 4 attempts).

6. Winning guess 47 → balloons and a green message: “You won! The secret was 47. Final score: 70.”

7. Any further submit shows “You already won. Start a new game to play again.”

8. Clicking New Game regenerates the secret, resets attempts to 8, score to 0, clears history, and returns to playing.

9. Switching to Hard sets Range: 1 to 50, Attempts allowed: 5, and the next New Game uses a secret in 1–50.

10. Running with GLITCHY_DEBUG=1 streamlit run app.py shows the Developer Debug Info for grading; it stays hidden by default.

## 🧪 Test Results

```
# Paste your pytest output here, e.g.:
# pytest tests/
# ========================= X passed in 0.XXs =========================
```

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]

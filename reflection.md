# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
    When I first run this game, I saw a number-guessing app with a Normal difficulty setting, a range of guessing number 1 to 100, number of attemps left, an input box of guess, buttons to submit game and start a new game, a visable hint option.
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").
    + The game attemps is not consistent with the setting
    + The app displayed " Developer Debug Info", which suggests debug-only information was leaking into the user-facing interface.
**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input Used | Expected Behavior | Actual Behavior | Console Error / Output |
|---|---|---|---|
| Finish one round, then click **New Game** | A fresh round should begin with a new secret number, reset attempts, and normal gameplay state. | After finishing a round, the game may not properly start a new game, so the player cannot continue normally. | none |
| Enter a number smaller than the secret number | The game should tell the player to guess higher. | The game incorrectly tells the player to “go lower.” | none |
| Enter a number larger than the secret number | The game should tell the player to guess lower. | The game incorrectly tells the player to “go higher.” | none |
| Enter an out-of-range value such as `-3` or `101` | The game should reject invalid input and ask for a number inside the allowed range. | The game accepts numbers outside the stated range. | none |
| Select **Easy** mode | The game should use the Easy settings exactly: range 1 to 20 and 6 attempts. | In practice, the range becomes 1 to 100 and attempts drop to 5. | none |
| Select **Normal** mode | The game should use 8 attempts for Normal mode. | In practice, the game gives only 7 attempts. | none |
| Select **Hard** mode | The game should use range 1 to 50 and 5 attempts. | In practice, the game still uses range 1 to 100 and fewer attempts than expected. | none |
| Open and play the game as a normal user | Internal debugging details should be hidden from the player. | The page visibly shows **Developer Debug Info**, which can reveal the answer or internal state. | none |
---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
    Claude
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
    Claude found that check_guess had the right outcome labels ("Too High" / "Too Low") but swapped message strings - it was telling players to "Go HIGHER" when they were already too high. I verified by playing the game: before the fix, guessing 80 with secret 50 said "Go HIGHER"; after the fix it correctly said "Go LOWER", and test_guess_too_high_outcome_and_message passed.
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).
    When I asked Claude to fix the difficulty bug, it rewrote the config values (Easy 8 attempts, Normal 6, etc.) under the assumption that "harder should mean larger range and fewer attempts." But the actual bug was that the UI and gameplay weren't reading from the existing config consistently — the original values (Easy 6, Normal 8, Hard 5) were intentional. I verified by re-reading my own task description, which never said the values themselves were wrong, and pushed back to restore the originals.
---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
    two-step check - first I ran pytest tests/test_game_logic.py to confirm logic-level correctness, then I manually played the Streamlit app and reproduced the original broken scenario to confirm the player-facing behavior was correct.
- Describe at least one test you ran (manual or using pytest) and what it showed you about your code.
    test_out_of_range_guess_is_rejected[Easy-21]. It confirmed that on Easy (range 1–20), entering 21 correctly returns ok=False with an error message containing both bounds. This showed me my validate_in_range helper actually rejects boundary-adjacent values, not just obviously wrong ones like -999.
- Did AI help you design or understand any tests? How?
    yes. Claude suggested parametrizing the range tests so one function covers all difficulties × boundary cases, and reminded me to also test the positive cases (in-range values that should be accepted) — I would have only tested the rejection side.
---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
    A Streamlit app re-runs the entire Python file top-to-bottom every time the user interacts with anything - clicks a button, types in a box, moves a slider. So any regular variable you set gets thrown away and recomputed on every rerun. st.session_state is a special dictionary that survives those reruns, which is where you put things you need to remember between interactions — like the secret number, score, or whether the game is won. The bug we hit was a perfect example: clicking "New Game" reset attempts and secret, but forgot to reset status in session_state, so the very next rerun saw status == "won" and froze the player on the win screen.
---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
  
  asking the AI to add # FIXME comments and explain the root cause before writing any fix. It forced me to understand each bug instead of just accepting a patch, and it kept the AI from "fixing" the wrong thing.
- What is one thing you would do differently next time you work with AI on a coding task?
    verify the AI's assumptions out loud before letting it change code — especially when it rewrites values or config. Claude's difficulty-values incident would have been avoided if I'd asked "what makes you think those values were wrong?" first.
- In one or two sentences, describe how this project changed the way you think about AI generated code.
    AI-generated code is confident and often wrong in subtle ways — off-by-ones, reversed messages, silent assumptions about what a "good" design looks like. I now treat anything the AI writes as a draft for review, not a finished answer.

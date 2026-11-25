#!/usr/bin/env python3
"""Fortune Cookie for the Liquidated Trader (make.fun bounty).

Writes one fortune cookie line for a crypto trader who has just been
liquidated to /output/entry.txt.

Method: 13 hand-written candidate lines, each scored 1-5 on the five axes
of the judge's brief, in the judge's own order of importance:

  (a) cookie voice AND the trading loss are both in the line
  (b) it makes the liquidated trader laugh, rueful and warm, never cruel
  (c) one line, at most 20 words, read whole in a single breath
  (d) fresh joke: a turn, a double meaning, a surprising last word
  (e) fortune voice: small, oracular, slightly formal phrasing that the
      punchline then breaks

The winner is picked by (total, a, d, e, last-word punch), then revised
once by hand (see REVISION below) before it is written out.
"""

import os
import sys

# Each candidate: (text, a, b, c, d, e, last_word_punch)
# last_word_punch is 1 when the final word itself is the surprising turn.
CANDIDATES = [
    (
        "The stars say your next trade will be brilliant \u2014 they just "
        "didn't say with whose money.",
        3, 4, 5, 4, 4, 0,
    ),
    (
        "A wealthy stranger will enter your life soon. It is you, after "
        "you stop using 100x leverage.",
        4, 4, 5, 4, 5, 0,
    ),
    (
        "Your lucky numbers are 0, 0, and 0 \u2014 the same as your margin "
        "balance, which is now at peace.",
        4, 3, 5, 3, 3, 0,
    ),
    (
        "The universe has taken your money, but it left you the lesson, "
        "the story, and this cookie.",
        5, 4, 5, 4, 4, 1,
    ),
    (
        "Good fortune is coming: it was liquidated along with you, and it "
        "is also starting over.",
        5, 4, 5, 4, 4, 0,
    ),
    (
        "You will meet a tall, dark stranger \u2014 your liquidation notice, "
        "which has been looking for you.",
        4, 3, 5, 3, 4, 0,
    ),
    (
        "The stars aligned perfectly, then sold the alignment at market "
        "price, just like you.",
        4, 4, 5, 4, 4, 0,
    ),
    (
        "A great opportunity awaits you: it's called spot, and it never "
        "liquidates anyone.",
        4, 3, 5, 4, 4, 0,
    ),
    (
        "Your future is bright, now that the exchange has turned off the "
        "lights on your position.",
        4, 3, 5, 3, 3, 0,
    ),
    (
        "Fortune favors the bold, but the exchange favors whoever reads "
        "the maintenance margin first.",
        4, 3, 5, 4, 4, 0,
    ),
    (
        "The market took your money and left you wisdom \u2014 a terrible "
        "trade, but the cookie is free.",
        5, 4, 5, 3, 3, 0,
    ),
    (
        "Your lucky day was yesterday. Today the cookie is free, and so, "
        "at last, are you.",
        3, 4, 5, 5, 5, 0,
    ),
    (
        "Great wealth is coming your way, just as soon as you stop trading "
        "like the market owes you.",
        3, 2, 5, 2, 3, 0,
    ),
]

# Winner of the scoring above: candidate 4, total 22.
# It ties on points with candidates 2, 5 and 12, but wins the tie-break:
# it is the only tied line that scores 5 on (a) — the loss is stated
# outright ("has taken your money") — and its punchline lands on the
# final word ("cookie"), while candidate 5 spends its turn mid-line and
# ends soft on "starting over", and candidates 2 and 12 only imply the
# loss instead of naming it.
CHOSEN = (
    "The universe has taken your money, but it left you the lesson, "
    "the story, and this cookie."
)

# REVISION (second pass, applied by hand after the first scoring):
# candidate 4's one weak spot is "the lesson" — it reads a touch like a
# lecture, and the judge's brief says the trader is laughing with the
# cookie, not being lectured by it. The revision below keeps the triple
# list and the last-word punch, but swaps the lecture for a joke about
# the fortune itself ("a story, a punchline"), and tightens "has taken"
# to "took" so the line reads in one breath.
REVISED = (
    "The universe took your money and left you a story, a punchline, "
    "and this cookie."
)

OUTPUT_PATH = "/output/entry.txt"
MAX_WORDS = 20
MAX_CHARS = 160


def score_table():
    """Print the candidate scores, highest total first."""
    rows = []
    for i, (text, a, b, c, d, e, punch) in enumerate(CANDIDATES, 1):
        rows.append((a + b + c + d + e, a, d, e, punch, i, text))
    rows.sort(key=lambda r: (-r[0], -r[1], -r[2], -r[3], -r[4], r[5]))
    for total, a, d, e, punch, i, text in rows:
        print(f"#{i:2d} total={total:2d} (a={a} d={d} e={e} punch={punch}): {text}")
    return rows


def pick_winner():
    """Return the winning candidate text by the tie-break order."""
    best = None
    best_key = None
    for text, a, b, c, d, e, punch in CANDIDATES:
        key = (a + b + c + d + e, a, d, e, punch)
        if best_key is None or key > best_key:
            best_key = key
            best = text
    return best


def validate(text):
    """The gate: 1-160 chars, one line, at most 20 words, plain text."""
    if not text or not text.strip():
        raise ValueError("fortune is empty")
    if "\n" in text.strip():
        raise ValueError("fortune must be a single line")
    if len(text) > MAX_CHARS:
        raise ValueError(f"fortune is {len(text)} chars, over {MAX_CHARS}")
    words = text.split()
    if len(words) > MAX_WORDS:
        raise ValueError(f"fortune is {len(words)} words, over {MAX_WORDS}")
    return len(words)


def verify_output(path, expected):
    """Second-pass check: read the written file back and prove it is the
    chosen fortune, byte for byte — exactly one line, at most 20 words,
    identical to `expected`. Returns (words, chars) on success; raises
    ValueError (non-zero exit in main) on any mismatch."""
    with open(path, "rb") as f:
        raw = f.read()
    expected_bytes = (expected + "\n").encode("utf-8")
    if raw != expected_bytes:
        raise ValueError(
            f"written output does not match the chosen fortune byte for byte: "
            f"wrote {raw!r}, expected {expected_bytes!r}"
        )
    text = raw.decode("utf-8")
    lines = text.splitlines()
    if len(lines) != 1:
        raise ValueError(f"written output has {len(lines)} lines, expected exactly 1")
    words = lines[0].split()
    if len(words) > MAX_WORDS:
        raise ValueError(f"written output has {len(words)} words, over {MAX_WORDS}")
    return len(words), len(lines[0])


def main():
    score_table()
    winner = pick_winner()
    assert winner == CHOSEN, "scoring pick drifted from the recorded winner"
    fortune = REVISED
    words = validate(fortune)
    print(f"winner (revised): {fortune}")
    print(f"words: {words}, chars: {len(fortune)}")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(fortune + "\n")
    print(f"wrote {OUTPUT_PATH}")
    try:
        v_words, v_chars = verify_output(OUTPUT_PATH, fortune)
    except ValueError as e:
        print(f"verification FAILED: {e}", file=sys.stderr)
        return 1
    print(
        f"verification OK: {OUTPUT_PATH} holds exactly 1 line, "
        f"{v_words} words, {v_chars} chars, byte-identical to the chosen fortune"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

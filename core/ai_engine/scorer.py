import math
from .ngram import NgramEngine


class PasswordScorer:
    """
    Scores and ranks password candidates.
    Uses N-gram frequency + heuristics to predict
    which passwords are most likely to be correct.
    """

    def __init__(self, ngram_engine: NgramEngine):
        self.ngram = ngram_engine

    def score(self, word: str) -> float:
        """
        Score a password. Higher = more likely.
        Combines: N-gram frequency + length penalty
        + complexity bonus + human pattern bonus.
        """
        if not word:
            return 0.0

        score = 0.0

        # N-gram frequency score
        ngram_score = self.ngram.score_word(word)
        score += ngram_score * 10

        # Length sweet spot (6-10 chars most common)
        length = len(word)
        if 6 <= length <= 10:
            score += 20
        elif 4 <= length <= 12:
            score += 10
        elif length > 16:
            score -= 10

        # Has digit — very common in passwords
        if any(c.isdigit() for c in word):
            score += 15

        # Has uppercase — common pattern
        if any(c.isupper() for c in word):
            score += 8

        # Ends with digit or ! — extremely common
        if word[-1].isdigit() or word[-1] in "!@#$":
            score += 12

        # Starts with uppercase — common pattern
        if word[0].isupper():
            score += 8

        # Contains year pattern
        for yr in ["19", "20"]:
            if yr in word:
                score += 6
                break

        # Penalize very random looking strings
        charset = len(set(word))
        if charset > length * 0.9:
            score -= 5

        return max(0.0, score)

    def rank(self, words: list[str]) -> list[tuple]:
        """
        Returns list of (word, score) sorted by
        score descending — highest probability first.
        """
        scored = [(w, self.score(w)) for w in words]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    def top_n(self, words: list[str],
              n: int = 100) -> list[str]:
        """Return top N most likely passwords."""
        return [w for w, _ in self.rank(words)[:n]]
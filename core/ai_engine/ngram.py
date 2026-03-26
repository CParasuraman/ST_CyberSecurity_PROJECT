from collections import Counter


class NgramEngine:
    """
    Analyses password datasets to find the most
    common N-gram sequences. Used to score and
    rank password candidates.
    """

    def __init__(self, n_values=(2, 3, 4)):
        self.n_values = n_values
        self.ngrams   = {n: Counter() for n in n_values}
        self.trained  = False

    def train(self, passwords: list[str]):
        for pwd in passwords:
            for n in self.n_values:
                for i in range(len(pwd) - n + 1):
                    gram = pwd[i:i + n]
                    self.ngrams[n][gram] += 1
        self.trained = bool(passwords)

    def score_word(self, word: str) -> float:
        """
        Score a word based on how common its
        N-grams are in the training data.
        Higher = more likely to be a real password.
        """
        if not self.trained or not word:
            return 0.0

        total_score = 0.0
        count       = 0

        for n in self.n_values:
            if len(word) < n:
                continue
            for i in range(len(word) - n + 1):
                gram = word[i:i + n]
                freq = self.ngrams[n].get(gram, 0)
                total_score += freq
                count += 1

        return total_score / count if count > 0 else 0.0

    def top_ngrams(self, n: int,
                   limit: int = 20) -> list[tuple]:
        """Return most common N-grams."""
        if n not in self.ngrams:
            return []
        return self.ngrams[n].most_common(limit)

    def generate_from_ngrams(self,
                             seed: str = "",
                             length: int = 8,
                             count: int = 50
                             ) -> list[str]:
        """
        Build words by chaining the most probable
        N-grams — pure statistical generation.
        """
        if not self.trained:
            return []

        n       = min(self.n_values)
        results = []
        top     = self.top_ngrams(n, 200)

        if not top:
            return []

        import random
        grams  = [g for g, _ in top]
        counts = [c for _, c in top]
        total  = sum(counts)

        for _ in range(count * 3):
            word = seed or ""
            if not word:
                r   = random.randint(1, total)
                cum = 0
                for g, c in zip(grams, counts):
                    cum += c
                    if r <= cum:
                        word = g
                        break

            while len(word) < length:
                tail = word[-n:] if len(word) >= n \
                       else word
                # find grams starting with tail
                matches = [(g, c) for g, c in top
                           if g.startswith(tail[-1])]
                if not matches:
                    break
                mt = sum(c for _, c in matches)
                r  = random.randint(1, mt)
                cum = 0
                chosen = matches[0][0]
                for g, c in matches:
                    cum += c
                    if r <= cum:
                        chosen = g
                        break
                word += chosen[-1]

            if 4 <= len(word) <= 16:
                results.append(word)

        return list(set(results))[:count]
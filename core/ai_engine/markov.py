import json
import os
import random
from collections import defaultdict


class MarkovPasswordModel:
    """
    Markov Chain that learns password patterns.
    Trains on real password lists and generates
    statistically likely new passwords.
    """

    def __init__(self, order=2):
        self.order      = order
        self.chain      = defaultdict(lambda: defaultdict(int))
        self.start_seqs = defaultdict(int)
        self.trained    = False
        self.total_trained = 0

    def train(self, passwords: list[str]):
        """Train the model on a list of passwords."""
        for pwd in passwords:
            if len(pwd) < self.order + 1:
                continue
            # Record starting sequences
            start = pwd[:self.order]
            self.start_seqs[start] += 1
            # Build transition table
            for i in range(len(pwd) - self.order):
                state = pwd[i:i + self.order]
                next_char = pwd[i + self.order]
                self.chain[state][next_char] += 1
            self.total_trained += 1

        self.trained = self.total_trained > 0

    def _pick_next(self, state: str) -> str | None:
        """Pick next character based on transition probabilities."""
        if state not in self.chain:
            return None
        transitions = self.chain[state]
        total = sum(transitions.values())
        r = random.randint(1, total)
        cumulative = 0
        for char, count in transitions.items():
            cumulative += count
            if r <= cumulative:
                return char
        return None

    def generate(self, min_len=4, max_len=16,
                 count=100) -> list[str]:
        """Generate new password candidates."""
        if not self.trained:
            return []

        results = []
        attempts = 0
        max_attempts = count * 20

        # Build weighted start list
        starts = list(self.start_seqs.keys())
        weights = list(self.start_seqs.values())

        while len(results) < count \
                and attempts < max_attempts:
            attempts += 1

            # Pick a starting sequence
            if not starts:
                break
            total_w = sum(weights)
            r = random.randint(1, total_w)
            cum = 0
            current = starts[0]
            for s, w in zip(starts, weights):
                cum += w
                if r <= cum:
                    current = s
                    break

            pwd = current
            # Generate rest character by character
            for _ in range(max_len - self.order):
                state = pwd[-self.order:]
                next_c = self._pick_next(state)
                if next_c is None:
                    break
                pwd += next_c

            if min_len <= len(pwd) <= max_len:
                results.append(pwd)

        return list(set(results))

    def save(self, path: str):
        data = {
            "order":         self.order,
            "chain":         {k: dict(v)
                              for k, v in self.chain.items()},
            "start_seqs":    dict(self.start_seqs),
            "total_trained": self.total_trained,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load(self, path: str):
        if not os.path.exists(path):
            return False
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.order         = data["order"]
        self.total_trained = data.get("total_trained", 0)
        self.start_seqs    = defaultdict(
            int, data["start_seqs"])
        self.chain         = defaultdict(
            lambda: defaultdict(int))
        for state, trans in data["chain"].items():
            for char, cnt in trans.items():
                self.chain[state][char] = cnt
        self.trained = self.total_trained > 0
        return True
import os
import json
from .markov import MarkovPasswordModel
from .ngram import NgramEngine


MODEL_DIR = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "data", "ai_models")

MARKOV_PATH = os.path.join(MODEL_DIR, "markov.json")
NGRAM_PATH  = os.path.join(MODEL_DIR, "ngram.json")
STATS_PATH  = os.path.join(MODEL_DIR, "stats.json")


class AITrainer:
    """
    Trains and manages the AI models.
    Handles loading wordlists, training,
    saving/loading models, and self-learning
    from cracked results.
    """

    def __init__(self):
        os.makedirs(MODEL_DIR, exist_ok=True)
        self.markov = MarkovPasswordModel(order=2)
        self.ngram  = NgramEngine(n_values=(2, 3, 4))
        self.stats  = self._load_stats()

    def _load_stats(self) -> dict:
        if os.path.exists(STATS_PATH):
            with open(STATS_PATH, "r") as f:
                return json.load(f)
        return {
            "total_trained": 0,
            "training_files": [],
            "self_learned":  0,
        }

    def _save_stats(self):
        with open(STATS_PATH, "w") as f:
            json.dump(self.stats, f, indent=2)

    def is_trained(self) -> bool:
        return (os.path.exists(MARKOV_PATH)
                and os.path.exists(NGRAM_PATH))

    def load_models(self) -> bool:
        """Load pre-trained models from disk."""
        ok1 = self.markov.load(MARKOV_PATH)
        ok2 = self._load_ngram()
        return ok1 and ok2

    def _load_ngram(self) -> bool:
        if not os.path.exists(NGRAM_PATH):
            return False
        with open(NGRAM_PATH, "r") as f:
            data = json.load(f)
        from collections import Counter
        for n_str, counts in data.items():
            n = int(n_str)
            if n in self.ngram.ngrams:
                self.ngram.ngrams[n] = Counter(counts)
        self.ngram.trained = True
        return True

    def _save_ngram(self):
        data = {
            str(n): dict(counter)
            for n, counter in self.ngram.ngrams.items()
        }
        with open(NGRAM_PATH, "w") as f:
            json.dump(data, f)

    def train_from_file(self, filepath: str,
                        callback=None) -> int:
        """
        Train models from a wordlist file.
        callback(progress_pct, count) for UI updates.
        Returns number of passwords trained on.
        """
        passwords = []
        try:
            with open(filepath, "r",
                      encoding="latin-1") as f:
                for line in f:
                    pwd = line.strip()
                    if 3 <= len(pwd) <= 20:
                        passwords.append(pwd)
        except Exception as e:
            return 0

        total = len(passwords)
        if total == 0:
            return 0

        # Train in chunks for UI responsiveness
        chunk_size = max(1000, total // 20)
        for i in range(0, total, chunk_size):
            chunk = passwords[i:i + chunk_size]
            self.markov.train(chunk)
            self.ngram.train(chunk)
            if callback:
                pct = int(((i + chunk_size) / total)
                          * 100)
                callback(min(pct, 100),
                         min(i + chunk_size, total))

        # Save models
        self.markov.save(MARKOV_PATH)
        self._save_ngram()

        # Update stats
        self.stats["total_trained"] += total
        self.stats["training_files"].append(
            os.path.basename(filepath))
        self._save_stats()

        return total

    def self_learn(self, cracked_results: list[dict]):
        """
        Self-learning — train on successfully
        cracked passwords to improve future guesses.
        This is what makes the AI get smarter over time.
        """
        new_passwords = [
            r["plain"] for r in cracked_results
            if r.get("status") == "Cracked"
            and r.get("plain") not in ("—", "", None)
        ]
        if not new_passwords:
            return 0

        # Weight cracked passwords 3x — they're gold
        weighted = new_passwords * 3
        self.markov.train(weighted)
        self.ngram.train(weighted)

        self.markov.save(MARKOV_PATH)
        self._save_ngram()

        self.stats["self_learned"] += len(new_passwords)
        self._save_stats()

        return len(new_passwords)

    def get_stats(self) -> dict:
        return {
            **self.stats,
            "markov_states": len(self.markov.chain),
            "ngram_2_count": len(
                self.ngram.ngrams.get(2, {})),
            "ngram_3_count": len(
                self.ngram.ngrams.get(3, {})),
        }
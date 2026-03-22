import hashlib
import time
import tkinter as tk
from core.rainbow import RainbowPasswordCracker

rainbow = RainbowPasswordCracker()

ALGORITHMS = {
    "md5":    lambda w: hashlib.md5(w.encode()).hexdigest(),
    "sha1":   lambda w: hashlib.sha1(w.encode()).hexdigest(),
    "sha256": lambda w: hashlib.sha256(w.encode()).hexdigest(),
    "sha512": lambda w: hashlib.sha512(w.encode()).hexdigest(),
}

def crack_passwords(hash_file, wordlist_file, output_text):
    start = time.time()

    with open(hash_file, "r", encoding="latin-1") as f:
        hashes = [h.strip() for h in f.read().splitlines() if h.strip()]

    with open(wordlist_file, "r", encoding="latin-1") as f:
        wordlist = [w.strip() for w in f.read().splitlines() if w.strip()]

    def log(msg):
        output_text.insert(tk.END, msg + "\n")
        output_text.see(tk.END)
        output_text.update_idletasks()

    log(f"Starting — {len(hashes)} hash(es), {len(wordlist)} words in wordlist\n")

    cracked, not_found = 0, 0

    for hash_val in hashes:
        found = False

        # 1. Rainbow table lookup first (fast)
        result = rainbow.lookup(hash_val)
        if result is not None:
            log(f"[RAINBOW]  {hash_val}  →  {result!r}")
            cracked += 1
            continue

        # 2. Dictionary / wordlist attack
        for word in wordlist:
            for algo_name, algo_fn in ALGORITHMS.items():
                if algo_fn(word) == hash_val.lower():
                    log(f"[{algo_name.upper():<7}]  {hash_val}  →  {word!r}")
                    cracked += 1
                    found = True
                    break
            if found:
                break

        if not found:
            log(f"[NOT FOUND]  {hash_val}")
            not_found += 1

    elapsed = round(time.time() - start, 2)
    log(f"\n{'='*60}")
    log(f"Done in {elapsed}s  |  Cracked: {cracked}  |  Not found: {not_found}")
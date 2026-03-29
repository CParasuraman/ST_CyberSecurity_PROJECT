"""
Hashcat-compatible rule engine.
Supports the most common rule operations.
"""


def apply_rule(word: str, rule: str) -> str | None:
    """
    Apply a single Hashcat-style rule to a word.
    Returns transformed word or None if rule fails.
    """
    rule = rule.strip()
    if not rule or rule.startswith("#"):
        return word

    tokens = rule.split()
    result = word

    for token in tokens:
        if not token:
            continue
        out = _apply_token(result, token)
        if out is None:
            return None
        result = out

    return result if result != word else result


def _apply_token(word: str, token: str) -> str | None:
    try:
        # ── Single char rules ────────────────────────
        if token == ":":   return word
        if token == "l":   return word.lower()
        if token == "u":   return word.upper()
        if token == "c":   return word.capitalize()
        if token == "C":
            return word[0].lower() + word[1:].upper() \
                   if word else word
        if token == "r":   return word[::-1]
        if token == "d":   return word + word
        if token == "f":
            return word + word[::-1]
        if token == "t":
            return word.swapcase()
        if token == "q":
            return "".join(c * 2 for c in word)
        if token == "k":
            return (word[1] + word[0] + word[2:]
                    if len(word) >= 2 else word)
        if token == "K":
            return (word[:-3] + word[-2] + word[-1]
                    + word[-3]
                    if len(word) >= 3 else word)

        # ── Append / Prepend ─────────────────────────
        if token.startswith("$") and len(token) == 2:
            return word + token[1]

        if token.startswith("^") and len(token) == 2:
            return token[1] + word

        # ── Truncate ──────────────────────────────────
        if token.startswith("["):
            n = int(token[1:]) if len(token) > 1 \
                else 1
            return word[n:]

        if token.startswith("]"):
            n = int(token[1:]) if len(token) > 1 \
                else 1
            return word[:-n] if n <= len(word) else ""

        # ── Delete at position ────────────────────────
        if token.startswith("D") and len(token) == 2:
            pos = _charpos(token[1], len(word))
            if pos is None or pos >= len(word):
                return None
            return word[:pos] + word[pos+1:]

        # ── Insert at position ────────────────────────
        if token.startswith("i") and len(token) == 3:
            pos  = _charpos(token[1], len(word))
            char = token[2]
            if pos is None:
                return None
            return word[:pos] + char + word[pos:]

        # ── Overwrite at position ─────────────────────
        if token.startswith("o") and len(token) == 3:
            pos  = _charpos(token[1], len(word))
            char = token[2]
            if pos is None or pos >= len(word):
                return None
            return word[:pos] + char + word[pos+1:]

        # ── Extract substring ─────────────────────────
        if token.startswith("x") and len(token) == 3:
            pos = _charpos(token[1], len(word))
            n   = _charpos(token[2], len(word))
            if pos is None or n is None:
                return None
            return word[pos:pos+n]

        # ── Title case ────────────────────────────────
        if token == "E":
            return " ".join(
                w.capitalize()
                for w in word.split())

        # ── Duplicate N times ─────────────────────────
        if token.startswith("p") and len(token) == 2:
            n = _charpos(token[1], 10)
            if n is None:
                return None
            return word * (n + 1)

        # ── Replace char ──────────────────────────────
        if token.startswith("s") and len(token) == 3:
            old = token[1]
            new = token[2]
            return word.replace(old, new)

        # ── Leet speak shortcuts ──────────────────────
        if token == "@e":
            return word.replace("e", "3")
        if token == "@a":
            return word.replace("a", "@")
        if token == "@i":
            return word.replace("i", "1")
        if token == "@o":
            return word.replace("o", "0")
        if token == "@s":
            return word.replace("s", "$")
        if token == "@t":
            return word.replace("t", "7")

        # ── Min/Max length filters ────────────────────
        if token.startswith(">") and len(token) >= 2:
            n = int(token[1:])
            return word if len(word) > n else None

        if token.startswith("<") and len(token) >= 2:
            n = int(token[1:])
            return word if len(word) < n else None

        if token.startswith("_") and len(token) >= 2:
            n = int(token[1:])
            return word if len(word) == n else None

        # Unknown token — skip
        return word

    except Exception:
        return None


def _charpos(char: str, length: int) -> int | None:
    """Convert Hashcat position char to int index."""
    if char.isdigit():
        return int(char)
    # Hashcat uses A=10, B=11 ... Z=35
    if char.isalpha() and char.isupper():
        return ord(char) - ord("A") + 10
    return None


def apply_rules_to_word(word: str,
                        rules: list[str]) -> list[str]:
    """Apply all rules to one word, return variants."""
    results = []
    seen    = set()
    for rule in rules:
        out = apply_rule(word, rule)
        if out is not None and out not in seen:
            seen.add(out)
            results.append(out)
    return results


def apply_rules_to_wordlist(
        wordlist: list[str],
        rules: list[str],
        callback=None) -> list[str]:
    """
    Apply all rules to entire wordlist.
    callback(pct, count) for progress updates.
    """
    results = []
    seen    = set()
    total   = len(wordlist)

    for i, word in enumerate(wordlist):
        word = word.strip()
        if not word:
            continue
        for rule in rules:
            out = apply_rule(word, rule)
            if out and out not in seen:
                seen.add(out)
                results.append(out)
        if callback and i % 100 == 0:
            pct = int(((i + 1) / total) * 100) \
                  if total else 0
            callback(pct, len(results))

    return results


def parse_rule_file(content: str) -> list[str]:
    """Parse a .rule file — skip comments/blanks."""
    rules = []
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            rules.append(line)
    return rules


# ── Built-in named rulesets ───────────────────────────
BUILT_IN_RULESETS = {
    "Basic leet": [
        "sa@ se3 si1 so0 ss$ st7",
        "c sa@ se3 si1 so0 ss$ st7",
        "u sa@ se3",
    ],
    "Common suffixes": [
        "$1", "$2", "$3", "$!",
        "$1$2$3", "$@", "$#",
        "c $1", "c $!", "c $1$2$3",
    ],
    "Case variants": [
        "l", "u", "c", "t",
        "C", "E",
    ],
    "Append years": [
        "$2$0$2$4", "$2$0$2$3",
        "$2$0$2$2", "$1$9$9$0",
        "$1$9$9$9", "$2$0$0$0",
        "c $2$0$2$4", "c $1$9$9$0",
    ],
    "Hashcat best64": [
        ":", "l", "u", "c", "r", "d",
        "$1", "$2", "$3", "$!", "$@",
        "^1", "^2", "^!",
        "c $1", "c $2", "c $!",
        "l $1", "u $1",
        "r $1", "d $1",
        "sa@", "se3", "si1", "so0",
        "c sa@", "c se3",
        "$1 $2 $3", "r d",
        "u $!", "c $1 $2 $3",
    ],
    "Names + numbers": [
        "c $1", "c $2", "c $3",
        "c $1$2", "c $1$2$3",
        "c $1$2$3$4",
        "c $!", "c $@", "c $#",
        "l $1", "l $2", "l $3",
    ],
}
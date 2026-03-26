import re


# Psychological password patterns humans use
PATTERNS = {
    "name_year":    "{name}{year}",
    "name_sym":     "{name}{sym}",
    "name_num":     "{name}{num}",
    "cap_name_num": "{Name}{num}",
    "cap_name_sym": "{Name}{sym}",
    "leet_name":    "{leet}",
    "name_name":    "{name}{name2}",
    "num_name":     "{num}{name}",
    "name_job":     "{name}{company}",
    "rev_name":     "{rev}",
}

COMMON_NUMS = [
    "1","2","12","123","1234","12345",
    "0","007","69","99","00","111","000","9"
]
COMMON_SYMS = ["!","@","#","$","!@#","?","*","!!"]
YEARS = [
    "2024","2023","2022","2021","2020",
    "2019","2018","2000","1999","1995",
    "1990","99","00","01","90","95"
]


def _leet(word: str) -> str:
    return (word.lower()
            .replace("a", "@")
            .replace("e", "3")
            .replace("i", "1")
            .replace("o", "0")
            .replace("s", "$")
            .replace("t", "7")
            .replace("l", "1")
            .replace("g", "9"))


class ContextAnalyser:
    """
    Analyses target personal information and
    generates psychologically likely passwords
    based on how humans actually create them.
    """

    def __init__(self):
        self.tokens = {}

    def load_target(self, info: dict):
        """
        info keys: name, username, birthday,
                   company, keywords, phone, custom
        """
        self.tokens = {}
        self.info   = info

        name = info.get("name", "").strip()
        if name:
            parts = name.lower().split()
            self.tokens["name"]  = parts[0] if parts else ""
            self.tokens["name2"] = parts[-1] if len(parts) > 1 else ""
            self.tokens["Name"]  = self.tokens["name"].capitalize()
            self.tokens["NAME"]  = self.tokens["name"].upper()
            self.tokens["leet"]  = _leet(self.tokens["name"])
            self.tokens["rev"]   = self.tokens["name"][::-1]

        username = info.get("username", "").strip()
        if username:
            self.tokens["username"] = username.lower()
            self.tokens["leet"] = self.tokens.get(
                "leet", _leet(username))

        company = info.get("company", "").strip()
        if company:
            c = company.lower().replace(" ", "")
            self.tokens["company"] = c
            self.tokens["Company"] = c.capitalize()

        bday = info.get("birthday", "").strip()
        self.bday_tokens = self._parse_birthday(bday)

        phone = info.get("phone", "").strip()
        self.phone_tokens = []
        if phone:
            digits = re.sub(r"\D", "", phone)
            self.phone_tokens = [
                digits, digits[-4:], digits[-6:],
                digits[:4]
            ] if digits else []

        self.keyword_tokens = []
        for field in ["keywords", "custom"]:
            val = info.get(field, "").strip()
            if val:
                for kw in val.split(","):
                    kw = kw.strip().lower()
                    if kw:
                        self.keyword_tokens.append(kw)
                        self.keyword_tokens.append(
                            kw.capitalize())
                        self.keyword_tokens.append(
                            _leet(kw))

    def _parse_birthday(self, bday: str) -> list[str]:
        tokens = []
        if not bday:
            return tokens
        digits = re.sub(r"\D", "", bday)
        if len(digits) >= 4:
            tokens += [
                digits,
                digits[-4:],     # year
                digits[:4],      # first 4
                digits[:2],      # day or month
                digits[2:4],     # month or day
                digits[-2:],     # last 2 of year
            ]
        return list(set(tokens))

    def generate(self, count: int = 500) -> list[str]:
        """
        Generate psychologically likely passwords
        based on the loaded target information.
        """
        seen    = set()
        results = []

        def add(w):
            w = str(w).strip()
            if w and w not in seen and 3 <= len(w) <= 20:
                seen.add(w)
                results.append(w)

        bases = []
        for key in ["name", "name2", "username",
                    "company", "leet"]:
            val = self.tokens.get(key, "")
            if val:
                bases.append(val)
        bases += self.keyword_tokens

        # ── Core pattern generation ──────────────────
        for base in bases:
            if not base:
                continue
            add(base)
            add(base.capitalize())
            add(base.upper())
            add(_leet(base))
            add(base[::-1])

            # + numbers
            for num in COMMON_NUMS:
                add(base + num)
                add(base.capitalize() + num)
                add(num + base)

            # + symbols
            for sym in COMMON_SYMS:
                add(base + sym)
                add(base.capitalize() + sym)
                add(base + "1" + sym)

            # + years
            for yr in YEARS:
                add(base + yr)
                add(base.capitalize() + yr)
                add(_leet(base) + yr)

            # + birthday fragments
            for tok in self.bday_tokens:
                add(base + tok)
                add(base.capitalize() + tok)
                add(tok + base)

            # + phone fragments
            for tok in self.phone_tokens:
                add(base + tok)
                add(base.capitalize() + tok)

        # ── Cross combinations ───────────────────────
        name  = self.tokens.get("name", "")
        name2 = self.tokens.get("name2", "")

        if name and name2:
            for combo in [
                name + name2,
                name2 + name,
                name + "." + name2,
                name[0] + name2,
                name + name2[0],
                name.capitalize() + name2,
                name + name2.capitalize(),
            ]:
                add(combo)
                for yr in YEARS[:6]:
                    add(combo + yr)
                for sym in COMMON_SYMS[:3]:
                    add(combo + sym)

        company = self.tokens.get("company", "")
        if name and company:
            for combo in [
                name + company,
                company + name,
                name + "@" + company,
            ]:
                add(combo)
                for yr in YEARS[:4]:
                    add(combo + yr)

        # ── Keyboard walk patterns ───────────────────
        walks = [
            "qwerty","qwert","asdf","zxcv",
            "qwerty123","abc123","pass","passwd",
        ]
        for walk in walks:
            add(walk)
            if name:
                add(name + walk)
                add(walk + name)

        # ── Common password templates ────────────────
        if name:
            for template in [
                f"{name}123!",
                f"{name.capitalize()}123",
                f"{name.capitalize()}@123",
                f"i{name}",
                f"i{name}!",
                f"love{name}",
                f"{name}love",
                f"my{name}",
            ]:
                add(template)

        return results[:count]

    def explain(self) -> list[str]:
        """
        Returns human-readable explanation of
        what patterns were detected — useful for
        the UI to show the user what AI is doing.
        """
        explanations = []
        if self.tokens.get("name"):
            explanations.append(
                f"Name '{self.tokens['name']}' detected "
                f"→ generating name+year, name+!, "
                f"leet versions")
        if self.tokens.get("company"):
            explanations.append(
                f"Company '{self.tokens['company']}' "
                f"→ generating work-related combos")
        if self.bday_tokens:
            explanations.append(
                f"Birthday detected "
                f"→ generating {len(self.bday_tokens)} "
                f"date fragments as suffixes")
        if self.phone_tokens:
            explanations.append(
                f"Phone number → generating last-4, "
                f"last-6 digit combos")
        if self.keyword_tokens:
            explanations.append(
                f"{len(self.keyword_tokens)} keywords "
                f"→ leet, caps, suffix variants")
        return explanations
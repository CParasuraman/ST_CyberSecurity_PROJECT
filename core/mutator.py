def mutate(word, rules=None):
    """
    Generate password mutations from a base word.
    rules: list of rule names to apply. None = all rules.
    """
    if rules is None:
        rules = ["leet","capitalise","numbers","symbols","year","reverse","duplicate"]

    variants = []
    seen = set()

    def add(w):
        if w and w not in seen:
            seen.add(w)
            variants.append(w)

    add(word)
    add(word.lower())
    add(word.upper())

    if "capitalise" in rules:
        add(word.capitalize())
        add(word.title())

    if "leet" in rules:
        leet = (word.lower()
                .replace('a','@').replace('e','3')
                .replace('i','1').replace('o','0')
                .replace('s','$').replace('t','7')
                .replace('l','1').replace('g','9'))
        add(leet)
        add(leet.capitalize())
        add(leet.upper())

    if "numbers" in rules:
        for n in ["1","12","123","1234","12345","2","007","69","99","00"]:
            add(word + n)
            add(word.lower() + n)
            add(word.capitalize() + n)

    if "symbols" in rules:
        for s in ["!","@","#","$","!@#","?"]:
            add(word + s)
            add(word.lower() + s)
            add(word.capitalize() + s)

    if "year" in rules:
        for y in ["2020","2021","2022","2023","2024","2025","1990",
                  "1995","1999","2000","2001"]:
            add(word + y)
            add(word.lower() + y)
            add(word.capitalize() + y)

    if "reverse" in rules:
        add(word[::-1])
        add(word.lower()[::-1])

    if "duplicate" in rules:
        add(word + word)
        add(word.lower() + word.lower())

    return variants
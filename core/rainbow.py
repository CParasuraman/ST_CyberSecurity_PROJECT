import json, os, sys

class RainbowPasswordCracker:
    def __init__(self):
        self.rainbow_table_files = ["rainbow_table.json"]
        self.rainbow_table = self.load_rainbow_tables()

    def load_rainbow_tables(self):
        combined = {}
        for file in self.rainbow_table_files:
            path = self.resource_path(file)
            if os.path.exists(path):
                with open(path, "r") as f:
                    combined.update(json.load(f))
            else:
                print(f"File not found: {path}")
        return combined

    def lookup(self, hash_value):
        return self.rainbow_table.get(hash_value.lower())

    @staticmethod
    def resource_path(relative_path):
        try:
            base = sys._MEIPASS
        except Exception:
            base = os.path.abspath("data")
        return os.path.join(base, relative_path)
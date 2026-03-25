import tkinter as tk
from tkinter import ttk, font

# Color theme — dark hacker style
BG_DARK    = "#1e1e2e"
BG_CARD    = "#2a2a3e"
BG_ACCENT  = "#1e3a4a"
FG_PRIMARY = "#cbd5e1"
FG_MUTED   = "#64748b"
FG_BLUE    = "#7dd3fc"
FG_GREEN   = "#22c55e"
BORDER     = "#3a3a50"
BTN_BLUE   = "#185FA5"

class LauncherWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Password Cracker v2.0")
        self.root.geometry("600x620")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(False, False)

        self.mode = tk.StringVar(value="Beginner")
        self._build_titlebar()
        self._build_header()
        self._build_mode_selector()
        self._build_module_grid()
        self._build_quick_start()
        self._build_statusbar()

    # ── Title bar ────────────────────────────────────────────
    def _build_titlebar(self):
        bar = tk.Frame(self.root, bg=BG_CARD, height=36)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # Traffic light dots
        for color in ["#ff5f57", "#febc2e", "#28c840"]:
            tk.Label(bar, bg=color, width=2, relief="flat").pack(
                side="left", padx=(8 if color == "#ff5f57" else 4, 0), pady=10)

        tk.Label(bar, text="Advanced Password Cracker v2.0 — Main Launcher",
                 bg=BG_CARD, fg=FG_MUTED, font=("Courier", 10)).pack(
                 side="left", padx=12)

    # ── Header ───────────────────────────────────────────────
    def _build_header(self):
        frame = tk.Frame(self.root, bg=BG_DARK)
        frame.pack(fill="x", pady=(20, 0))

        tk.Label(frame, text="PASSWORD CRACKER",
                 bg=BG_DARK, fg=FG_BLUE,
                 font=("Courier", 20, "bold")).pack()

        tk.Label(frame, text="Ethical security testing toolkit  ·  For authorized use only",
                 bg=BG_DARK, fg=FG_MUTED,
                 font=("Courier", 9)).pack(pady=(4, 0))

        # Divider
        tk.Frame(self.root, bg=BORDER, height=1).pack(
            fill="x", padx=20, pady=14)

    # ── Mode selector ────────────────────────────────────────
    def _build_mode_selector(self):
        outer = tk.Frame(self.root, bg=BG_DARK)
        outer.pack(fill="x", padx=20)

        tk.Label(outer, text="SELECT MODE",
                 bg=BG_DARK, fg=FG_MUTED,
                 font=("Courier", 8)).pack(anchor="w", pady=(0, 8))

        row = tk.Frame(outer, bg=BG_DARK)
        row.pack(fill="x")

        modes = [
            ("Beginner",    "Step-by-step\nguidance"),
            ("Advanced",    "Full control\n& options"),
            ("Report Mode", "Audit &\ncompliance"),
        ]

        self.mode_btns = {}
        for name, desc in modes:
            btn = tk.Frame(row, bg=BG_CARD, relief="flat",
                           highlightthickness=1,
                           highlightbackground=BORDER)
            btn.pack(side="left", expand=True, fill="x", padx=4)

            tk.Label(btn, text=name, bg=BG_CARD, fg=FG_PRIMARY,
                     font=("Courier", 10, "bold")).pack(pady=(10, 2))
            tk.Label(btn, text=desc, bg=BG_CARD, fg=FG_MUTED,
                     font=("Courier", 8), justify="center").pack(pady=(0, 10))

            btn.bind("<Button-1>", lambda e, n=name: self._select_mode(n))
            for child in btn.winfo_children():
                child.bind("<Button-1>", lambda e, n=name: self._select_mode(n))

            self.mode_btns[name] = btn

        self._select_mode("Beginner")

    def _select_mode(self, name):
        self.mode.set(name)
        for n, btn in self.mode_btns.items():
            if n == name:
                btn.configure(highlightbackground=FG_BLUE, bg=BG_ACCENT)
                for c in btn.winfo_children():
                    c.configure(bg=BG_ACCENT, fg=FG_BLUE)
            else:
                btn.configure(highlightbackground=BORDER, bg=BG_CARD)
                for c in btn.winfo_children():
                    c.configure(bg=BG_CARD,
                                fg=FG_PRIMARY if "bold" in c.cget("font") else FG_MUTED)

    # ── Module grid ──────────────────────────────────────────
    def _build_module_grid(self):
        outer = tk.Frame(self.root, bg=BG_DARK)
        outer.pack(fill="x", padx=20, pady=(16, 0))

        tk.Label(outer, text="OPEN MODULE",
                 bg=BG_DARK, fg=FG_MUTED,
                 font=("Courier", 8)).pack(anchor="w", pady=(0, 8))

        modules = [
            ("Hash Cracker",       "MD5 · SHA1 · SHA256 · NTLM", self._open_hash_cracker),
            ("Hybrid Attack",      "Dict + rules + brute force",   self._open_hybrid),
            ("Wordlist Generator", "AI-assisted smart lists",      self._open_wordlist),
            ("Rainbow Tables",     "Lookup & manage tables",       self._open_rainbow),
            ("Analytics",          "Strength dashboard",           self._open_analytics),
            ("Reports & Logs",     "Export · compliance",          self._open_reports),
        ]

        grid = tk.Frame(outer, bg=BG_DARK)
        grid.pack(fill="x")

        for i, (name, hint, cmd) in enumerate(modules):
            card = tk.Frame(grid, bg=BG_CARD, relief="flat",
                            highlightthickness=1,
                            highlightbackground=BORDER,
                            cursor="hand2")
            card.grid(row=i // 2, column=i % 2,
                      sticky="ew", padx=4, pady=4)
            grid.columnconfigure(0, weight=1)
            grid.columnconfigure(1, weight=1)

            inner = tk.Frame(card, bg=BG_CARD)
            inner.pack(fill="x", padx=12, pady=10)

            tk.Label(inner, text=name, bg=BG_CARD, fg=FG_PRIMARY,
                     font=("Courier", 10, "bold")).pack(anchor="w")
            tk.Label(inner, text=hint, bg=BG_CARD, fg=FG_MUTED,
                     font=("Courier", 8)).pack(anchor="w")

            card.bind("<Button-1>", lambda e, c=cmd: c())
            card.bind("<Enter>",
                      lambda e, f=card: f.configure(highlightbackground=FG_BLUE))
            card.bind("<Leave>",
                      lambda e, f=card: f.configure(highlightbackground=BORDER))
            for w in card.winfo_children() + inner.winfo_children():
                w.bind("<Button-1>", lambda e, c=cmd: c())

    # ── Quick start button ───────────────────────────────────
    def _build_quick_start(self):
        frame = tk.Frame(self.root, bg=BG_DARK)
        frame.pack(fill="x", padx=20, pady=16)

        tk.Button(frame, text="▶  Start Quick Crack",
                  bg=BTN_BLUE, fg="#e0f0ff",
                  font=("Courier", 12, "bold"),
                  relief="flat", bd=0,
                  activebackground="#1a6fbf",
                  activeforeground="#ffffff",
                  cursor="hand2",
                  command=self._open_hash_cracker).pack(fill="x", ipady=10)

    # ── Status bar ───────────────────────────────────────────
    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=BG_CARD, height=30)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        tk.Label(bar, text="●", bg=BG_CARD, fg=FG_GREEN,
                 font=("Courier", 10)).pack(side="left", padx=(12, 4))
        tk.Label(bar, text="Ready · No session active",
                 bg=BG_CARD, fg=FG_MUTED,
                 font=("Courier", 9)).pack(side="left")
        tk.Label(bar, text="v2.0 · Authorized use only",
                 bg=BG_CARD, fg=FG_MUTED,
                 font=("Courier", 9)).pack(side="right", padx=12)

    # ── Module openers (stubs — each filled in next windows) ─
    def _open_hash_cracker(self):
        from ui.hash_cracker_window import HashCrackerWindow
        HashCrackerWindow(self.root)

    def _open_hybrid(self):
        from ui.hybrid_attack_window import HybridAttackWindow
        HybridAttackWindow(self.root)

    def _open_wordlist(self):
        _coming_soon(self.root, "Wordlist Generator")

    def _open_rainbow(self):
        _coming_soon(self.root, "Rainbow Table Manager")

    def _open_analytics(self):
        _coming_soon(self.root, "Analytics Dashboard")

    def _open_reports(self):
        _coming_soon(self.root, "Reports & Logs")


def _coming_soon(parent, name):
    win = tk.Toplevel(parent)
    win.title(name)
    win.geometry("320x160")
    win.configure(bg=BG_DARK)
    win.resizable(False, False)
    tk.Label(win, text=f"{name}",
             bg=BG_DARK, fg=FG_BLUE,
             font=("Courier", 13, "bold")).pack(pady=(30, 8))
    tk.Label(win, text="Coming soon — building next!",
             bg=BG_DARK, fg=FG_MUTED,
             font=("Courier", 10)).pack()
    tk.Button(win, text="Close", command=win.destroy,
              bg=BG_CARD, fg=FG_PRIMARY,
              font=("Courier", 10), relief="flat").pack(pady=16)
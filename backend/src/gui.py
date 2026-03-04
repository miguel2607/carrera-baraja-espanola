import os
import tkinter as tk
from tkinter import messagebox, ttk

from PIL import Image, ImageTk
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

from .game import CarreraEspanola, TRACK_LEN
from .model import SUITS, Card

# ============================================================
# PALETA
# ============================================================
C_BG         = "#0C0C0F"
C_SURFACE    = "#13131A"
C_PANEL      = "#1A1A24"
C_PANEL2     = "#22222F"
C_BORDER     = "#2A2A3D"
C_BORDER2    = "#3A3A55"
C_GOLD       = "#D4A843"
C_GOLD_LIGHT = "#F0C96A"
C_GOLD_DIM   = "#7A5E20"
C_EMERALD    = "#10B981"
C_CRIMSON    = "#E53E5A"
C_SAPPHIRE   = "#4F8EF7"
C_TEXT       = "#F0EDE8"
C_TEXT2      = "#9D9BB5"
C_TEXT3      = "#5A5875"
C_BTN        = "#1E1E2C"
C_BTN_H      = "#2A2A3D"
C_CANVAS     = "#0A0A0D"
C_LANE       = "#141420"

SUIT_COLORS = {
    "Oros":    "#D4A843",
    "Copas":   "#E53E5A",
    "Espadas": "#4F8EF7",
    "Bastos":  "#10B981",
}
SUIT_SYMBOLS = {
    "Oros":    "◈",
    "Copas":   "♥",
    "Espadas": "⚔",
    "Bastos":  "⌘",
}
SVG_SUIT_KEY = {
    "Oros": "coins", "Copas": "cups",
    "Espadas": "swords", "Bastos": "clubs",
}

# Colores y etiquetas para cada jugador (hasta 4)
PLAYER_COLORS = ["#E8C84A", "#E05C7A", "#5BA8F5", "#3DD68C"]
PLAYER_LABELS = ["Jugador 1", "Jugador 2", "Jugador 3", "Jugador 4"]


def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _blend(c1, c2, t):
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    return (f"#{int(r1+(r2-r1)*t):02x}"
            f"{int(g1+(g2-g1)*t):02x}"
            f"{int(b1+(b2-b1)*t):02x}")


def thin_separator(parent, bg=C_BORDER2):
    return tk.Frame(parent, bg=bg, height=1)


# ============================================================
# SetupDialog con jugadores
# ============================================================
class SetupDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Nueva partida")
        self.configure(bg=C_BG)
        self.geometry("620x620")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.focus_force()

        self.result = None
        self.n_players_var = tk.IntVar(value=2)
        self.n_horses_var  = tk.IntVar(value=4)
        self.player_name_vars = [tk.StringVar(value=PLAYER_LABELS[i]) for i in range(4)]
        self.player_suit_vars = [tk.StringVar(value=SUITS[i % len(SUITS)]) for i in range(4)]
        self._player_rows = []

        self._build()
        self._refresh()
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def _build(self):
        border = tk.Frame(self, bg=C_GOLD)
        border.pack(fill="both", expand=True, padx=1, pady=1)
        root = tk.Frame(border, bg=C_BG)
        root.pack(fill="both", expand=True, padx=1, pady=1)

        tk.Frame(root, bg=C_GOLD, height=4).pack(fill="x")

        tr = tk.Frame(root, bg=C_BG)
        tr.pack(fill="x", padx=24, pady=(18, 4))
        tk.Label(tr, text="CARRERA DE CABALLOS", bg=C_BG, fg=C_GOLD,
                 font=("Georgia", 17, "bold")).pack(anchor="w")
        tk.Label(tr, text="Configura jugadores y caballos antes de comenzar",
                 bg=C_BG, fg=C_TEXT2, font=("Georgia", 9, "italic")).pack(anchor="w")

        thin_separator(root, C_BORDER2).pack(fill="x", padx=24, pady=(12, 0))

        body = tk.Frame(root, bg=C_BG)
        body.pack(fill="both", expand=True, padx=24, pady=12)

        # Número de jugadores
        tk.Label(body, text="JUGADORES", bg=C_BG, fg=C_GOLD_LIGHT,
                 font=("Georgia", 9, "bold")).pack(anchor="w")
        rr1 = tk.Frame(body, bg=C_BG)
        rr1.pack(anchor="w", pady=(6, 12))
        for v in range(2, 5):
            tk.Radiobutton(
                rr1, text=f"  {v}  ", variable=self.n_players_var, value=v,
                command=self._refresh,
                bg=C_PANEL, fg=C_TEXT, selectcolor=C_GOLD_DIM,
                activebackground=C_PANEL2, activeforeground=C_TEXT,
                relief="flat", cursor="hand2",
                font=("Georgia", 11, "bold"), indicatoron=0,
                bd=1, highlightthickness=0, padx=14, pady=8,
            ).pack(side="left", padx=(0, 8))

        thin_separator(body, C_BORDER).pack(fill="x", pady=(0, 12))

        # Número de caballos
        tk.Label(body, text="CABALLOS EN CARRERA", bg=C_BG, fg=C_GOLD_LIGHT,
                 font=("Georgia", 9, "bold")).pack(anchor="w")
        tk.Label(body, text="Con 3 caballos uno queda fuera; sus cartas no mueven a nadie",
                 bg=C_BG, fg=C_TEXT3, font=("Georgia", 8, "italic")).pack(anchor="w", pady=(2, 8))
        rr2 = tk.Frame(body, bg=C_BG)
        rr2.pack(anchor="w", pady=(0, 12))
        for v in (3, 4):
            tk.Radiobutton(
                rr2, text=f"  {v} caballos  ", variable=self.n_horses_var, value=v,
                command=self._refresh,
                bg=C_PANEL, fg=C_TEXT, selectcolor=C_GOLD_DIM,
                activebackground=C_PANEL2, activeforeground=C_TEXT,
                relief="flat", cursor="hand2",
                font=("Georgia", 11), indicatoron=0,
                bd=1, highlightthickness=0, padx=12, pady=8,
            ).pack(side="left", padx=(0, 10))

        thin_separator(body, C_BORDER).pack(fill="x", pady=(0, 12))

        # Filas de jugadores
        tk.Label(body, text="NOMBRES Y CABALLOS", bg=C_BG, fg=C_GOLD_LIGHT,
                 font=("Georgia", 9, "bold")).pack(anchor="w", pady=(0, 8))

        self.players_frame = tk.Frame(body, bg=C_BG)
        self.players_frame.pack(fill="x")

        for i in range(4):
            row = tk.Frame(self.players_frame, bg=C_BG)

            # Badge color jugador
            tk.Label(row, text=f"J{i+1}", bg=PLAYER_COLORS[i], fg=C_BG,
                     font=("Georgia", 9, "bold"), width=3, pady=6,
                     ).pack(side="left", padx=(0, 8))

            # Nombre
            tk.Entry(
                row, textvariable=self.player_name_vars[i],
                bg=C_PANEL, fg=C_TEXT, insertbackground=C_TEXT,
                relief="flat", font=("Georgia", 10),
                highlightthickness=1, highlightbackground=C_BORDER2,
                highlightcolor=C_GOLD, width=16,
            ).pack(side="left", padx=(0, 10), ipady=5)

            # Palo (OptionMenu)
            om = tk.OptionMenu(row, self.player_suit_vars[i], *SUITS,
                               command=lambda _v, _i=i: self._refresh())
            om.config(bg=C_PANEL, fg=C_TEXT, activebackground=C_PANEL2,
                      activeforeground=C_TEXT, relief="flat", cursor="hand2",
                      font=("Georgia", 10, "bold"), bd=0, highlightthickness=0)
            om["menu"].config(bg=C_PANEL2, fg=C_TEXT,
                              activebackground=C_GOLD_DIM, activeforeground=C_TEXT,
                              font=("Georgia", 10))
            om.pack(side="left")

            self._player_rows.append(row)

        # Hint
        self.hint_var = tk.StringVar(value="")
        tk.Label(body, textvariable=self.hint_var, bg=C_BG, fg=C_GOLD,
                 font=("Georgia", 9, "italic")).pack(anchor="w", pady=(10, 0))

        thin_separator(root, C_BORDER2).pack(fill="x", padx=24)
        footer = tk.Frame(root, bg=C_BG)
        footer.pack(fill="x", padx=24, pady=14)

        tk.Button(footer, text="Cancelar", command=self.on_cancel,
                  bg=C_BTN, fg=C_TEXT2, relief="flat", cursor="hand2",
                  font=("Georgia", 10), bd=0, padx=20, pady=10,
                  ).pack(side="right", padx=(10, 0))
        self.btn_ok = tk.Button(footer, text="⚑  INICIAR CARRERA", command=self.on_ok,
                                bg=C_GOLD, fg=C_BG, relief="flat", cursor="hand2",
                                font=("Georgia", 11, "bold"), bd=0, padx=22, pady=10,
                                activebackground=C_GOLD_LIGHT, activeforeground=C_BG)
        self.btn_ok.pack(side="right")

    def _refresh(self):
        n = self.n_players_var.get()
        n_horses = self.n_horses_var.get()

        for i, row in enumerate(self._player_rows):
            if i < n:
                row.pack(fill="x", pady=3)
            else:
                row.pack_forget()

        chosen = [self.player_suit_vars[i].get() for i in range(n)]
        dupes  = len(chosen) != len(set(chosen))

        if dupes:
            self.hint_var.set("⚠ Dos jugadores no pueden elegir el mismo caballo")
            self.btn_ok.config(state="disabled")
            return
        if n_horses == 3 and n > 3:
            self.hint_var.set("⚠ Con 3 caballos puede haber máximo 3 jugadores")
            self.btn_ok.config(state="disabled")
            return
        self.hint_var.set("✓ Todo listo")
        self.btn_ok.config(state="normal")

    def on_ok(self):
        n        = self.n_players_var.get()
        n_horses = self.n_horses_var.get()
        players  = []
        chosen   = []
        for i in range(n):
            name = self.player_name_vars[i].get().strip() or PLAYER_LABELS[i]
            suit = self.player_suit_vars[i].get()
            if suit in chosen:
                messagebox.showerror("Error", "Dos jugadores no pueden elegir el mismo caballo.")
                return
            chosen.append(suit)
            players.append({"name": name, "suit": suit, "color": PLAYER_COLORS[i]})

        if n_horses == 4:
            active_suits = set(SUITS)
        else:
            active_suits = set(chosen)
            for s in SUITS:
                if len(active_suits) >= 3:
                    break
                active_suits.add(s)

        self.result = {"active_suits": active_suits, "players": players}
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()

    def on_cancel(self):
        self.result = None
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()


# ============================================================
# App principal
# ============================================================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Carrera de Caballos — Baraja Española")
        self.configure(bg=C_BG)
        self.geometry("1400x820")
        self.minsize(1200, 700)

        cfg = self._ask_setup()
        if cfg is None:
            self.destroy()
            return

        self.game    = CarreraEspanola()
        self.players = []
        self._apply_config(cfg)

        root_dir = os.path.dirname(os.path.dirname(__file__))
        self.svg_dir       = os.path.join(root_dir, "assets", "svg")
        self.png_cache_dir = os.path.join(root_dir, "assets", "png_cache")
        os.makedirs(self.png_cache_dir, exist_ok=True)

        self.tk_img_cache: dict = {}
        self.CP_SIZE    = (88, 124)
        self.HORSE_SIZE = (64, 90)
        self.LAST_SIZE  = (240, 340)

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Dark.TNotebook", background=C_SURFACE, borderwidth=0)
        style.configure("Dark.TNotebook.Tab",
                        padding=(16, 9), background=C_PANEL,
                        foreground=C_TEXT2, font=("Georgia", 10, "bold"))
        style.map("Dark.TNotebook.Tab",
                  background=[("selected", C_GOLD_DIM)],
                  foreground=[("selected", C_GOLD_LIGHT)])

        self._build_layout()
        self._init_board()
        self._clear_log()
        self._render_all()

        active_str = ", ".join(sorted(self.game.active_suits))
        self._log_header(f"Partida iniciada — Caballos: {active_str}")
        for p in self.players:
            sym = SUIT_SYMBOLS.get(p["suit"], "")
            self._log(f"  {sym} {p['suit']}  ←  {p['name']}", "player_info")

        self.bind("<space>", lambda e: self.on_step())
        self.bind("<Configure>", self._on_resize)

    # ── config ─────────────────────────────────────────────────
    def _ask_setup(self):
        dlg = SetupDialog(self)
        self.wait_window(dlg)
        return dlg.result

    def _apply_config(self, cfg):
        self.players = cfg["players"]
        self.game.reset(active_suits=cfg["active_suits"])
        self.suit_to_player = {p["suit"]: p for p in self.players}

    # ── SVG ────────────────────────────────────────────────────
    def _svg_name(self, card):
        return f"card_{SVG_SUIT_KEY[card.suit]}_{card.rank:02d}.svg"

    def _svg_to_png(self, svg_path, png_path, size):
        w, h = size
        drawing = svg2rlg(svg_path)
        if drawing.width and drawing.height:
            sx, sy = w / drawing.width, h / drawing.height
            drawing.scale(sx, sy)
            drawing.width, drawing.height = w, h
        renderPM.drawToFile(drawing, png_path, fmt="PNG")

    def _get_photo_from_svg(self, svg_filename, size):
        svg_path = os.path.join(self.svg_dir, svg_filename)
        if not os.path.exists(svg_path):
            return None
        w, h = size
        key  = f"{svg_filename}_{w}x{h}"
        if key in self.tk_img_cache:
            return self.tk_img_cache[key]
        png_path = os.path.join(self.png_cache_dir, f"{key}.png")
        if not os.path.exists(png_path):
            self._svg_to_png(svg_path, png_path, size)
        photo = ImageTk.PhotoImage(Image.open(png_path).convert("RGBA"))
        self.tk_img_cache[key] = photo
        return photo

    def _get_card_photo(self, card, size):
        return self._get_photo_from_svg(self._svg_name(card), size)

    def _get_back_photo(self, size):
        p = self._get_photo_from_svg("card_back.svg", size)
        return p or self._get_photo_from_svg("back.svg", size)

    # ============================================================
    # Layout
    # ============================================================
    def _build_layout(self):
        # Top bar
        topbar = tk.Frame(self, bg=C_SURFACE, height=64)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        tk.Frame(topbar, bg=C_GOLD, height=3).place(x=0, y=0, relwidth=1)

        tb = tk.Frame(topbar, bg=C_SURFACE)
        tb.pack(side="left", padx=(24, 0))
        tk.Label(tb, text="⚑", bg=C_SURFACE, fg=C_GOLD,
                 font=("Georgia", 22)).pack(side="left", padx=(0, 10))
        tv = tk.Frame(tb, bg=C_SURFACE)
        tv.pack(side="left")
        tk.Label(tv, text="CARRERA DE CABALLOS", bg=C_SURFACE, fg=C_TEXT,
                 font=("Georgia", 14, "bold")).pack(anchor="w")
        tk.Label(tv, text="Baraja Española", bg=C_SURFACE, fg=C_GOLD,
                 font=("Georgia", 9, "italic")).pack(anchor="w")

        self.status_var = tk.StringVar(value="Presiona ESPACIO para voltear")
        sf = tk.Frame(topbar, bg=C_PANEL)
        sf.pack(side="left", padx=24, pady=16)
        tk.Label(sf, textvariable=self.status_var, bg=C_PANEL, fg=C_TEXT2,
                 font=("Georgia", 10, "italic"), padx=14, pady=6).pack()

        br = tk.Frame(topbar, bg=C_SURFACE)
        br.pack(side="right", padx=24)
        tk.Button(br, text="↺  Nueva partida", command=self.on_new,
                  bg=C_BTN, fg=C_TEXT2, relief="flat", cursor="hand2",
                  font=("Georgia", 10, "bold"), padx=18, pady=10,
                  activebackground=C_BTN_H, activeforeground=C_TEXT, bd=0,
                  ).pack(side="right", padx=(10, 0))
        self.btn_flip = tk.Button(br, text="▶  VOLTEAR CARTA", command=self.on_step,
                                  bg=C_GOLD, fg=C_BG, relief="flat", cursor="hand2",
                                  font=("Georgia", 11, "bold"), padx=22, pady=10,
                                  activebackground=C_GOLD_LIGHT, activeforeground=C_BG, bd=0)
        self.btn_flip.pack(side="right")

        tk.Frame(self, bg=C_GOLD_DIM, height=1).pack(fill="x")

        main = tk.Frame(self, bg=C_BG)
        main.pack(fill="both", expand=True)

        # Tablero
        lw = tk.Frame(main, bg=C_BG)
        lw.pack(side="left", fill="both", expand=True, padx=(16, 8), pady=16)
        bh = tk.Frame(lw, bg=C_BG)
        bh.pack(fill="x", pady=(0, 8))
        tk.Label(bh, text="TABLERO", bg=C_BG, fg=C_GOLD,
                 font=("Georgia", 11, "bold")).pack(side="left")
        tk.Label(bh, text="  —  Checkpoints arriba · Carriles abajo",
                 bg=C_BG, fg=C_TEXT3, font=("Georgia", 9, "italic")).pack(side="left")
        cb = tk.Frame(lw, bg=C_GOLD_DIM)
        cb.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(cb, bg=C_CANVAS, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=1, pady=1)

        # Sidebar
        self.right = tk.Frame(main, bg=C_SURFACE, width=395)
        self.right.pack(side="right", fill="y", padx=(0, 16), pady=16)
        self.right.pack_propagate(False)
        tk.Frame(self.right, bg=C_GOLD_DIM, width=2).place(x=0, y=0, relheight=1)

        self.tabs = ttk.Notebook(self.right, style="Dark.TNotebook")
        self.tabs.pack(fill="both", expand=True, padx=(8, 0))

        self.tab_players = tk.Frame(self.tabs, bg=C_SURFACE)
        self.tab_card    = tk.Frame(self.tabs, bg=C_SURFACE)
        self.tab_log     = tk.Frame(self.tabs, bg=C_SURFACE)
        self.tabs.add(self.tab_players, text="  Jugadores  ")
        self.tabs.add(self.tab_card,    text="  Carta  ")
        self.tabs.add(self.tab_log,     text="  Registro  ")

        self._build_tab_players()
        self._build_tab_card()
        self._build_tab_log()

    # ── Tab Jugadores ─────────────────────────────────────────
    def _build_tab_players(self):
        t = self.tab_players
        tk.Label(t, text="JUGADORES EN CARRERA", bg=C_SURFACE, fg=C_GOLD,
                 font=("Georgia", 9, "bold")).pack(anchor="w", padx=18, pady=(18, 2))
        tk.Label(t, text="Posiciones en tiempo real", bg=C_SURFACE, fg=C_TEXT3,
                 font=("Georgia", 8, "italic")).pack(anchor="w", padx=18, pady=(0, 10))
        thin_separator(t, C_BORDER).pack(fill="x", padx=18, pady=(0, 12))

        self.player_panel = tk.Frame(t, bg=C_SURFACE)
        self.player_panel.pack(fill="x", padx=18)
        self._player_widgets = []
        self._rebuild_player_panel()

        thin_separator(t, C_BORDER).pack(fill="x", padx=18, pady=(16, 10))
        tk.Label(t, text="TODOS LOS CABALLOS", bg=C_SURFACE, fg=C_TEXT3,
                 font=("Georgia", 8, "bold")).pack(anchor="w", padx=18, pady=(0, 8))

        self.horses_panel = tk.Frame(t, bg=C_SURFACE)
        self.horses_panel.pack(fill="x", padx=18)
        self._horse_widgets = {}
        self._build_horses_panel()

    def _rebuild_player_panel(self):
        for w in self.player_panel.winfo_children():
            w.destroy()
        self._player_widgets = []

        for p in self.players:
            suit  = p["suit"]
            color = p["color"]
            sym   = SUIT_SYMBOLS.get(suit, "")
            sc    = SUIT_COLORS.get(suit, C_TEXT)

            card_frame = tk.Frame(self.player_panel, bg=C_PANEL,
                                  highlightbackground=color, highlightthickness=2)
            card_frame.pack(fill="x", pady=4)

            tk.Frame(card_frame, bg=color, width=5).pack(side="left", fill="y")

            inner = tk.Frame(card_frame, bg=C_PANEL)
            inner.pack(side="left", fill="both", expand=True, padx=10, pady=8)

            top_r = tk.Frame(inner, bg=C_PANEL)
            top_r.pack(fill="x")
            tk.Label(top_r, text=p["name"], bg=C_PANEL, fg=color,
                     font=("Georgia", 11, "bold")).pack(side="left")
            tk.Label(top_r, text=f"  {sym} {suit}", bg=C_PANEL, fg=sc,
                     font=("Georgia", 10)).pack(side="left")

            prog_r = tk.Frame(inner, bg=C_PANEL)
            prog_r.pack(fill="x", pady=(6, 0))

            bar_bg = tk.Frame(prog_r, bg=C_BORDER, height=8)
            bar_bg.pack(side="left", fill="x", expand=True)
            bar_bg.pack_propagate(False)
            bar_fill = tk.Frame(bar_bg, bg=color, height=8)
            bar_fill.place(x=0, y=0, relheight=1, relwidth=0.0)

            pos_lbl = tk.Label(prog_r, text="0 / 7", bg=C_PANEL, fg=C_TEXT3,
                               font=("Georgia", 9))
            pos_lbl.pack(side="left", padx=(8, 0))

            self._player_widgets.append({
                "suit": suit, "color": color,
                "bar_fill": bar_fill, "pos_lbl": pos_lbl,
                "card_frame": card_frame,
            })

    def _build_horses_panel(self):
        for w in self.horses_panel.winfo_children():
            w.destroy()
        self._horse_widgets = {}

        for suit in SUITS:
            if suit not in self.game.active_suits:
                continue
            color = SUIT_COLORS[suit]
            sym   = SUIT_SYMBOLS[suit]
            owner = self.suit_to_player.get(suit)
            owner_txt   = f"← {owner['name']}" if owner else "Sin dueño"
            owner_color = owner["color"] if owner else C_TEXT3

            row = tk.Frame(self.horses_panel, bg=C_SURFACE)
            row.pack(fill="x", pady=2)

            tk.Label(row, text=sym, bg=C_SURFACE, fg=color,
                     font=("Georgia", 13, "bold"), width=3).pack(side="left")
            tk.Label(row, text=suit, bg=C_SURFACE, fg=color,
                     font=("Georgia", 9, "bold"), width=8, anchor="w").pack(side="left")

            bar_bg = tk.Frame(row, bg=C_BORDER, height=6, width=100)
            bar_bg.pack(side="left", padx=(4, 6))
            bar_bg.pack_propagate(False)
            bar_fill = tk.Frame(bar_bg, bg=color, height=6)
            bar_fill.place(x=0, y=0, relheight=1, relwidth=0.0)

            pos_lbl = tk.Label(row, text="0", bg=C_SURFACE, fg=C_TEXT3,
                               font=("Georgia", 9), width=2)
            pos_lbl.pack(side="left")

            tk.Label(row, text=owner_txt, bg=C_SURFACE, fg=owner_color,
                     font=("Georgia", 8, "italic")).pack(side="left", padx=(6, 0))

            self._horse_widgets[suit] = {"bar_fill": bar_fill, "pos_lbl": pos_lbl}

    # ── Tab Carta ─────────────────────────────────────────────
    def _build_tab_card(self):
        t = self.tab_card
        tk.Label(t, text="ÚLTIMA CARTA", bg=C_SURFACE, fg=C_GOLD,
                 font=("Georgia", 9, "bold")).pack(anchor="w", padx=18, pady=(18, 2))
        self.last_name_var = tk.StringVar(value="— ninguna —")
        tk.Label(t, textvariable=self.last_name_var, bg=C_SURFACE, fg=C_TEXT2,
                 font=("Georgia", 11, "italic")).pack(anchor="w", padx=18, pady=(0, 10))
        thin_separator(t, C_BORDER).pack(fill="x", padx=18)

        wrap = tk.Frame(t, bg=C_PANEL, highlightbackground=C_BORDER2, highlightthickness=1)
        wrap.pack(padx=18, pady=14)
        self.last_canvas = tk.Canvas(wrap, width=self.LAST_SIZE[0], height=self.LAST_SIZE[1],
                                     bg=C_PANEL, highlightthickness=0)
        self.last_canvas.pack(padx=14, pady=14)
        self.last_item = self.last_canvas.create_image(
            self.LAST_SIZE[0]//2, self.LAST_SIZE[1]//2, anchor="center")

        back_ph = self._get_back_photo(self.LAST_SIZE)
        if back_ph:
            self.last_canvas.itemconfig(self.last_item, image=back_ph)
            self._last_back_photo = back_ph
        self.last_placeholder = self.last_canvas.create_text(
            self.LAST_SIZE[0]//2, self.LAST_SIZE[1]//2,
            text="" if back_ph else "Voltea una carta\npara comenzar",
            fill=C_TEXT3, font=("Georgia", 11, "italic"), justify="center")

        thin_separator(t, C_BORDER).pack(fill="x", padx=18, pady=(0, 10))
        tip = tk.Frame(t, bg=C_PANEL, highlightbackground=C_BORDER, highlightthickness=1)
        tip.pack(fill="x", padx=18)
        tk.Label(tip, text="⌨  ESPACIO para voltear carta", bg=C_PANEL, fg=C_TEXT3,
                 font=("Georgia", 9, "italic"), padx=12, pady=8).pack()

    # ── Tab Registro ──────────────────────────────────────────
    def _build_tab_log(self):
        t = self.tab_log
        hdr = tk.Frame(t, bg=C_SURFACE)
        hdr.pack(fill="x", padx=18, pady=(18, 8))
        tk.Label(hdr, text="REGISTRO DE EVENTOS", bg=C_SURFACE, fg=C_GOLD,
                 font=("Georgia", 9, "bold")).pack(side="left")
        tk.Button(hdr, text="Limpiar", command=self._clear_log,
                  bg=C_BTN, fg=C_TEXT3, relief="flat", cursor="hand2",
                  font=("Georgia", 9), padx=10, pady=4, bd=0,
                  activebackground=C_BTN_H, activeforeground=C_TEXT).pack(side="right")

        thin_separator(t, C_BORDER).pack(fill="x", padx=18, pady=(0, 8))
        box = tk.Frame(t, bg=C_PANEL, highlightbackground=C_BORDER2, highlightthickness=1)
        box.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.log = tk.Text(box, wrap="word", bg=C_PANEL, fg=C_TEXT,
                           insertbackground=C_TEXT, relief="flat", borderwidth=0,
                           font=("Consolas", 9), selectbackground=C_BORDER2)
        self.log.pack(fill="both", expand=True, padx=10, pady=10)
        self.log.config(state="disabled")
        self.log.tag_config("header",      foreground=C_GOLD,    font=("Georgia", 9, "bold"))
        self.log.tag_config("player_info", foreground=C_TEXT2)
        self.log.tag_config("event",       foreground=C_TEXT2)
        self.log.tag_config("cp",          foreground=C_SAPPHIRE)
        self.log.tag_config("penalty",     foreground=C_CRIMSON)
        self.log.tag_config("winner",      foreground=C_EMERALD, font=("Georgia", 10, "bold"))

    # ============================================================
    # Tablero canvas
    # ============================================================
    def _layout_board(self):
        self.update_idletasks()
        self.w = max(860, self.canvas.winfo_width())
        self.h = max(580, self.canvas.winfo_height())
        self.pad     = 32
        self.label_w = 96
        self.cp_y    = 130
        half_cp      = self.CP_SIZE[0] // 2
        self.cp_x0   = self.pad + self.label_w + half_cp
        usable_w     = self.w - self.cp_x0 - self.pad - half_cp
        self.cp_gap  = int(usable_w / max(TRACK_LEN - 1, 1))
        self.lanes_y0 = self.cp_y + self.CP_SIZE[1] // 2 + 72
        n_active = len(self.game.active_suits)
        self.lane_gap = max(80, int((self.h - self.lanes_y0 - 28) / max(n_active, 1)))

    def _pos_to_x(self, pos):
        x0   = self.cp_x0
        x1   = self.cp_x0 + self.cp_gap * (TRACK_LEN - 1) + self.CP_SIZE[0] // 2
        step = (x1 - x0) / TRACK_LEN
        return int(x0 + pos * step)

    def _init_board(self):
        self.canvas.delete("all")
        self._layout_board()
        self.cp_items    = []
        self.horse_items = {}
        self.lane_y      = {}

        label_x  = self.pad + self.label_w
        track_x0 = self._pos_to_x(0)
        track_x1 = self._pos_to_x(TRACK_LEN)

        # Encabezado checkpoints
        self.canvas.create_text(self.pad, 12, text="CHECKPOINTS", fill=C_GOLD,
                                font=("Georgia", 10, "bold"), anchor="w")
        self.canvas.create_text(self.pad + 112, 12,
                                text="— se revelan cuando todos los caballos superan la posición",
                                fill=C_TEXT3, font=("Georgia", 8, "italic"), anchor="w")

        # Slots
        for i in range(TRACK_LEN):
            x  = self.cp_x0 + i * self.cp_gap
            y  = self.cp_y
            hw = self.CP_SIZE[0] // 2
            hh = self.CP_SIZE[1] // 2
            self.canvas.create_rectangle(x-hw+5, y-hh+6, x+hw+5, y+hh+6,
                                         outline="", fill="#06060A")
            self.canvas.create_rectangle(x-hw-4, y-hh-4, x+hw+4, y+hh+4,
                                         outline=C_GOLD_DIM, width=1, fill="")
            self.canvas.create_rectangle(x-hw, y-hh, x+hw, y+hh,
                                         outline=C_BORDER2, width=1, fill=C_PANEL)
            self.canvas.create_text(x, y+hh+13, text=str(i+1),
                                    fill=C_GOLD_DIM, font=("Georgia", 8))
            img_id = self.canvas.create_image(x, y, anchor="center")
            txt_id = self.canvas.create_text(x, y, text="", fill=C_TEXT,
                                             font=("Georgia", 10, "bold"))
            self.cp_items.append((img_id, txt_id))

        # Separador
        sep_y = self.cp_y + self.CP_SIZE[1] // 2 + 28
        self.canvas.create_line(self.pad, sep_y, self.w - self.pad, sep_y,
                                fill=C_BORDER, width=1, dash=(4, 10))

        # Encabezado carriles
        lane_hdr_y = self.lanes_y0 - 34
        self.canvas.create_text(self.pad, lane_hdr_y, text="CARRILES", fill=C_GOLD,
                                font=("Georgia", 10, "bold"), anchor="w")
        self.canvas.create_text(self.pad + 86, lane_hdr_y,
                                text="— avanza con cada carta del palo",
                                fill=C_TEXT3, font=("Georgia", 8, "italic"), anchor="w")

        active_suits = [s for s in SUITS if s in self.game.active_suits]

        # Bandas
        for idx, suit in enumerate(active_suits):
            y         = self.lanes_y0 + idx * self.lane_gap
            band_fill = C_LANE if idx % 2 == 0 else _blend(C_LANE, "#000000", 0.3)
            self.canvas.create_rectangle(label_x, y - self.lane_gap//2 + 2,
                                         self.w - self.pad, y + self.lane_gap//2 - 2,
                                         fill=band_fill, outline="")

        # Meta
        mx          = track_x1
        lane_top    = self.lanes_y0 - self.lane_gap//2 + 2
        lane_bottom = (self.lanes_y0 + (len(active_suits)-1) * self.lane_gap
                       + self.lane_gap//2 - 2)
        self.canvas.create_rectangle(mx-4, lane_top, mx+4, lane_bottom,
                                     fill=C_GOLD, outline="")
        self.canvas.create_text(mx, lane_top - 16, text="META",
                                fill=C_GOLD_LIGHT, font=("Georgia", 9, "bold"))

        # Carriles individuales
        for idx, suit in enumerate(active_suits):
            y     = self.lanes_y0 + idx * self.lane_gap
            self.lane_y[suit] = y
            color = SUIT_COLORS[suit]
            sym   = SUIT_SYMBOLS[suit]

            self.canvas.create_line(track_x0, y, mx, y,
                                    fill=_blend(color, "#000000", 0.65), width=2)
            for p in range(TRACK_LEN + 1):
                tx = self._pos_to_x(p)
                self.canvas.create_line(tx, y-20, tx, y+20,
                                        fill=C_GOLD_DIM if p == TRACK_LEN else C_BORDER2,
                                        width=1)

            lx = label_x - 8
            self.canvas.create_text(lx, y-12, text=sym,
                                    fill=color, font=("Georgia", 16, "bold"), anchor="e")
            self.canvas.create_text(lx, y+8, text=suit,
                                    fill=_blend(color, C_TEXT3, 0.35),
                                    font=("Georgia", 8, "bold"), anchor="e")

            # Nombre del jugador dueño debajo del símbolo
            owner = self.suit_to_player.get(suit)
            if owner:
                self.canvas.create_text(lx, y+22, text=owner["name"],
                                        fill=owner["color"],
                                        font=("Georgia", 7, "italic"), anchor="e")

            # Token caballo
            horse_card = Card(rank=11, suit=suit)
            horse_img  = self._get_card_photo(horse_card, self.HORSE_SIZE)
            hx         = self._pos_to_x(0)

            if horse_img:
                img_id   = self.canvas.create_image(hx, y, anchor="center", image=horse_img)
                fallback = None
            else:
                r  = 22
                img_id = None
                fb_bg  = self.canvas.create_oval(hx-r, y-r, hx+r, y+r,
                                                  fill=_blend(color, "#000000", 0.55),
                                                  outline=color, width=2)
                fb_txt = self.canvas.create_text(hx, y, text=sym, fill=color,
                                                  font=("Georgia", 14, "bold"))
                fallback = (fb_bg, fb_txt)

            self.horse_items[suit] = (img_id, fallback)

    def _on_resize(self, _evt):
        if getattr(self, "_resize_after_id", None):
            self.after_cancel(self._resize_after_id)
        self._resize_after_id = self.after(130, self._rebuild_after_resize)

    def _rebuild_after_resize(self):
        self._init_board()
        self._render_all()

    # ============================================================
    # Log
    # ============================================================
    def _clear_log(self):
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")

    def _log(self, msg, tag="event"):
        self.log.config(state="normal")
        self.log.insert("end", msg + "\n", tag)
        self.log.see("end")
        self.log.config(state="disabled")

    def _log_header(self, msg):
        self._log(f"▸ {msg}", "header")

    # ============================================================
    # Render
    # ============================================================
    def _render_all(self):
        back = self._get_back_photo(self.CP_SIZE)
        for i in range(TRACK_LEN):
            img_id, txt_id = self.cp_items[i]
            if self.game.revealed[i]:
                photo = self._get_card_photo(self.game.checkpoints[i], self.CP_SIZE)
                if photo:
                    self.canvas.itemconfig(img_id, image=photo)
                    self.canvas.itemconfig(txt_id, text="")
                else:
                    self.canvas.itemconfig(img_id, image="")
                    self.canvas.itemconfig(txt_id, text=self.game.checkpoints[i].short())
            else:
                if back:
                    self.canvas.itemconfig(img_id, image=back)
                    self.canvas.itemconfig(txt_id, text="")
                else:
                    self.canvas.itemconfig(img_id, image="")
                    self.canvas.itemconfig(txt_id, text="?")

        for suit in self.game.active_suits:
            pos = self.game.positions.get(suit, 0)
            self._move_horse(suit, pos)

        self._update_player_panel()

    def _move_horse(self, suit, pos):
        if suit not in self.lane_y:
            return
        y      = self.lane_y[suit]
        x      = self._pos_to_x(pos)
        img_id, fallback = self.horse_items[suit]
        if img_id is not None:
            self.canvas.coords(img_id, x, y)
        if fallback is not None:
            bg_id, txt_id = fallback
            r = 22
            self.canvas.coords(bg_id, x-r, y-r, x+r, y+r)
            self.canvas.coords(txt_id, x, y)

    def _update_player_panel(self):
        for pw in self._player_widgets:
            suit = pw["suit"]
            pos  = self.game.positions.get(suit, 0)
            pw["bar_fill"].place(relwidth=pos / TRACK_LEN)
            pw["pos_lbl"].config(text=f"{pos} / {TRACK_LEN}")
            leader = max(self.game.positions.values()) if self.game.positions else 0
            thickness = 3 if pos == leader and pos > 0 else 2
            pw["card_frame"].config(highlightthickness=thickness)

        for suit, ww in self._horse_widgets.items():
            pos = self.game.positions.get(suit, 0)
            ww["bar_fill"].place(relwidth=pos / TRACK_LEN)
            ww["pos_lbl"].config(text=str(pos))

    # ============================================================
    # Acciones
    # ============================================================
    def on_new(self):
        cfg = self._ask_setup()
        if cfg is None:
            return
        self._apply_config(cfg)
        self._clear_log()
        self.last_name_var.set("— ninguna —")
        back_ph = self._get_back_photo(self.LAST_SIZE)
        if back_ph:
            self.last_canvas.itemconfig(self.last_item, image=back_ph)
            self._last_back_photo = back_ph
            self.last_canvas.itemconfig(self.last_placeholder, text="")
        else:
            self.last_canvas.itemconfig(self.last_item, image="")
            self.last_canvas.itemconfig(self.last_placeholder, text="Voltea una carta\npara comenzar")
        self.status_var.set("Nueva partida lista — presiona ESPACIO")
        self._rebuild_player_panel()
        self._build_horses_panel()
        self._init_board()
        self._render_all()
        self._log_header("Nueva partida")
        for p in self.players:
            sym = SUIT_SYMBOLS.get(p["suit"], "")
            self._log(f"  {sym} {p['suit']}  ←  {p['name']}", "player_info")

    def on_step(self):
        try:
            info = self.game.step()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self.last_name_var.set(info.drawn.name)
        sym = SUIT_SYMBOLS.get(info.drawn.suit, "")
        self.status_var.set(f"{sym}  {info.drawn.name}")

        photo = self._get_card_photo(info.drawn, self.LAST_SIZE)
        if photo:
            self.last_canvas.itemconfig(self.last_item, image=photo)
            self.last_canvas.itemconfig(self.last_placeholder, text="")
        else:
            self.last_canvas.itemconfig(self.last_item, image="")

        if info.advanced_suit:
            owner = self.suit_to_player.get(info.advanced_suit)
            suffix = f" ({owner['name']})" if owner else ""
            self._log(f"  {sym} {info.drawn.name}  →  avanza {info.advanced_suit}{suffix}", "event")
        else:
            self._log(f"  {info.drawn.name}  →  (palo inactivo)", "event")

        if info.revealed_checkpoint_index is not None and info.revealed_card is not None:
            idx = info.revealed_checkpoint_index + 1
            self._log(f"  ◉ Checkpoint #{idx} revelado: {info.revealed_card.name}", "cp")
            if info.penalty_suit:
                owner = self.suit_to_player.get(info.penalty_suit)
                suffix = f" ({owner['name']})" if owner else ""
                self._log(f"  ⚠ Penalidad: {info.penalty_suit}{suffix} retrocede 1 casilla", "penalty")

        self._render_all()

        if info.winner:
            self._show_winner(info.winner)

    def _show_winner(self, winner_suit):
        win_sym    = SUIT_SYMBOLS.get(winner_suit, "")
        suit_color = SUIT_COLORS.get(winner_suit, C_TEXT)
        owner      = self.suit_to_player.get(winner_suit)

        if owner:
            self._log(f"  ★ GANADOR: {win_sym} {winner_suit}  ←  {owner['name']}", "winner")
            self.status_var.set(f"★  Ganó: {owner['name']} ({winner_suit})")
        else:
            self._log(f"  ★ GANADOR: {win_sym} {winner_suit}", "winner")
            self.status_var.set(f"★  Ganó: {winner_suit}")

        # Diálogo ganador
        win_dlg = tk.Toplevel(self)
        win_dlg.title("Carrera finalizada")
        win_dlg.configure(bg=C_BG)
        win_dlg.geometry("430x320")
        win_dlg.resizable(False, False)
        win_dlg.transient(self)
        win_dlg.grab_set()

        tk.Frame(win_dlg, bg=C_GOLD, height=4).pack(fill="x")
        tk.Frame(win_dlg, bg=suit_color, height=2).pack(fill="x")

        tk.Label(win_dlg, text="★  CARRERA FINALIZADA  ★", bg=C_BG, fg=C_GOLD,
                 font=("Georgia", 12, "bold")).pack(pady=(20, 4))

        if owner:
            tk.Label(win_dlg, text=owner["name"], bg=C_BG, fg=owner["color"],
                     font=("Georgia", 22, "bold")).pack(pady=(0, 2))
            tk.Label(win_dlg, text=f"{win_sym}  {winner_suit}", bg=C_BG, fg=suit_color,
                     font=("Georgia", 13)).pack(pady=(0, 12))
        else:
            tk.Label(win_dlg, text=f"{win_sym}  {winner_suit}", bg=C_BG, fg=suit_color,
                     font=("Georgia", 22, "bold")).pack(pady=(0, 16))

        # Clasificación
        if self.players:
            rf = tk.Frame(win_dlg, bg=C_PANEL)
            rf.pack(fill="x", padx=28, pady=(0, 10))
            sorted_p = sorted(self.players,
                              key=lambda p: self.game.positions.get(p["suit"], 0),
                              reverse=True)
            medals = ["🥇", "🥈", "🥉", " 4."]
            for rank, p in enumerate(sorted_p):
                pos   = self.game.positions.get(p["suit"], 0)
                sym   = SUIT_SYMBOLS.get(p["suit"], "")
                medal = medals[rank] if rank < len(medals) else f"{rank+1}."
                row   = tk.Frame(rf, bg=C_PANEL)
                row.pack(fill="x", padx=10, pady=2)
                tk.Label(row, text=medal, bg=C_PANEL, fg=C_TEXT,
                         font=("Georgia", 10), width=3).pack(side="left")
                tk.Label(row, text=p["name"], bg=C_PANEL, fg=p["color"],
                         font=("Georgia", 10, "bold")).pack(side="left")
                tk.Label(row, text=f"  {sym} {p['suit']}  — casilla {pos}",
                         bg=C_PANEL, fg=C_TEXT3, font=("Georgia", 9)).pack(side="left")

        thin_separator(win_dlg, C_BORDER2).pack(fill="x", padx=28, pady=(0, 10))
        tk.Button(win_dlg, text="↺  Nueva partida",
                  command=lambda: (win_dlg.destroy(), self.on_new()),
                  bg=C_GOLD, fg=C_BG, relief="flat", cursor="hand2",
                  font=("Georgia", 11, "bold"), padx=24, pady=10,
                  activebackground=C_GOLD_LIGHT, activeforeground=C_BG).pack()
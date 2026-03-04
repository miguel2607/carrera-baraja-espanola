import os
from typing import Optional, Dict, Any, List

from flask import Flask, jsonify, render_template, send_from_directory, request
from flask_cors import CORS

from src.game import CarreraEspanola, TRACK_LEN, StepInfo
from src.model import SUITS, Card


app = Flask(__name__)
CORS(app) # Habilita CORS para todas las rutas

# Estado de juego simple en memoria (suficiente para demo en Render)
game: Optional[CarreraEspanola] = None
players: List[Dict[str, Any]] = []
suit_to_player: Dict[str, Dict[str, Any]] = {}

SVG_SUIT_KEY = {
    "Oros": "coins",
    "Copas": "cups",
    "Espadas": "swords",
    "Bastos": "clubs",
}

PLAYER_COLORS = ["#E8C84A", "#E05C7A", "#5BA8F5", "#3DD68C"]


def card_svg_filename(card: Card) -> str:
    suit_key = SVG_SUIT_KEY.get(card.suit, "").lower()
    return f"card_{suit_key}_{card.rank:02d}.svg"


def serialize_card(card: Card) -> Dict[str, Any]:
    return {
        "rank": card.rank,
        "suit": card.suit,
        "name": card.name,
        "short": card.short(),
        "svg": card_svg_filename(card),
    }


def serialize_state(last_step: Optional[StepInfo] = None) -> Dict[str, Any]:
    if game is None:
        return {
            "game": None,
            "last_step": None,
            "players": [],
            "suit_to_player": {},
        }

    data: Dict[str, Any] = {
        "track_len": TRACK_LEN,
        "active_suits": sorted(list(game.active_suits)),
        "positions": game.positions,
        "winner": game.winner,
        "winner_player": suit_to_player.get(game.winner) if game.winner else None,
        "checkpoints": [],
        "players": players,
        "suit_to_player": suit_to_player,
    }

    for idx, card in enumerate(game.checkpoints):
        revealed = game.revealed[idx]
        data["checkpoints"].append(
            {
                "index": idx,
                "revealed": revealed,
                "card": serialize_card(card) if revealed else None,
            }
        )

    if last_step is not None:
        step_payload: Dict[str, Any] = {
            "drawn": serialize_card(last_step.drawn),
            "advanced_suit": last_step.advanced_suit,
            "revealed_checkpoint_index": last_step.revealed_checkpoint_index,
            "revealed_card": serialize_card(last_step.revealed_card)
            if last_step.revealed_card
            else None,
            "penalty_suit": last_step.penalty_suit,
            "winner": last_step.winner,
        }
        if last_step.advanced_suit:
            step_payload["advanced_player"] = suit_to_player.get(last_step.advanced_suit)
        if last_step.penalty_suit:
            step_payload["penalty_player"] = suit_to_player.get(last_step.penalty_suit)
        if last_step.winner:
            step_payload["winner_player"] = suit_to_player.get(last_step.winner)
        data["last_step"] = step_payload
    else:
        data["last_step"] = None

    return data


@app.route("/assets/cards/<path:filename>")
def serve_card_svg(filename: str):
    # Sirve directamente los SVG originales del directorio assets/svg
    svg_dir = os.path.join(os.path.dirname(__file__), "assets", "svg")
    return send_from_directory(svg_dir, filename)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/new-game", methods=["POST"])
def api_new_game():
    """
    Inicia una nueva partida configurando jugadores y caballos,
    imitando la lógica del diálogo de configuración en Tkinter.
    """
    global game, players, suit_to_player

    payload = request.get_json(silent=True) or {}
    n_players = int(payload.get("n_players", 2))
    n_horses = int(payload.get("n_horses", 4))
    raw_players = payload.get("players", [])

    if n_players < 2 or n_players > 4:
        return jsonify({"error": "El número de jugadores debe estar entre 2 y 4."}), 400
    if n_horses not in (3, 4):
        return jsonify({"error": "El número de caballos debe ser 3 o 4."}), 400

    if len(raw_players) < n_players:
        return jsonify({"error": "Faltan datos de jugadores."}), 400

    players = []
    chosen_suits = []
    for idx in range(n_players):
        raw = raw_players[idx] or {}
        name = str(raw.get("name", "")).strip() or f"Jugador {idx + 1}"
        suit = str(raw.get("suit", "")).strip() or SUITS[idx % len(SUITS)]
        if suit in chosen_suits:
            return jsonify({"error": "Dos jugadores no pueden elegir el mismo caballo."}), 400
        if suit not in SUITS:
            return jsonify({"error": f"Palo inválido: {suit}"}), 400
        chosen_suits.append(suit)
        color = PLAYER_COLORS[idx % len(PLAYER_COLORS)]
        players.append({"name": name, "suit": suit, "color": color})

    if n_horses == 3 and n_players > 3:
        return jsonify({"error": "Con 3 caballos puede haber máximo 3 jugadores."}), 400

    if n_horses == 4:
        active_suits = set(SUITS)
    else:
        active_suits = set(chosen_suits)
        for s in SUITS:
            if len(active_suits) >= 3:
                break
            active_suits.add(s)

    game = CarreraEspanola()
    game.reset(active_suits=active_suits)
    suit_to_player = {p["suit"]: p for p in players}

    return jsonify(serialize_state())


@app.route("/api/step", methods=["POST"])
def api_step():
    if game is None:
        return jsonify({"error": "No hay partida activa. Crea una nueva primero."}), 400

    try:
        step_info = game.step()
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(serialize_state(last_step=step_info))


@app.route("/api/state", methods=["GET"])
def api_state():
    return jsonify(serialize_state())


if __name__ == "__main__":
    # Para pruebas locales: py web_app.py
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)


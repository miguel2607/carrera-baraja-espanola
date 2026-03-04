from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from .model import Card, Deck, SUITS

TRACK_LEN = 7
HORSE_RANK = 11  # Caballo

@dataclass
class StepInfo:
    drawn: Card
    advanced_suit: Optional[str]
    revealed_checkpoint_index: Optional[int]
    revealed_card: Optional[Card]
    penalty_suit: Optional[str]
    winner: Optional[str]

class CarreraEspanola:
    """
    Lógica según la descripción del usuario:

    - Caballos = cartas rank 11 (Caballo) de cada palo (solo palos activos).
    - Checkpoints = 7 cartas boca abajo (verticales).
    - Se voltean cartas:
        - si sale un palo activo -> el caballo de ese palo avanza 1
    - Se destapa el checkpoint i cuando TODOS los caballos activos han pasado i
      (posición > i). Al destapar:
        - si la carta destapada es de un palo activo -> ese caballo retrocede 1 (min 0)
    - Gana el primer caballo en llegar a TRACK_LEN.
    """
    def __init__(self) -> None:
        self.reset(active_suits=set(SUITS))

    def reset(self, active_suits: Set[str]) -> None:
        if len(active_suits) not in (3, 4):
            raise ValueError("active_suits debe tener 3 o 4 palos.")

        self.active_suits: Set[str] = set(active_suits)

        self.deck = Deck()

        # Quitamos los caballos del mazo para que no salgan en flips ni checkpoints
        self.deck.cards = [c for c in self.deck.cards if c.rank != HORSE_RANK]

        # Caballos (estado)
        self.horses: Dict[str, Card] = {s: Card(HORSE_RANK, s) for s in self.active_suits}
        self.positions: Dict[str, int] = {s: 0 for s in self.active_suits}

        # Checkpoints: 7 cartas boca abajo (pueden ser de cualquier palo)
        self.checkpoints: List[Card] = [self.deck.draw() for _ in range(TRACK_LEN)]
        self.revealed: List[bool] = [False] * TRACK_LEN

        self.discard: List[Card] = []
        self.winner: Optional[str] = None

    def _next_reveal_index(self) -> Optional[int]:
        for i in range(TRACK_LEN):
            if not self.revealed[i]:
                return i
        return None

    def _all_passed(self, checkpoint_idx: int) -> bool:
        # "pasar" el checkpoint i significa estar estrictamente más allá: pos > i
        for s in self.active_suits:
            if self.positions[s] <= checkpoint_idx:
                return False
        return True

    def step(self) -> StepInfo:
        if self.winner is not None:
            raise RuntimeError("La carrera ya terminó. Inicia una nueva carrera.")

        drawn = self.deck.draw()
        self.discard.append(drawn)

        advanced_suit = None
        if drawn.suit in self.active_suits:
            self.positions[drawn.suit] += 1
            advanced_suit = drawn.suit

        # Chequear si alguien ganó por avance
        for s in self.active_suits:
            if self.positions[s] >= TRACK_LEN:
                self.winner = s
                return StepInfo(drawn, advanced_suit, None, None, None, self.winner)

        # Revelar checkpoints en cadena si corresponde (puede pasar más de uno)
        revealed_checkpoint_index = None
        revealed_card = None
        penalty_suit = None

        while True:
            idx = self._next_reveal_index()
            if idx is None:
                break
            if not self._all_passed(idx):
                break

            # Revelar este checkpoint
            self.revealed[idx] = True
            revealed_checkpoint_index = idx
            revealed_card = self.checkpoints[idx]

            # Penalidad: si el palo es activo, retrocede 1 (mínimo 0)
            if revealed_card.suit in self.active_suits:
                penalty_suit = revealed_card.suit
                self.positions[penalty_suit] = max(0, self.positions[penalty_suit] - 1)

            # ¿alguien ganó después de revelar? (normalmente no por retroceso, pero por consistencia)
            for s in self.active_suits:
                if self.positions[s] >= TRACK_LEN:
                    self.winner = s
                    break

            # seguir intentando revelar más checkpoints si ahora todos pasaron los siguientes
            if self.winner is not None:
                break

        return StepInfo(
            drawn=drawn,
            advanced_suit=advanced_suit,
            revealed_checkpoint_index=revealed_checkpoint_index,
            revealed_card=revealed_card,
            penalty_suit=penalty_suit,
            winner=self.winner
        )

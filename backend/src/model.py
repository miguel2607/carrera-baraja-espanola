from __future__ import annotations
from dataclasses import dataclass
from typing import List
import random

SUITS = ["Oros", "Copas", "Espadas", "Bastos"]

# Baraja española común (40 cartas): 1-7, 10-12
RANKS = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]
RANK_NAMES = {
    1: "As",
    2: "Dos",
    3: "Tres",
    4: "Cuatro",
    5: "Cinco",
    6: "Seis",
    7: "Siete",
    10: "Sota",
    11: "Caballo",
    12: "Rey",
}

# Para UI compacta
RANK_SHORT = {
    1: "1",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    10: "S",
    11: "C",
    12: "R",
}

@dataclass(frozen=True)
class Card:
    rank: int
    suit: str

    @property
    def name(self) -> str:
        return f"{RANK_NAMES[self.rank]} de {self.suit}"

    def short(self) -> str:
        # ej: C-E (Caballo de Espadas), 4-O (Cuatro de Oros)
        return f"{RANK_SHORT[self.rank]}-{self.suit[0]}"

class Deck:
    def __init__(self) -> None:
        self.cards: List[Card] = [Card(r, s) for s in SUITS for r in RANKS]
        self.shuffle()

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def draw(self) -> Card:
        if not self.cards:
            raise RuntimeError("No hay más cartas en el mazo.")
        return self.cards.pop()

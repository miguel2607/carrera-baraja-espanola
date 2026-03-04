import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

const api = axios.create({
    baseURL: API_BASE,
});

export interface Card {
    rank: number;
    suit: string;
    name: string;
    short: string;
    svg: string;
}

export interface Player {
    name: string;
    suit: string;
    color: string;
}

export interface Checkpoint {
    index: number;
    revealed: boolean;
    card: Card | null;
}

export interface StepInfo {
    drawn: Card;
    advanced_suit: string | null;
    advanced_player: Player | null;
    revealed_checkpoint_index: number | null;
    revealed_card: Card | null;
    penalty_suit: string | null;
    penalty_player: Player | null;
    winner: string | null;
    winner_player: Player | null;
}

export interface GameState {
    track_len: number;
    active_suits: string[];
    positions: Record<string, number>;
    winner: string | null;
    winner_player: Player | null;
    checkpoints: Checkpoint[];
    players: Player[];
    suit_to_player: Record<string, Player>;
    last_step: StepInfo | null;
}

export const getGameState = async (): Promise<GameState> => {
    const res = await api.get('/state');
    return res.data;
};

export const startNewGame = async (config: { n_players: number; n_horses: number; players: { name: string; suit: string }[] }): Promise<GameState> => {
    const res = await api.post('/new-game', config);
    return res.data;
};

export const stepGame = async (): Promise<GameState> => {
    const res = await api.post('/step');
    return res.data;
};

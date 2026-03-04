import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Trophy, Play, RotateCcw, Info, Settings, User, Sword, Shield, Crown, Sparkles } from 'lucide-react';
import { getGameState, startNewGame, stepGame } from './api';
import type { GameState, Player, Card as CardData } from './api';
import confetti from 'canvas-confetti';

const SUIT_ICONS: Record<string, string> = {
  Oros: "◈",
  Copas: "♥",
  Espadas: "⚔",
  Bastos: "⌘",
};

const Card = ({ card, revealed = true, className = "" }: { card: CardData | null, revealed?: boolean, className?: string }) => {
  return (
    <motion.div
      layout
      initial={{ rotateY: 180, opacity: 0 }}
      animate={{ rotateY: revealed ? 0 : 180, opacity: 1 }}
      transition={{ type: "spring", stiffness: 260, damping: 20 }}
      className={`relative w-24 h-36 rounded-xl overflow-hidden shadow-2xl border ${className} ${revealed ? 'border-primary/30' : 'border-white/10'}`}
    >
      <div className="absolute inset-0 bg-slate-800 flex items-center justify-center">
        {revealed && card ? (
          <img src={`/assets/cards/${card.svg}`} alt={card.name} className="w-full h-full object-cover" />
        ) : (
          <img src="/assets/cards/card_back.svg" alt="Card Back" className="w-full h-full object-cover opacity-60" />
        )}
      </div>
    </motion.div>
  );
};

const HorseToken = ({ suit, color, pos, trackLen }: { suit: string, color: string, pos: number, trackLen: number }) => {
  const progress = (pos / trackLen) * 100;
  return (
    <motion.div
      animate={{ left: `${progress}%` }}
      transition={{ type: "spring", stiffness: 100, damping: 15 }}
      className="absolute top-1/2 -translate-y-1/2 -ml-6 z-10"
    >
      <div
        className="w-12 h-16 rounded-lg border-2 shadow-lg flex flex-col items-center justify-center bg-slate-900 overflow-hidden"
        style={{ borderColor: color }}
      >
        <img
          src={`/assets/cards/card_${suit.toLowerCase() === 'oros' ? 'coins' : suit.toLowerCase() === 'copas' ? 'cups' : suit.toLowerCase() === 'espadas' ? 'swords' : 'clubs'}_11.svg`}
          alt={suit}
          className="w-full h-full object-cover opacity-90"
        />
        <div className="absolute bottom-0 inset-x-0 bg-black/60 text-[10px] text-center font-bold py-0.5">
          {SUIT_ICONS[suit]}
        </div>
      </div>
    </motion.div>
  );
};

export default function App() {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [loading, setLoading] = useState(false);
  const [showConfig, setShowConfig] = useState(true);
  const [config, setConfig] = useState({
    n_players: 2,
    n_horses: 4,
    players: [
      { name: 'Jugador 1', suit: 'Oros' },
      { name: 'Jugador 2', suit: 'Copas' },
      { name: 'Jugador 3', suit: 'Espadas' },
      { name: 'Jugador 4', suit: 'Bastos' },
    ]
  });

  useEffect(() => {
    fetchState();
  }, []);

  const fetchState = async () => {
    try {
      const state = await getGameState();
      setGameState(state);
      if (state.active_suits?.length > 0) setShowConfig(false);
    } catch (e) {
      console.error(e);
    }
  };

  const handleNewGame = async () => {
    setLoading(true);
    try {
      const state = await startNewGame({
        ...config,
        players: config.players.slice(0, config.n_players)
      });
      setGameState(state);
      setShowConfig(false);
    } catch (e: any) {
      alert(e.response?.data?.error || "Error al iniciar partida");
    } finally {
      setLoading(false);
    }
  };

  const handleStep = async () => {
    if (loading || gameState?.winner) return;
    setLoading(true);
    try {
      const state = await stepGame();
      setGameState(state);
      if (state.winner) {
        confetti({
          particleCount: 150,
          spread: 70,
          origin: { y: 0.6 },
          colors: [state.winner_player?.color || '#ffd700', '#ffffff']
        });
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  if (showConfig || !gameState) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6 bg-[radial-gradient(circle_at_top,_#1e293b_0%,_#020617_100%)]">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-2xl glass p-8 rounded-3xl shadow-2xl relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
            <Trophy size={120} className="text-primary" />
          </div>

          <h1 className="text-4xl font-display font-bold text-gradient mb-2 tracking-tight">CARRERA DE CABALLOS</h1>
          <p className="text-slate-400 mb-8 font-medium">Baraja Española · Premium Edition</p>

          <div className="space-y-8">
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-3">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                  <User size={14} /> Jugadores
                </label>
                <div className="flex gap-2">
                  {[2, 3, 4].map(n => (
                    <button
                      key={n}
                      onClick={() => setConfig({ ...config, n_players: n })}
                      className={`flex-1 py-3 rounded-xl font-bold transition-all ${config.n_players === n ? 'bg-primary text-background' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
                    >
                      {n}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-3">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                  <Sword size={14} /> Caballos
                </label>
                <div className="flex gap-2">
                  {[3, 4].map(n => (
                    <button
                      key={n}
                      onClick={() => setConfig({ ...config, n_horses: n })}
                      className={`flex-1 py-3 rounded-xl font-bold transition-all ${config.n_horses === n ? 'bg-primary text-background' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
                    >
                      {n}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                <Settings size={14} /> Configuración de Jugadores
              </label>
              <div className="grid grid-cols-1 gap-3">
                {Array.from({ length: config.n_players }).map((_, i) => (
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    key={i}
                    className="flex gap-3 items-center bg-slate-800/50 p-3 rounded-2xl border border-white/5"
                  >
                    <div className="w-10 h-10 rounded-xl bg-slate-700 flex items-center justify-center font-bold text-primary">
                      {i + 1}
                    </div>
                    <input
                      type="text"
                      placeholder={`Jugador ${i + 1}`}
                      className="flex-1 bg-transparent border-none focus:ring-0 text-slate-100 placeholder:text-slate-600 font-medium"
                      value={config.players[i].name}
                      onChange={(e) => {
                        const newPlayers = [...config.players];
                        newPlayers[i].name = e.target.value;
                        setConfig({ ...config, players: newPlayers });
                      }}
                    />
                    <select
                      className="bg-slate-900 border-none rounded-lg text-sm font-bold text-primary focus:ring-0"
                      value={config.players[i].suit}
                      onChange={(e) => {
                        const newPlayers = [...config.players];
                        newPlayers[i].suit = e.target.value;
                        setConfig({ ...config, players: newPlayers });
                      }}
                    >
                      {['Oros', 'Copas', 'Espadas', 'Bastos'].map(s => (
                        <option key={s} value={s}>{SUIT_ICONS[s]} {s}</option>
                      ))}
                    </select>
                  </motion.div>
                ))}
              </div>
            </div>

            <button
              onClick={handleNewGame}
              disabled={loading}
              className="w-full py-5 bg-gradient-to-r from-primary to-amber-500 text-background font-black rounded-2xl shadow-[0_10px_40px_rgba(212,168,67,0.3)] hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-3 text-lg"
            >
              <Play fill="currentColor" /> INICIAR CARRERA
            </button>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 flex flex-col gap-8">
      {/* Header */}
      <header className="flex justify-between items-center glass p-6 rounded-3xl premium-border">
        <div>
          <h1 className="text-2xl font-display font-black text-gradient leading-none mb-1">CARRERA DE CABALLOS</h1>
          <div className="flex gap-4 items-center">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em] flex items-center gap-1.5">
              <Sparkles size={12} className="text-primary" /> Partida en curso
            </span>
          </div>
        </div>
        <div className="flex gap-4">
          <button
            onClick={() => setShowConfig(true)}
            className="p-4 rounded-2xl bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition-all flex items-center gap-2 font-bold"
          >
            <RotateCcw size={20} /> <span className="text-sm">Reiniciar</span>
          </button>
          <button
            onClick={handleStep}
            disabled={loading || !!gameState.winner}
            className={`px-8 rounded-2xl font-black transition-all flex items-center gap-3 shadow-lg ${gameState.winner ? 'bg-slate-800 text-slate-600 grayscale' : 'bg-gradient-to-br from-success to-emerald-600 text-background hover:scale-105 active:scale-95 shadow-emerald-500/20'}`}
          >
            <Play fill="currentColor" /> VOLTEAR CARTA
          </button>
        </div>
      </header>

      <main className="grid grid-cols-1 lg:grid-cols-12 gap-8 flex-1">
        {/* Board Section */}
        <div className="lg:col-span-8 flex flex-col gap-8">
          {/* Checkpoints */}
          <section className="glass p-6 rounded-3xl premium-border overflow-hidden relative">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xs font-black text-slate-500 uppercase tracking-widest flex items-center gap-2">
                <Shield size={14} className="text-secondary" /> Puntos de Control
              </h2>
            </div>
            <div className="flex justify-between gap-4">
              {gameState.checkpoints.map((cp, i) => (
                <div key={i} className="flex flex-col items-center gap-3">
                  <Card
                    card={cp.card}
                    revealed={cp.revealed}
                    className={cp.revealed ? "ring-2 ring-primary/50 shadow-primary/20" : "opacity-80"}
                  />
                  <span className={`text-[10px] font-black ${cp.revealed ? 'text-primary' : 'text-slate-600'}`}>#{i + 1}</span>
                </div>
              ))}
            </div>
          </section>

          {/* Lanes */}
          <section className="glass p-8 rounded-3xl premium-border flex-1 relative overflow-hidden">
            <div className="absolute top-0 right-0 p-8 opacity-5">
              <Sparkles size={300} strokeWidth={1} />
            </div>

            <div className="flex justify-between items-center mb-10">
              <h2 className="text-xs font-black text-slate-500 uppercase tracking-widest flex items-center gap-2">
                <Trophy size={14} className="text-primary" /> La Pista
              </h2>
            </div>

            <div className="space-y-12 relative">
              {/* Finish Line */}
              <div className="absolute right-0 top-0 bottom-0 w-2 bg-gradient-to-b from-primary/50 via-primary to-primary/50 rounded-full shadow-[0_0_20px_rgba(212,168,67,0.4)]" />

              {gameState.active_suits.map((suit) => {
                const player = gameState.suit_to_player[suit];
                return (
                  <div key={suit} className="relative h-20 flex items-center">
                    {/* Lane Info */}
                    <div className="absolute -top-6 left-0 flex items-center gap-2">
                      <span className="text-lg" style={{ color: player?.color || 'inherit' }}>{SUIT_ICONS[suit]}</span>
                      <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">
                        {suit} {player ? `— ${player.name}` : ''}
                      </span>
                    </div>
                    {/* Lane Bar */}
                    <div className="absolute inset-x-0 h-1 bg-white/5 rounded-full overflow-hidden">
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent to-white/10" />
                    </div>
                    {/* Marks */}
                    <div className="absolute inset-x-0 flex justify-between px-0">
                      {Array.from({ length: gameState.track_len + 1 }).map((_, i) => (
                        <div key={i} className={`w-0.5 h-3 bg-white/10 ${i === gameState.track_len ? 'hidden' : ''}`} />
                      ))}
                    </div>
                    {/* Horse */}
                    <HorseToken
                      suit={suit}
                      color={player?.color || '#ffd700'}
                      pos={gameState.positions[suit]}
                      trackLen={gameState.track_len}
                    />
                  </div>
                );
              })}
            </div>
          </section>
        </div>

        {/* Sidebar */}
        <aside className="lg:col-span-4 flex flex-col gap-8">
          {/* Last Card Played */}
          <section className="glass p-8 rounded-3xl premium-border relative overflow-hidden min-h-[400px] flex flex-col items-center justify-center bg-gradient-to-br from-slate-900 to-slate-950">
            <div className="absolute top-0 right-0 p-4">
              <Info size={20} className="text-slate-700 hover:text-primary transition-colors cursor-help" />
            </div>
            <h2 className="absolute top-8 left-8 text-xs font-black text-slate-500 uppercase tracking-widest">Turno Actual</h2>

            <AnimatePresence mode="wait">
              {gameState.last_step ? (
                <motion.div
                  key={gameState.last_step.drawn.short}
                  initial={{ scale: 0.8, y: 20, opacity: 0 }}
                  animate={{ scale: 1, y: 0, opacity: 1 }}
                  className="flex flex-col items-center gap-6"
                >
                  <Card card={gameState.last_step.drawn} className="w-48 h-72 rounded-2xl ring-4 ring-primary/20" />
                  <div className="text-center">
                    <p className="text-2xl font-display font-black text-primary">{gameState.last_step.drawn.name}</p>
                    {gameState.last_step.advanced_suit ? (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="text-success font-bold flex items-center justify-center gap-2 mt-2"
                      >
                        <Sparkles size={16} /> ¡Avanza {gameState.last_step.advanced_suit}!
                      </motion.div>
                    ) : (
                      <p className="text-slate-500 text-sm font-medium mt-1">Palo inactivo</p>
                    )}
                  </div>
                </motion.div>
              ) : (
                <div className="flex flex-col items-center gap-4 text-slate-600">
                  <Card card={null} revealed={false} className="w-48 h-72 opacity-40" />
                  <p className="font-bold text-sm tracking-widest">INICIA LA CARRERA</p>
                </div>
              )}
            </AnimatePresence>

            {gameState.winner && (
              <motion.div
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                className="absolute inset-0 z-20 bg-slate-950/90 backdrop-blur-xl flex flex-col items-center justify-center p-8 text-center"
              >
                <motion.div
                  animate={{ scale: [1, 1.1, 1] }}
                  transition={{ repeat: Infinity, duration: 2 }}
                  className="w-24 h-24 rounded-full bg-primary/20 flex items-center justify-center text-primary mb-6"
                >
                  <Crown size={60} />
                </motion.div>
                <h3 className="text-4xl font-display font-black text-gradient mb-2 uppercase tracking-tighter">¡VICTORIA!</h3>
                <p className="text-xl font-bold text-slate-100 mb-8">
                  {gameState.winner_player?.name || gameState.winner} ha ganado la carrera
                </p>
                <button
                  onClick={() => setShowConfig(true)}
                  className="px-10 py-4 bg-primary text-background font-black rounded-2xl hover:scale-105 transition-all text-sm uppercase tracking-widest"
                >
                  Otra Partida
                </button>
              </motion.div>
            )}
          </section>

          {/* History / Log */}
          <section className="glass p-6 rounded-3xl premium-border flex-1 flex flex-col overflow-hidden max-h-[350px]">
            <h2 className="text-xs font-black text-slate-500 uppercase tracking-widest mb-4">Registro de Eventos</h2>
            <div className="space-y-3 overflow-y-auto pr-2 scrollbar-premium flex-1">
              {gameState.last_step && (
                <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-2xl">
                  <p className="text-xs text-blue-300 font-bold flex items-center gap-2 leading-none">
                    <Info size={12} /> {gameState.last_step.revealed_checkpoint_index !== null ? `Checkpoint #${gameState.last_step.revealed_checkpoint_index + 1} revelado` : 'Último movimiento'}
                  </p>
                  {gameState.last_step.penalty_suit && (
                    <p className="text-sm text-danger font-bold mt-2">
                      ⚠ Penalidad: {gameState.last_step.penalty_suit} retrocede
                    </p>
                  )}
                </div>
              )}
              <div className="text-slate-500 text-[10px] font-bold tracking-widest mt-4 uppercase">Instrucciones</div>
              <p className="text-xs text-slate-400 font-medium leading-relaxed">
                Cada carta del mazo hace avanzar al caballo de su palo. Los checkpoints se revelan cuando todos los caballos los superan. ¡Si el checkpoint coincide con un caballo activo, éste retrocede!
              </p>
            </div>
          </section>
        </aside>
      </main>
    </div>
  );
}

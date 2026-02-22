import streamlit as st
import random
from Juego import NimNode, Tree

OPERATORS = [1, 2, 3]
INIT_STATE = 25

LEVELS = {
    "🟢 Fácil":   {"depth": 1, "bonus_base": 10, "bonus_factor": 1},
    "🟡 Medio":   {"depth": 3, "bonus_base": 30, "bonus_factor": 3},
    "🔴 Difícil": {"depth": 8, "bonus_base": 50, "bonus_factor": 5},
}

st.set_page_config(page_title="Juego NIM", page_icon="🪵")
st.title("🪵 Juego NIM")
st.markdown("**Reglas:** Los jugadores toman turnos sacando 1, 2 o 3 fichas. El que tome la última gana.")

# ── Session State ──────────────────────────────────────────────────────────────
if "tokens" not in st.session_state:
    st.session_state.tokens = INIT_STATE
if "turn" not in st.session_state:
    st.session_state.turn = "human"
if "log" not in st.session_state:
    st.session_state.log = []
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "winner" not in st.session_state:
    st.session_state.winner = None
if "game_started" not in st.session_state:
    st.session_state.game_started = False
if "config" not in st.session_state:
    st.session_state.config = None
if "algorithm" not in st.session_state:
    st.session_state.algorithm = None
if "spin_result" not in st.session_state:
    st.session_state.spin_result = None
if "first_player" not in st.session_state:
    st.session_state.first_player = None
# Contadores
if "wins_human" not in st.session_state:
    st.session_state.wins_human = 0
if "wins_machine" not in st.session_state:
    st.session_state.wins_machine = 0
if "game_count" not in st.session_state:
    st.session_state.game_count = 0

# ── Helpers ────────────────────────────────────────────────────────────────────
def spin_wheel():
    result = random.choice(["human", "machine"])
    st.session_state.spin_result = result
    st.session_state.first_player = result

def start_game(nivel, algoritmo):
    st.session_state.config = LEVELS[nivel]
    st.session_state.algorithm = algoritmo
    st.session_state.tokens = INIT_STATE
    st.session_state.turn = st.session_state.first_player
    st.session_state.log = []
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.game_started = True
    st.session_state.game_count += 1

def rematch():
    """Alterna quién empieza respecto a la partida anterior y reinicia."""
    prev = st.session_state.first_player
    next_first = "machine" if prev == "human" else "human"
    st.session_state.first_player = next_first
    st.session_state.spin_result = next_first
    st.session_state.tokens = INIT_STATE
    st.session_state.turn = next_first
    st.session_state.log = []
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.game_started = True
    st.session_state.game_count += 1

def reset_game():
    """Vuelve a la pantalla de configuración y resetea todo."""
    st.session_state.game_started = False
    st.session_state.config = None
    st.session_state.algorithm = None
    st.session_state.tokens = INIT_STATE
    st.session_state.turn = "human"
    st.session_state.log = []
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.spin_result = None
    st.session_state.first_player = None
    st.session_state.wins_human = 0
    st.session_state.wins_machine = 0
    st.session_state.game_count = 0

def machine_move(tokens):
    if tokens <= max(OPERATORS):
        return tokens
    config = st.session_state.config
    node = NimNode(True, value="inicio", state=tokens, operators=OPERATORS)
    tree = Tree(node, OPERATORS)
    if st.session_state.algorithm == "MiniMax":
        best = tree.miniMax(config["depth"], config["bonus_base"], config["bonus_factor"])
    else:
        best = tree.miniMaxAlphaBeta(config["depth"], config["bonus_base"], config["bonus_factor"])
    return tokens - best.state

def apply_move(taken):
    st.session_state.tokens -= taken
    st.session_state.log.append((st.session_state.turn, taken, st.session_state.tokens))
    if st.session_state.tokens == 0:
        st.session_state.game_over = True
        st.session_state.winner = st.session_state.turn
        # Actualizar contador
        if st.session_state.turn == "human":
            st.session_state.wins_human += 1
        else:
            st.session_state.wins_machine += 1
    else:
        st.session_state.turn = "machine" if st.session_state.turn == "human" else "human"

# ── Pantalla de configuración ──────────────────────────────────────────────────
if not st.session_state.game_started:
    st.subheader("⚙️ Configuración de la partida")

    nivel = st.radio("Selecciona la dificultad:", list(LEVELS.keys()), horizontal=True)
    cfg = LEVELS[nivel]
    st.caption(f"Profundidad: `{cfg['depth']}` · Bonus Base: `{cfg['bonus_base']}` · Bonus Factor: `{cfg['bonus_factor']}`")

    st.divider()

    algoritmo = st.radio("Selecciona el algoritmo:", ["MiniMax", "MiniMax Alpha-Beta"], horizontal=True)

    st.divider()

    st.subheader("🎰 ¿Quién empieza?")
    col_spin, col_result = st.columns([1, 2])

    with col_spin:
        st.button("🎰 ¡Girar ruleta!", on_click=spin_wheel)

    with col_result:
        if st.session_state.spin_result is None:
            st.info("Gira la ruleta para decidir quién empieza.")
        elif st.session_state.spin_result == "human":
            st.success("👤 ¡Empiezas tú!")
        else:
            st.error("🤖 ¡Empieza la máquina!")

    st.divider()

    if st.session_state.first_player is not None:
        st.button("🚀 ¡Comenzar partida!", on_click=start_game, args=(nivel, algoritmo))
    else:
        st.button("🚀 ¡Comenzar partida!", disabled=True)

# ── Juego ──────────────────────────────────────────────────────────────────────
else:
    # Sidebar con info y marcador
    st.sidebar.header("📌 Partida actual")
    st.sidebar.markdown(f"""
    **Dificultad:** {[k for k,v in LEVELS.items() if v == st.session_state.config][0]}  
    **Algoritmo:** `{st.session_state.algorithm}`  
    **Profundidad:** `{st.session_state.config['depth']}`  
    **Empieza:** {"👤 Humano" if st.session_state.first_player == "human" else "🤖 Máquina"}
    """)

    st.sidebar.divider()
    st.sidebar.header("🏆 Marcador")
    st.sidebar.markdown(f"""
    **Partidas jugadas:** `{st.session_state.game_count}`  
    👤 Humano: `{st.session_state.wins_human}`  
    🤖 Máquina: `{st.session_state.wins_machine}`  
    """)

    st.sidebar.divider()
    st.sidebar.button("🔄 Nueva configuración", on_click=reset_game)

    # Turno de la máquina
    if st.session_state.turn == "machine" and not st.session_state.game_over:
        taken = machine_move(st.session_state.tokens)
        apply_move(taken)
        st.rerun()

    # UI Principal
    tokens = st.session_state.tokens
    st.subheader(f"Fichas restantes: {tokens}")
    if tokens > 0:
        cols = st.columns(min(tokens, 25))
        for i in range(tokens):
            cols[i % 25].markdown("🪵")
    else:
        st.markdown("¡No quedan fichas!")

    st.divider()

    if st.session_state.game_over:
        if st.session_state.winner == "human":
            st.success("🙅🏽‍♂️ ¡Ganó el humano! 🎉")
        else:
            st.error("🤖 ¡Ganó la máquina! 🎉")

        next_first = "machine" if st.session_state.first_player == "human" else "human"
        st.info(f"En la siguiente partida empieza: {'🤖 Máquina' if next_first == 'machine' else '👤 Humano'}")

        col_rematch, col_reset = st.columns(2)
        with col_rematch:
            st.button("🔁 Revancha", on_click=rematch)
        with col_reset:
            st.button("🏠 Cambiar configuración", on_click=reset_game)

    else:
        if st.session_state.turn == "human":
            st.subheader("Tu turno — ¿Cuántas fichas tomas?")
            col1, col2, col3 = st.columns(3)
            for col, n in zip([col1, col2, col3], OPERATORS):
                if n <= tokens:
                    col.button(f"Tomar {n}", key=f"take_{n}", on_click=apply_move, args=(n,))
        else:
            st.subheader("⏳ Turno de la máquina...")

    # Historial
    if st.session_state.log:
        st.divider()
        st.subheader("📋 Historial")
        for who, taken, remaining in reversed(st.session_state.log):
            icon = "👤" if who == "human" else "🤖"
            st.write(f"{icon} tomó **{taken}** → quedan **{remaining}** fichas")
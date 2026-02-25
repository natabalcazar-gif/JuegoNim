
import streamlit as st
import random
from Juego import NimNode, NimNodeMisere, Tree

OPERATORS = [1, 2, 3]
DEFAULT_INIT_STATE = 25

LEVELS = {
    "🟢 Fácil":   {"depth": 1, "bonus_base": 10, "bonus_factor": 1},
    "🟡 Medio":   {"depth": 3, "bonus_base": 30, "bonus_factor": 3},
    "🔴 Difícil": {"depth": 8, "bonus_base": 50, "bonus_factor": 5},
}

VARIANTS = {
    "🏆 Clásico": {
        "label": "Clásico",
        "description": "El que tome la **última** ficha **gana**.",
        "node_class": NimNode,
    },
    "💀 Misère": {
        "label": "Misère",
        "description": "El que tome la **última** ficha **pierde**.",
        "node_class": NimNodeMisere,
    },
}

st.set_page_config(page_title="Juego NIM", page_icon="🪵")
st.title("🪵 Juego NIM")

# ── Session State ──────────────────────────────────────────────────────────────
defaults = {
    "tokens": DEFAULT_INIT_STATE,
    "init_state": DEFAULT_INIT_STATE,
    "turn": "human",
    "log": [],
    "game_over": False,
    "winner": None,
    "game_started": False,
    "config": None,
    "algorithm": None,
    "variant": None,
    "spin_result": None,
    "first_player": None,
    "wins_human_clasico": 0,
    "wins_machine_clasico": 0,
    "game_count_clasico": 0,
    "wins_human_misere": 0,
    "wins_machine_misere": 0,
    "game_count_misere": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ────────────────────────────────────────────────────────────────────
def variant_key():
    return "misere" if st.session_state.variant == "💀 Misère" else "clasico"

def spin_wheel():
    result = random.choice(["human", "machine"])
    st.session_state.spin_result = result
    st.session_state.first_player = result

def start_game(nivel, algoritmo, variante, init_tokens):
    st.session_state.config = LEVELS[nivel]
    st.session_state.algorithm = algoritmo
    st.session_state.variant = variante
    st.session_state.init_state = init_tokens
    st.session_state.tokens = init_tokens
    st.session_state.turn = st.session_state.first_player
    st.session_state.log = []
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.game_started = True
    key = variant_key()
    st.session_state[f"game_count_{key}"] += 1

def rematch():
    prev = st.session_state.first_player
    next_first = "machine" if prev == "human" else "human"
    st.session_state.first_player = next_first
    st.session_state.spin_result = next_first
    st.session_state.tokens = st.session_state.init_state
    st.session_state.turn = next_first
    st.session_state.log = []
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.game_started = True
    key = variant_key()
    st.session_state[f"game_count_{key}"] += 1

def reset_game():
    for k in ["game_started", "config", "algorithm", "variant", "spin_result", "first_player",
              "game_over", "winner"]:
        st.session_state[k] = defaults[k]
    st.session_state.tokens = st.session_state.init_state
    st.session_state.turn = "human"
    st.session_state.log = []

def machine_move(tokens):
    if tokens <= max(OPERATORS):
        if st.session_state.variant == "💀 Misère":
            return max(1, tokens - 1)
        return tokens

    config = st.session_state.config
    NodeClass = VARIANTS[st.session_state.variant]["node_class"]
    node = NodeClass(True, value="inicio", state=tokens, operators=OPERATORS)
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
        key = variant_key()
        if st.session_state.variant == "💀 Misère":
            loser = st.session_state.turn
            winner = "machine" if loser == "human" else "human"
        else:
            winner = st.session_state.turn
        st.session_state.winner = winner
        st.session_state[f"wins_{winner}_{key}"] += 1
    else:
        st.session_state.turn = "machine" if st.session_state.turn == "human" else "human"

# ── Pantalla de configuración ──────────────────────────────────────────────────
if not st.session_state.game_started:
    st.subheader("⚙️ Configuración de la partida")

    # Variante
    variante = st.radio("Selecciona la variante:", list(VARIANTS.keys()), horizontal=True)
    st.caption(VARIANTS[variante]["description"])

    st.divider()

    # Fichas iniciales
    init_tokens = st.slider(
        "Fichas iniciales:",
        min_value=20,
        max_value=50,
        value=DEFAULT_INIT_STATE,
        step=1,
        help="Número de fichas con las que empieza la partida."
    )
    mod = init_tokens % (max(OPERATORS) + 1)
    if mod == 0:
        st.caption(f"⚠️ {init_tokens} es múltiplo de 4 — quien empieza está en **posición perdedora** en Clásico.")
    else:
        st.caption(f"✅ {init_tokens} no es múltiplo de 4 — quien empieza tiene **ventaja** en Clásico.")

    st.divider()

    # Dificultad
    nivel = st.radio("Selecciona la dificultad:", list(LEVELS.keys()), horizontal=True)
    cfg = LEVELS[nivel]
    st.caption(f"Profundidad: `{cfg['depth']}` · Bonus Base: `{cfg['bonus_base']}` · Bonus Factor: `{cfg['bonus_factor']}`")

    st.divider()

    # Algoritmo
    algoritmo = st.radio("Selecciona el algoritmo:", ["MiniMax", "MiniMax Alpha-Beta"], horizontal=True)

    st.divider()

    # Ruleta
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
        st.button("🚀 ¡Comenzar partida!", on_click=start_game, args=(nivel, algoritmo, variante, init_tokens))
    else:
        st.button("🚀 ¡Comenzar partida!", disabled=True)

# ── Juego ──────────────────────────────────────────────────────────────────────
else:
    vkey = variant_key()
    variant_info = VARIANTS[st.session_state.variant]

    # Sidebar
    st.sidebar.header("📌 Partida actual")
    st.sidebar.markdown(f"""
**Variante:** {st.session_state.variant}
**Fichas iniciales:** `{st.session_state.init_state}`
**Dificultad:** {[k for k,v in LEVELS.items() if v == st.session_state.config][0]}
**Algoritmo:** `{st.session_state.algorithm}`
**Profundidad:** `{st.session_state.config['depth']}`
**Empieza:** {"👤 Humano" if st.session_state.first_player == "human" else "🤖 Máquina"}
    """)

    st.sidebar.divider()
    st.sidebar.header("🏆 Marcador")
    for v_key, v_label in [("clasico", "🏆 Clásico"), ("misere", "💀 Misère")]:
        st.sidebar.markdown(f"**{v_label}** — Partidas: `{st.session_state[f'game_count_{v_key}']}`")
        c1, c2 = st.sidebar.columns(2)
        c1.metric("👤 Humano", st.session_state[f"wins_human_{v_key}"])
        c2.metric("🤖 Máquina", st.session_state[f"wins_machine_{v_key}"])

    st.sidebar.divider()
    st.sidebar.button("🔄 Nueva configuración", on_click=reset_game)

    # Regla activa
    st.info(f"{st.session_state.variant} — {variant_info['description']}")

    # Turno de la máquina
    if st.session_state.turn == "machine" and not st.session_state.game_over:
        taken = machine_move(st.session_state.tokens)
        apply_move(taken)
        st.rerun()

    # Tablero
    tokens = st.session_state.tokens
    st.subheader(f"Fichas restantes: {tokens} / {st.session_state.init_state}")
    if tokens > 0:
        cols = st.columns(min(tokens, 25))
        for i in range(tokens):
            cols[i % 25].markdown("🪵")
    else:
        st.markdown("¡No quedan fichas!")

    st.divider()

    # Resultado o botones
    if st.session_state.game_over:
        if st.session_state.winner == "human":
            st.success("👤 ¡Ganó el humano! 🎉")
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

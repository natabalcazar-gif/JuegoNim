import streamlit as st
from Juego import NimNode, Tree  # importa tus clases

# ── Configuración inicial ──────────────────────────────────────────────────────
OPERATORS = [1, 2, 3]
INIT_STATE = 25
DEPTH = 6

st.set_page_config(page_title="Juego NIM", page_icon="🪵")
st.title("🪵 Juego NIM")
st.markdown("**Reglas:** Los jugadores toman turnos sacando 1, 2 o 3 fichas. El que tome la última gana.")

# ── Session State ──────────────────────────────────────────────────────────────
if "tokens" not in st.session_state:
    st.session_state.tokens = INIT_STATE
if "turn" not in st.session_state:
    st.session_state.turn = "human"  # "human" o "machine"
if "log" not in st.session_state:
    st.session_state.log = []
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "winner" not in st.session_state:
    st.session_state.winner = None



# ── Helpers ────────────────────────────────────────────────────────────────────
def reset_game():
    st.session_state.tokens = INIT_STATE
    st.session_state.turn = "machine" #Comienza la maquina 
    st.session_state.log = []
    st.session_state.game_over = False
    st.session_state.winner = None

def machine_move(tokens):
    # Si puede tomar todo de una vez, lo hace
    if tokens <= max(OPERATORS):
        return tokens
    
    """Devuelve cuántas fichas saca la máquina usando miniMax."""
    node = NimNode(True, value="inicio", state=tokens, operators=OPERATORS)
    tree = Tree(node, OPERATORS)
    best = tree.miniMax(DEPTH)
    taken = tokens - best.state


    
    return taken

def apply_move(taken):
    st.session_state.tokens -= taken
    st.session_state.log.append((st.session_state.turn, taken, st.session_state.tokens))

    # Verificar si ganó quien acaba de mover
    if st.session_state.tokens == 0:
        st.session_state.game_over = True
        st.session_state.winner = st.session_state.turn
    else:
        # Cambiar turno
        st.session_state.turn = "machine" if st.session_state.turn == "human" else "human"

# ── Turno de la máquina (se ejecuta automáticamente si es su turno) ─────────────
if st.session_state.turn == "machine" and not st.session_state.game_over:
    taken = machine_move(st.session_state.tokens)
    apply_move(taken)
    st.rerun()

# ── UI Principal ───────────────────────────────────────────────────────────────
tokens = st.session_state.tokens

# Mostrar fichas visualmente
st.subheader(f"Fichas restantes: {tokens}")
if tokens > 0:
    cols = st.columns(min(tokens, 25))
    for i in range(tokens):
        cols[i % 25].markdown("🪵")
else:
    st.markdown("¡No quedan fichas!")


st.divider()

# Estado del juego
if st.session_state.game_over:
    if st.session_state.winner == "human":
        st.success(" 🙅🏽‍♂️ Ganó el humano 🎉")
    else:
        
        st.error("🤖 Gano la máquina 🎉")

    st.button("🔄 Jugar de nuevo", on_click=reset_game)

else:
    st.subheader("Tu turno — ¿Cuántas fichas tomas?")
    col1, col2, col3 = st.columns(3)
    for col, n in zip([col1, col2, col3], OPERATORS):
        if n <= tokens:
            col.button(f"Tomar {n}", key=f"take_{n}", on_click=apply_move, args=(n,))




# ── Historial ──────────────────────────────────────────────────────────────────
if st.session_state.log:
    st.divider()
    st.subheader("📋 Historial")
    for who, taken, remaining in reversed(st.session_state.log):
        icon = "👤" if who == "human" else "🤖"
        st.write(f"{icon} tomó **{taken}** → quedan **{remaining}** fichas")



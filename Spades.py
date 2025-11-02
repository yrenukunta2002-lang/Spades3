import streamlit as st
import json
import time
from pathlib import Path

state_file = Path("spades_state.json")

def save_state():
    state = {
        "players": st.session_state.players,
        "scores": st.session_state.scores,
        "bags": st.session_state.bags,
        "round": st.session_state.round,
        "show_scoreboard": st.session_state.show_scoreboard
    }
    state_file.write_text(json.dumps(state))

def load_state():
    if state_file.exists():
        state = json.loads(state_file.read_text())
        st.session_state.players = state.get("players", [])
        st.session_state.scores = state.get("scores", {})
        st.session_state.bags = state.get("bags", {})
        st.session_state.round = state.get("round", 1)
        st.session_state.show_scoreboard = state.get("show_scoreboard", False)
    else:
        st.session_state.players = []
        st.session_state.scores = {}
        st.session_state.bags = {}
        st.session_state.round = 1
        st.session_state.show_scoreboard = False

st.set_page_config(page_title="Spades Scorekeeper", layout="centered")

page_bg = """
<style>
[data-testid="stAppViewContainer"]{
background: linear-gradient(180deg, #0b0c10, #1f2833);
color: white;
}
[data-testid="stSidebar"]{
background: #1f2833;
}
.stButton>button {
background-color: #45a29e;
color: white;
border-radius: 10px;
}
.stNumberInput>div>input {
background-color: #0b0c10;
color: white;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

if "players" not in st.session_state:
    load_state()

st.sidebar.title("Menu")

if st.sidebar.button("📊 Scores"):
    st.session_state.show_scoreboard = not st.session_state.get("show_scoreboard", False)
    save_state()

if st.sidebar.button("🔄 Restart Game"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    if state_file.exists():
        state_file.unlink()
    st.success("Game restarted!")
    st.rerun()

if not st.session_state.players:
    st.title("Spades Scorekeeper")
    num_players = st.number_input("Enter number of players", 2, 10, 4)
    if st.button("Continue"):
        st.session_state.num_players = num_players
        st.session_state.player_names_entered = False
        st.rerun()

if "num_players" in st.session_state and not st.session_state.get("player_names_entered", False):
    st.title("Enter Player Names")
    players = []
    for i in range(st.session_state.num_players):
        name = st.text_input(f"Player {i+1} name", key=f"name_{i}")
        if name:
            players.append(name)
    if st.button("Start Game") and len(players) == st.session_state.num_players:
        st.session_state.players = players
        st.session_state.scores = {p: 0 for p in players}
        st.session_state.bags = {p: 0 for p in players}
        st.session_state.round = 1
        st.session_state.player_names_entered = True
        save_state()
        st.rerun()

if st.session_state.players:
    players = st.session_state.players
    if st.session_state.show_scoreboard:
        st.title("📊 Scoreboard")
        scoreboard = ""
        for p in players:
            scoreboard += f"**{p}** — Score: {st.session_state.scores[p]} | Bags: {st.session_state.bags[p]}\n\n"
        st.markdown(scoreboard)
    else:
        st.title(f"Round {st.session_state.round}")
        st.subheader("Enter Bids and Wins")

        bids = {}
        wins = {}

        cols = st.columns(2)
        with cols[0]:
            st.write("**Bids**")
            for i, p in enumerate(players):
                bids[p] = st.number_input(f"{p} bid", 0, 13, 0, key=f"bid_{i}_{st.session_state.round}")
        with cols[1]:
            st.write("**Wins**")
            for i, p in enumerate(players):
                wins[p] = st.number_input(f"{p} wins", 0, 13, 0, key=f"win_{i}_{st.session_state.round}")

        if st.button("Submit Round"):
            for p in players:
                bid = bids[p]
                win = wins[p]
                if win == bid:
                    st.session_state.scores[p] += 10 * bid + win
                elif win > bid:
                    st.session_state.scores[p] += 10 * bid + (win - bid)
                    st.session_state.bags[p] += (win - bid)
                else:
                    st.session_state.scores[p] -= 10 * bid
                if st.session_state.bags[p] >= 10:
                    st.session_state.scores[p] -= 100
                    st.session_state.bags[p] -= 10

            st.success("Round complete! Scores updated.")
            save_state()
            st.session_state.round += 1
            st.rerun()

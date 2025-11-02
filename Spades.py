import streamlit as st
import json
import os
import time
import base64

SAVE_FILE = "spades_game_state.json"

def save_state():
    try:
        state = {k: v for k, v in st.session_state.items() if not k.startswith("_")}
        with open(SAVE_FILE, "w") as f:
            json.dump(state, f)
    except:
        pass

def load_state():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        for k, v in data.items():
            st.session_state[k] = v

def reset_game():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
    st.session_state.clear()
    st.session_state.update({"round": 1, "scores": {}, "bags": {}, "history": [], "show_scoreboard": False})
    save_state()
    st.experimental_rerun()

@st.cache_data
def load_bg(image_file):
    with open(image_file, "rb") as f:
        return base64.b64encode(f.read()).decode()

def set_bg_from_local(image_file):
    encoded = load_bg(image_file)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

st.set_page_config(page_title="Spades Scoring", layout="wide")
set_bg_from_local("4.jpg")

load_state()

st.markdown("<h1 style='text-align: center; color: white;'>♠️ Spades Score Tracker ♠️</h1>", unsafe_allow_html=True)

if "round" not in st.session_state:
    st.session_state.round = 1
if "scores" not in st.session_state:
    st.session_state.scores = {}
if "bags" not in st.session_state:
    st.session_state.bags = {}
if "history" not in st.session_state:
    st.session_state.history = []
if "show_scoreboard" not in st.session_state:
    st.session_state.show_scoreboard = False

st.sidebar.markdown("## 🧭 Controls")
if st.sidebar.button("🔁 Restart Game"):
    reset_game()
if st.sidebar.button("📊 Scores"):
    st.session_state.show_scoreboard = not st.session_state.get("show_scoreboard", False)
    save_state()

if "players" not in st.session_state:
    decks = st.number_input("🃏 Number of Decks", min_value=1, step=1, key="decks")
    players_count = st.number_input("👥 Number of Players", min_value=2, max_value=8, step=1, key="players_count")
    players = [st.text_input(f"Enter Player {i+1} Name") for i in range(players_count)]
    if all(players):
        st.session_state.players = players
        for p in players:
            st.session_state.scores[p] = 0
            st.session_state.bags[p] = 0
        save_state()
        st.experimental_rerun()
    st.stop()

players = st.session_state.players
round_num = st.session_state.round

if st.session_state.show_scoreboard:
    st.markdown("### 📊 Current Scoreboard")
    scoreboard = []
    for p in players:
        scoreboard.append(f"**{p}** — {st.session_state.scores[p]} pts ({st.session_state.bags[p]} bags)")
    st.markdown("<br>".join(scoreboard), unsafe_allow_html=True)
    st.stop()

st.markdown(f"<h2 style='color: white;'>Round {round_num}</h2>", unsafe_allow_html=True)

cols = st.columns(len(players))
bids = {}
wins = {}
for i, p in enumerate(players):
    with cols[i]:
        bids[p] = st.number_input(f"{p} Bid", min_value=0, max_value=13, step=1, key=f"bid_{i}_{round_num}")
        wins[p] = st.number_input(f"{p} Won", min_value=0, max_value=13, step=1, key=f"win_{i}_{round_num}")

if st.button("✅ Submit Round"):
    total_bids = sum(bids.values())
    total_wins = sum(wins.values())
    if total_wins != total_bids:
        st.error("⚠️ Total wins must equal total bids!")
        st.stop()
    round_data = {"round": round_num, "bids": bids, "wins": wins}
    st.session_state.history.append(round_data)
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
    st.session_state.round += 1
    save_state()
    st.success("🎉 Round submitted successfully!")
    time.sleep(1)
    st.experimental_rerun()

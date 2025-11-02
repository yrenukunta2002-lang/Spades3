import streamlit as st
import pandas as pd
import time
import base64
import json
import os

st.set_page_config(page_title="♠️ Spades", page_icon="♠️", layout="centered")

SAVE_FILE = "spades_game_state.json"

def save_state():
    state = {k: v for k, v in st.session_state.items() if k not in ["_is_running_with_streamlit", "_session_state"]}
    with open(SAVE_FILE, "w") as f:
        json.dump(state, f)

def load_state():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            for k, v in data.items():
                st.session_state[k] = v

load_state()

def set_bg_from_local(image_file):
    with open(image_file, "rb") as file:
        encoded = base64.b64encode(file.read()).decode()
    css = f"""
    <style>
    :root {{ color-scheme: dark; }}
    html, body, [class*="stAppViewContainer"], .stApp {{
        height: 100%; width: 100%; overflow-x: hidden;
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)),
                    url(data:image/png;base64,{encoded});
        background-size: cover; background-position: center;
        background-repeat: no-repeat; background-attachment: fixed;
        color: #F5F5F5 !important; font-family: 'Poppins', sans-serif;
    }}
    .block-container {{
        background: rgba(0, 0, 0, 0.55);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.45);
        margin: auto; max-width: 800px;
    }}
    h1, h2, h3, h4 {{
        text-align: center; color: #FFFFFF !important;
        text-shadow: 0 0 12px rgba(0,0,0,0.7); font-weight: 600;
    }}
    .stButton>button {{
        background: linear-gradient(90deg, #7F00FF, #E100FF);
        color: white !important; border: none; border-radius: 10px;
        padding: 0.6rem 1.2rem; font-weight: 600; width: 100%;
        box-shadow: 0px 0px 10px rgba(142,45,226,0.4);
        transition: 0.3s ease;
    }}
    .stButton>button:hover {{
        box-shadow: 0px 0px 25px rgba(255,255,255,0.6);
        transform: scale(1.05);
    }}
    input, select, textarea {{
        background-color: rgba(255,255,255,0.12) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255,255,255,0.25) !important;
        color: #FFFFFF !important;
    }}
    div[data-testid="stExpander"] {{
        background: rgba(255,255,255,0.08);
        border-radius: 12px; color: #FFF !important;
    }}
    div[data-testid="stProgressBar"] > div {{
        background-color: #BB86FC !important;
    }}
    @media (max-width: 768px) {{
        .block-container {{ padding: 1rem; width: 95%; }}
        h1 {{ font-size: 1.6rem !important; }}
        .stButton>button {{ font-size: 0.9rem; padding: 0.5rem 1rem; }}
    }}
    @media (max-width: 480px) {{
        h1 {{ font-size: 1.3rem !important; }}
        .stButton>button {{ font-size: 0.85rem; padding: 0.4rem 0.8rem; }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

set_bg_from_local("4.jpg")

st.title("♠️ Spades")

with st.sidebar:
    if st.button("📊 Scores"):
        st.session_state.show_scoreboard = not st.session_state.get("show_scoreboard", False)
        save_state()
        st.rerun()
    if st.button("🔁 Restart Game"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
        st.success("Game restarted!")
        st.rerun()

if "setup_done" not in st.session_state:
    st.session_state.setup_done = False
    st.session_state.names_entered = False
    st.session_state.round = 1
    st.session_state.scores = []
    st.session_state.bags = []
    st.session_state.show_scoreboard = False
    st.session_state.history = []
    st.session_state.round_summary_display = False

if st.session_state.get("show_scoreboard", False) and "scores" in st.session_state:
    with st.expander("📊 Current Scoreboard", expanded=True):
        st.subheader("🏅 Total Scores")
        for i, name in enumerate(st.session_state.player_names):
            if st.session_state.enable_bags:
                st.write(f"**{name or f'Player {i+1}'}:** {st.session_state.scores[i]} pts ({st.session_state.bags[i]} bags)")
            else:
                st.write(f"**{name or f'Player {i+1}'}:** {st.session_state.scores[i]} pts")
        if st.session_state.history:
            st.markdown("---")
            st.subheader("🧾 Round-wise Details")
            df = pd.DataFrame(st.session_state.history)
            rounds = sorted(df["Round"].unique())
            for r in rounds:
                with st.expander(f"▶️ Round {r}", expanded=False):
                    rd = df[df["Round"] == r][["Player", "Bid", "Win", "Round Points", "Total Points"] + (["Bags"] if st.session_state.enable_bags else [])]
                    st.table(rd.reset_index(drop=True))
        else:
            st.info("No rounds completed yet.")
        st.write("---")

if not st.session_state.setup_done:
    st.header("Game Setup")
    num_decks = st.number_input("Number of Decks", min_value=1, step=1, value=1)
    num_players = st.number_input("Number of Players", min_value=2, step=1, value=4)
    cards_per_deck = 52
    max_rounds_by_decks = 13 * num_decks
    max_possible_round = min(13, (cards_per_deck * num_decks) // num_players)
    total_rounds = min(max_possible_round, max_rounds_by_decks)
    st.markdown(f"**🃏 Total Rounds Possible:** {total_rounds}")
    game_mode = st.selectbox("Select Game Mode", ["With Bags (Standard Rules)", "Without Bags (No Bag Penalty)"], index=0)
    if st.button("Next"):
        st.session_state.num_decks = num_decks
        st.session_state.num_players = num_players
        st.session_state.enable_bags = game_mode.startswith("With Bags")
        st.session_state.player_names = ["" for _ in range(num_players)]
        st.session_state.scores = [0 for _ in range(num_players)]
        st.session_state.bags = [0 for _ in range(num_players)]
        st.session_state.total_rounds = total_rounds
        st.session_state.setup_done = True
        save_state()
        st.rerun()

elif not st.session_state.names_entered:
    st.header("Enter Player Names")
    for i in range(st.session_state.num_players):
        st.session_state.player_names[i] = st.text_input(f"Player {i+1} Name", st.session_state.player_names[i])
    if st.button("Start Game"):
        st.session_state.names_entered = True
        save_state()
        st.rerun()

elif st.session_state.round <= st.session_state.total_rounds:
    if st.session_state.round_summary_display:
        st.header(f"🏁 Round {st.session_state.round - 1} Summary")
        st.subheader("📊 Current Scores")
        for i, name in enumerate(st.session_state.player_names):
            if st.session_state.enable_bags:
                st.write(f"**{name or f'Player {i+1}'}:** {st.session_state.scores[i]} pts ({st.session_state.bags[i]} bags)")
            else:
                st.write(f"**{name or f'Player {i+1}'}:** {st.session_state.scores[i]} pts")
        st.markdown("---")
        countdown_placeholder = st.empty()
        for sec in range(3, 0, -1):
            countdown_placeholder.markdown(f"<h3 style='text-align:center; color:#FFD700;'>🕒 Round {st.session_state.round} starts in <b>{sec}</b>...</h3>", unsafe_allow_html=True)
            time.sleep(1)
        st.session_state.round_summary_display = False
        save_state()
        st.rerun()

    round_num = st.session_state.round
    st.header(f"Round {round_num}")
    st.progress(round_num / st.session_state.total_rounds)

    bids, wins = [], []
    st.markdown("### ✍️ Enter Bids and Wins")
    cols = st.columns([2, 1, 1])
    cols[0].markdown("**Player**")
    cols[1].markdown("**Bid**")
    cols[2].markdown("**Won**")

    for i, name in enumerate(st.session_state.player_names):
        col1, col2, col3 = st.columns([2, 1, 1])
        col1.text(name or f"Player {i+1}")
        bid = col2.number_input(f"Bid_{i}", min_value=0, step=1, key=f"bid_{i}_{round_num}", label_visibility="collapsed")
        win = col3.number_input(f"Win_{i}", min_value=0, step=1, key=f"win_{i}_{round_num}", label_visibility="collapsed")
        bids.append(bid)
        wins.append(win)

    if st.button("Submit Round ✅"):
        total_wins = sum(wins)
        tricks_this_round = round_num
        if total_wins != tricks_this_round:
            st.error(f"❌ Invalid: Total wins ({total_wins}) must equal tricks in this round ({tricks_this_round}).")
            st.stop()
        round_summary = []
        for i in range(st.session_state.num_players):
            bid = bids[i]
            win = wins[i]
            if st.session_state.enable_bags:
                if bid == 0 and win == 0:
                    points = 0
                elif win == bid:
                    points = 10 * bid
                elif win < bid:
                    points = -10 * bid
                else:
                    extras = win - bid
                    points = 10 * bid + extras
                    st.session_state.bags[i] += extras
                st.session_state.scores[i] += points
                if st.session_state.bags[i] >= 5:
                    st.session_state.scores[i] -= 50
                    st.session_state.bags[i] -= 5
                    st.warning(f"{st.session_state.player_names[i]} lost 50 pts (5 bags penalty)")
            else:
                if bid == 0 and win == 0:
                    points = 0
                elif win == bid:
                    points = 10 * bid
                elif win < bid:
                    points = -10 * bid
                else:
                    extras = win - bid
                    points = 10 * bid + extras
                st.session_state.scores[i] += points
            round_summary.append(f"{st.session_state.player_names[i]}: +{points} pts")
            entry = {"Round": round_num, "Player": st.session_state.player_names[i], "Bid": bid, "Win": win, "Round Points": points, "Total Points": st.session_state.scores[i]}
            if st.session_state.enable_bags:
                entry["Bags"] = st.session_state.bags[i]
            st.session_state.history.append(entry)
        st.success(f"✅ Round {round_num} completed successfully!")
        st.info("\n".join(round_summary))
        st.session_state.round += 1
        st.session_state.round_summary_display = True
        save_state()
        st.rerun()

else:
    st.header("🏁 Final Results")
    for i, name in enumerate(st.session_state.player_names):
        if st.session_state.enable_bags:
            st.write(f"{name or f'Player {i+1}'}: **{st.session_state.scores[i]} pts** ({st.session_state.bags[i]} bags)")
        else:
            st.write(f"{name or f'Player {i+1}'}: **{st.session_state.scores[i]} pts**")
    winner_idx = st.session_state.scores.index(max(st.session_state.scores))
    st.success(f"🏆 Winner: {st.session_state.player_names[winner_idx]}")
    if st.checkbox("Enable Scoreboard Download"):
        df = pd.DataFrame(st.session_state.history)
        st.download_button("💾 Download Full Scoreboard (CSV)", df.to_csv(index=False), "spades_full_scoreboard.csv")
    save_state()

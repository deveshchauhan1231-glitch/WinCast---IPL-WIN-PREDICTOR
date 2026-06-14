import streamlit as st
import pickle
import pandas as pd
from pathlib import Path


st.set_page_config(
    page_title="WinCast - IPL Win Predictor",
    page_icon=str(BASE_DIR / "logo.png"),
    layout="centered"
)

BASE_DIR = Path(__file__).parent

@st.cache_resource
def load_model():
    with open(BASE_DIR / "model.pkl", "rb") as f:
        return pickle.load(f)

model = load_model()



st.title("IPL Win Predictor")

TEAMS = ["CSK", "MI", "RCB", "KKR", "SRH", "DC", "PBKS", "RR", "LSG", "GT"]

VENUES = [
    "Wankhede Stadium (MI)",
    "M. A. Chidambaram Stadium (CSK)",
    "Eden Gardens (KKR)",
    "M. Chinnaswamy Stadium (RCB)",
    "Arun Jaitley Stadium (DC)",
    "Rajiv Gandhi International Stadium (SRH)",
    "Punjab Cricket Association IS Bindra Stadium (PBKS)",
    "Sawai Mansingh Stadium (RR)",
    "Ekana Cricket Stadium (LSG)",
    "Narendra Modi Stadium (GT)",
    "Dubai International Cricket Stadium (Neutral)",
    "Sheikh Zayed Stadium (Neutral)",
]

st.subheader("Match Setup")
col1, col2 = st.columns(2)
team1 = col1.selectbox("Team 1", TEAMS)
team2 = col2.selectbox("Team 2", [t for t in TEAMS if t != team1])

col3, col4 = st.columns(2)
toss_winner = col3.selectbox("Toss Winner", [team1, team2])
toss_decision = col4.selectbox("Toss Decision", ["Bat", "Field"])

venue = st.selectbox("Venue", VENUES)

st.subheader("Innings Roles")
col5, col6 = st.columns(2)

if toss_decision == "Bat":
    batting_team = toss_winner
else:
    batting_team = team2 if toss_winner == team1 else team1

chasing_team = team2 if batting_team == team1 else team1

col5.text_input("Batting Team", value=batting_team, disabled=True)
col6.text_input("Chasing Team", value=chasing_team, disabled=True)

st.subheader(f"{batting_team} — 1st Innings")
col7, col8 = st.columns(2)
total_score = col7.number_input("Total Score", min_value=0, max_value=300, value=170)
total_wickets = col8.number_input("Wickets Fallen", min_value=0, max_value=10, value=6)

st.subheader(f"{chasing_team} — 2nd Innings (Live)")
col9, col10 = st.columns(2)
current_score = col9.number_input("Current Score", min_value=0, max_value=300, value=80)
current_wickets = col10.number_input("Wickets Down", min_value=0, max_value=10, value=3)
overs_done = st.text_input("Overs Completed (e.g. 12.4)", value="12.4")

is_powerplay=1
is_middle_overs=0
is_death_overs=0
def phase(s):
    try:
        global is_death_overs, is_middle_overs, is_powerplay
        f = float(s.strip())
        if f < 6:
            is_powerplay=1
            is_middle_overs=0
            is_death_overs=0
        elif f < 16:
            is_powerplay=0
            is_middle_overs=1
            is_death_overs=0
        else:
            is_powerplay=0
            is_middle_overs=0
            is_death_overs=1
    except:
        return None
def parse_overs(s):
    try:
        f = float(s.strip())
        full = int(f)
        balls = min(round((f - full) * 10), 5)
        return full * 6 + balls
    except:
        return None

avg_score=0
ground_toss_advantage=0
chasing_win_percentage=0
AVG_SCORE = {
    "CSK": 155.14,
    "DC": 162.07,
    "DCG": 155.74,
    "GL": 147.92,
    "GT": 177.82,
    "KKR": 160.94,
    "LSG": 161.36,
    "MI": 165.74,
    "Neutral": 149.49,
    "PBKS": 165.82,
    "PWI": 141.50,
    "RCB": 164.21,
    "RPS": 158.79,
    "RR": 161.34,
    "SRH": 159.42
}

GROUND_TOSS_ADVANTAGE = {
    "CSK": 50.53,
    "DC": 49.50,
    "DCG": 52.94,
    "GL": 40.91,
    "GT": 45.95,
    "KKR": 50.00,
    "LSG": 61.54,
    "MI": 51.54,
    "Neutral": 52.27,
    "PBKS": 52.00,
    "PWI": 56.25,
    "RCB": 52.88,
    "RPS": 54.29,
    "RR": 54.05,
    "SRH": 36.78
}

CHASING_WIN_PERCENTAGE = {
    "CSK": 46.32,
    "DC": 53.47,
    "DCG": 52.94,
    "GL": 59.09,
    "GT": 51.35,
    "KKR": 58.65,
    "LSG": 61.54,
    "MI": 55.38,
    "Neutral": 56.44,
    "PBKS": 56.00,
    "PWI": 37.50,
    "RCB": 57.69,
    "RPS": 48.57,
    "RR": 63.51,
    "SRH": 56.32
}

avg_score=0
ground_toss_advantage=0
chasing_win_percentage=0

def parse_venue(v):
    try:
        global venue
        venue = v.split("(")[1].rstrip(")")

        global avg_score, ground_toss_advantage, chasing_win_percentage
        avg_score = AVG_SCORE[venue]
        ground_toss_advantage = GROUND_TOSS_ADVANTAGE[venue]
        chasing_win_percentage = CHASING_WIN_PERCENTAGE[venue]
    except:
        return None


if st.button("Predict", type="primary"):
    balls_done = parse_overs(overs_done)
    if balls_done is None:
        st.error("Invalid overs format. Use X.Y like 12.4")
        st.stop()
    phase(overs_done)
    parse_venue(venue)

    balls_remaining = 120 - balls_done
    runs_required = total_score - current_score + 1
    wickets_remaining = 10 - current_wickets
    crr = (current_score / balls_done * 6) if balls_done > 0 else 0.0
    rrr = (runs_required / balls_remaining * 6) if balls_remaining > 0 else 999.0

    input_df = pd.DataFrame([{
        "batting_team": batting_team,
        "bowling_team": chasing_team,
        "venue": venue,
        "toss_winner": toss_winner,
        "toss_decision": toss_decision.lower(),
        "target": total_score,
        "avg_score":avg_score,
        "is_powerplay": is_powerplay,
        "is_middle_overs": is_middle_overs,
        "is_death_overs": is_death_overs,
        "ground_toss_advantage":ground_toss_advantage,
        "chasing_win_percentage":chasing_win_percentage,
        # "total_wickets": total_wickets,
        "total_runs": current_score,
        # "current_wickets": current_wickets,
        # "balls_done": balls_done,
        "balls_left": balls_remaining,
        # "runs_required": runs_required,
        "wickets_left": wickets_remaining,
        "innings2_crr": round(crr, 4),
        "innings2_rrr": round(rrr, 4),
        "innings1_rr":round(total_score/20,4)
    }])

    proba = model.predict_proba(input_df)[0]
    chase_win = round(proba[1] * 100, 1)
    bat_win = round(100 - chase_win, 1)
    print(venue)

    st.subheader("Result")
    st.metric(f"{batting_team} Win Probability", f"{bat_win:.2f}%")
    st.metric(f"{chasing_team} Win Probability", f"{chase_win:.2f}%")
    st.progress(int(chase_win), text=f"{chasing_team} {chase_win:.2f}% vs {batting_team} {bat_win:.2f}%")

    st.info(f"Need {runs_required} runs off {balls_remaining} balls | CRR {crr:.2f} | RRR {rrr:.2f} | {wickets_remaining} wickets left")

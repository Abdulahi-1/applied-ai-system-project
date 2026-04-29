import os
import streamlit as st
from dotenv import load_dotenv

from models.schemas import Task
from agent.tools import SchedulerTools

load_dotenv()

# ── page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PawPal+ · Smart Pet Care",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── helpers ────────────────────────────────────────────────────────────────────
def task_icon(name: str) -> str:
    n = name.lower()
    if any(w in n for w in ["walk", "run", "hike", "exercise", "jog"]): return "🦮"
    if any(w in n for w in ["feed", "food", "meal", "eat", "breakfast", "dinner", "lunch"]): return "🍖"
    if any(w in n for w in ["groom", "bath", "brush", "wash", "trim", "nail", "fur"]): return "✂️"
    if any(w in n for w in ["play", "game", "toy", "fetch", "tug", "fun"]): return "🎾"
    if any(w in n for w in ["vet", "doctor", "health", "medicine", "pill", "shot", "vaccine", "checkup"]): return "💊"
    if any(w in n for w in ["train", "training", "sit", "stay", "heel", "command", "obedience"]): return "🏆"
    if any(w in n for w in ["sleep", "rest", "nap", "bed", "crate"]): return "💤"
    if any(w in n for w in ["potty", "toilet", "outside", "poop", "bathroom", "litter"]): return "🌿"
    if any(w in n for w in ["socializ", "park", "friend", "dog park"]): return "🐾"
    return "🐾"

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800;900&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
h1, h2, h3, h4 { font-family: 'Nunito', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ── page background ─────────────────────────────────────────── */
.stApp { background: #F0F9FF !important; }
.main .block-container { padding: 1.75rem 2.25rem 5rem; max-width: 1060px; }

/* ── sidebar ─────────────────────────────────────────────────── */
[data-testid="stSidebar"] > div:first-child {
    background: linear-gradient(175deg, #0c1a3a 0%, #1e3a8a 50%, #0369a1 100%);
    padding-top: 0;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div { color: rgba(255,255,255,0.9) !important; }

[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stNumberInput input {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    color: white !important;
    caret-color: white !important;
    -webkit-text-fill-color: white !important;
    padding: 0.6rem 0.9rem !important;
    font-size: 0.875rem !important;
    transition: border-color 0.2s, background 0.2s !important;
}
[data-testid="stSidebar"] .stTextInput input:focus,
[data-testid="stSidebar"] .stNumberInput input:focus {
    background: rgba(255,255,255,0.13) !important;
    border-color: rgba(125,211,252,0.7) !important;
}
[data-testid="stSidebar"] .stTextInput input::placeholder { color: rgba(255,255,255,0.35) !important; }
[data-testid="stSidebar"] .stNumberInput input { -webkit-text-fill-color: white !important; }
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    font-size: 0.875rem !important;
}
[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%) !important;
    border: none !important;
    color: white !important;
    border-radius: 12px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 800 !important;
    font-size: 0.9rem !important;
    padding: 0.8rem 1rem !important;
    box-shadow: 0 4px 20px rgba(14,165,233,0.4) !important;
    transition: all 0.2s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    box-shadow: 0 6px 28px rgba(14,165,233,0.6) !important;
    transform: translateY(-2px) !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.10) !important;
    margin: 1rem 0 !important;
}

/* ── tabs ────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(224,242,254,0.8);
    border-radius: 16px;
    padding: 5px;
    gap: 4px;
    border: 1px solid #BAE6FD;
    box-shadow: 0 2px 12px rgba(14,165,233,0.08);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 11px !important;
    padding: 0.55rem 1.5rem !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    color: #0369a1 !important;
    background: transparent !important;
    border: none !important;
    transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #0284c7 !important;
    box-shadow: 0 2px 12px rgba(14,165,233,0.15) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }

/* ── form inputs ─────────────────────────────────────────────── */
.stTextInput input, .stNumberInput input {
    border-radius: 11px !important;
    border: 1.5px solid #BAE6FD !important;
    padding: 0.65rem 0.95rem !important;
    font-size: 0.9rem !important;
    background: white !important;
    color: #1e293b !important;
    caret-color: #0ea5e9 !important;
    box-shadow: 0 1px 3px rgba(14,165,233,0.06) !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #0ea5e9 !important;
    box-shadow: 0 0 0 3px rgba(14,165,233,0.12) !important;
    background: white !important;
}
.stSelectbox > div > div {
    border-radius: 11px !important;
    border: 1.5px solid #BAE6FD !important;
    background: white !important;
    color: #1e293b !important;
    box-shadow: 0 1px 3px rgba(14,165,233,0.06) !important;
}

/* ── buttons ─────────────────────────────────────────────────── */
.stButton > button {
    border-radius: 10px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.875rem !important;
    transition: all 0.2s !important;
    border: 1.5px solid #BAE6FD !important;
    background: white !important;
    color: #0369a1 !important;
    box-shadow: 0 1px 4px rgba(14,165,233,0.08) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(14,165,233,0.14) !important;
    border-color: #7DD3FC !important;
    background: #F0F9FF !important;
}

/* ── progress bar ────────────────────────────────────────────── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #38bdf8, #7dd3fc) !important;
    border-radius: 100px !important;
}
.stProgress > div > div {
    background: #E0F2FE !important;
    border-radius: 100px !important;
}

/* ── alerts ──────────────────────────────────────────────────── */
.stSuccess { border-radius: 12px !important; }
.stWarning { border-radius: 12px !important; }
.stError   { border-radius: 12px !important; }
.stInfo    { border-radius: 12px !important; }

/* ── chat ────────────────────────────────────────────────────── */
[data-testid="stChatInput"] textarea {
    border-radius: 16px !important;
    border: 1.5px solid #BAE6FD !important;
    background: white !important;
    font-size: 0.9rem !important;
    box-shadow: 0 2px 8px rgba(14,165,233,0.08) !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #0ea5e9 !important;
    box-shadow: 0 0 0 3px rgba(14,165,233,0.12) !important;
}

/* ══════════════════════════════════════════════════════════════
   CUSTOM COMPONENTS
   ══════════════════════════════════════════════════════════════ */

/* ── hero ────────────────────────────────────────────────────── */
.paw-hero {
    background: linear-gradient(135deg, #0c1a3a 0%, #1e3a8a 45%, #0369a1 100%);
    border-radius: 24px;
    padding: 2rem 2.5rem;
    color: white;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 40px rgba(14,165,233,0.28);
    position: relative;
    overflow: hidden;
}
.paw-hero::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: rgba(186,230,253,0.06);
    border-radius: 50%;
}
.paw-hero::after {
    content: '';
    position: absolute;
    bottom: -60px; right: 80px;
    width: 150px; height: 150px;
    background: rgba(125,211,252,0.07);
    border-radius: 50%;
}
.paw-hero .pet-avatar {
    width: 80px; height: 80px;
    background: rgba(255,255,255,0.12);
    border-radius: 20px;
    display: flex; align-items: center; justify-content: center;
    font-size: 2.4rem;
    flex-shrink: 0;
    border: 2px solid rgba(255,255,255,0.15);
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
}
.paw-hero .hero-content { flex: 1; }
.paw-hero h2 {
    margin: 0;
    font-size: 1.7rem;
    font-weight: 900;
    letter-spacing: -0.02em;
    font-family: 'Nunito', sans-serif !important;
}
.paw-hero .hero-sub { margin: 0.3rem 0 0.6rem; opacity: 0.65; font-size: 0.88rem; }
.paw-hero .pill-row { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.paw-hero .pill {
    display: inline-flex; align-items: center;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 100px;
    padding: 4px 12px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    font-family: 'Nunito', sans-serif;
}
.paw-hero .hero-stats {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-end;
    flex-shrink: 0;
}
.paw-hero .hstat {
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 14px;
    padding: 0.6rem 1rem;
    text-align: center;
    min-width: 70px;
}
.paw-hero .hstat .hval {
    font-size: 1.5rem; font-weight: 900; line-height: 1;
    font-family: 'Nunito', sans-serif;
}
.paw-hero .hstat .hlbl {
    font-size: 0.65rem; opacity: 0.55;
    text-transform: uppercase; letter-spacing: 0.07em;
    margin-top: 2px; font-weight: 700;
}

/* ── section label ───────────────────────────────────────────── */
.section-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.72rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #38BDF8;
    margin: 1.5rem 0 0.75rem;
    font-family: 'Nunito', sans-serif;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #BAE6FD, transparent);
}

/* ── stat cards ──────────────────────────────────────────────── */
.stat-card {
    flex: 1;
    background: white;
    border-radius: 18px;
    padding: 1.1rem 1.25rem 1rem;
    border: 1px solid #BAE6FD;
    box-shadow: 0 2px 10px rgba(14,165,233,0.07);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.15rem;
    position: relative;
    overflow: hidden;
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 18px 18px 0 0;
}
.stat-card.blue::before  { background: linear-gradient(90deg, #0ea5e9, #38bdf8); }
.stat-card.green::before { background: linear-gradient(90deg, #10b981, #34d399); }
.stat-card.red::before   { background: linear-gradient(90deg, #ef4444, #f87171); }
.stat-card.sky::before   { background: linear-gradient(90deg, #7dd3fc, #bae6fd); }
.stat-card .val  { font-size: 2rem; font-weight: 900; color: #1e293b; line-height: 1; font-family: 'Nunito', sans-serif; }
.stat-card .val.red   { color: #ef4444; }
.stat-card .val.green { color: #10b981; }
.stat-card .val.blue  { color: #0284c7; }
.stat-card .val.sky   { color: #0ea5e9; }
.stat-card .lbl { font-size: 0.7rem; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.07em; font-weight: 700; }

/* ── budget bar ──────────────────────────────────────────────── */
.budget-bar-wrap {
    background: white;
    border-radius: 16px;
    padding: 1.1rem 1.4rem;
    border: 1px solid #BAE6FD;
    box-shadow: 0 2px 10px rgba(14,165,233,0.06);
    margin-bottom: 1rem;
}
.budget-bar-wrap .bar-label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.82rem;
    font-weight: 700;
    color: #6B7280;
    margin-bottom: 0.6rem;
    font-family: 'Nunito', sans-serif;
}
.budget-bar-wrap .bar-label span:first-child { color: #374151; font-size: 0.88rem; }

/* ── add form card ───────────────────────────────────────────── */
.add-form-card {
    background: white;
    border: 2px solid #BAE6FD;
    border-radius: 18px;
    padding: 1.25rem 1.5rem 0.75rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 2px 12px rgba(14,165,233,0.07);
}
.add-form-card .form-header {
    font-size: 0.78rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: #0284C7;
    margin-bottom: 0.75rem;
    font-family: 'Nunito', sans-serif;
}

/* ── task card ───────────────────────────────────────────────── */
.task-card {
    background: white;
    border-radius: 16px;
    padding: 0.85rem 1.15rem;
    border: 1px solid #BAE6FD;
    box-shadow: 0 2px 8px rgba(14,165,233,0.06);
    display: flex;
    align-items: center;
    gap: 0.85rem;
    margin-bottom: 0.55rem;
    transition: box-shadow 0.2s, transform 0.15s;
}
.task-card:hover { box-shadow: 0 6px 20px rgba(14,165,233,0.14); transform: translateY(-1px); }
.task-icon {
    width: 42px; height: 42px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    flex-shrink: 0;
    background: #E0F2FE;
}
.task-card .name {
    font-weight: 700;
    font-size: 0.93rem;
    color: #1e293b;
    font-family: 'Nunito', sans-serif;
}
.task-card .meta { font-size: 0.78rem; color: #9CA3AF; margin-top: 2px; }
.task-card .right { margin-left: auto; display: flex; align-items: center; gap: 0.5rem; flex-shrink: 0; }
.task-card .priority-bar { width: 3px; height: 36px; border-radius: 100px; flex-shrink: 0; }
.done-card { opacity: 0.45; }
.done-card .name { text-decoration: line-through; }

/* ── badges ──────────────────────────────────────────────────── */
.badge {
    font-size: 0.7rem;
    font-weight: 800;
    padding: 3px 10px;
    border-radius: 100px;
    letter-spacing: 0.04em;
    font-family: 'Nunito', sans-serif;
}
.badge-high   { background: #FEE2E2; color: #DC2626; }
.badge-medium { background: #DBEAFE; color: #1D4ED8; }
.badge-low    { background: #D1FAE5; color: #065f46; }

/* ── timeline ────────────────────────────────────────────────── */
.timeline-item { display: flex; gap: 1rem; margin-bottom: 0.75rem; align-items: flex-start; }
.timeline-dot {
    width: 38px; height: 38px;
    border-radius: 50%;
    background: linear-gradient(135deg, #0ea5e9, #38bdf8);
    color: white;
    font-weight: 900;
    font-size: 0.88rem;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 3px 12px rgba(14,165,233,0.4);
    margin-top: 2px;
    font-family: 'Nunito', sans-serif;
}
.timeline-card {
    flex: 1;
    background: white;
    border-radius: 16px;
    padding: 0.9rem 1.15rem;
    border: 1px solid #BAE6FD;
    box-shadow: 0 2px 8px rgba(14,165,233,0.06);
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.timeline-card .ticon {
    font-size: 1.25rem;
    width: 38px; height: 38px;
    background: #E0F2FE;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.timeline-card .tname { font-weight: 700; color: #1e293b; font-size: 0.93rem; font-family: 'Nunito', sans-serif; }
.timeline-card .tmeta { font-size: 0.78rem; color: #9CA3AF; margin-top: 2px; }
.timeline-card .tright { margin-left: auto; flex-shrink: 0; }

/* ── empty state ─────────────────────────────────────────────── */
.empty-state {
    text-align: center;
    padding: 3.5rem 1rem;
    color: #9CA3AF;
}
.empty-state .paw-icon { font-size: 2.5rem; margin-bottom: 0.85rem; display: block; opacity: 0.4; }
.empty-state .etitle { font-size: 1rem; font-weight: 800; color: #6B7280; font-family: 'Nunito', sans-serif; margin-bottom: 0.3rem; }
.empty-state .esub { font-size: 0.85rem; margin: 0; }

/* ── prompt chips ────────────────────────────────────────────── */
.chip-row { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1.25rem; }
.prompt-chip {
    display: inline-flex;
    align-items: center;
    background: white;
    border: 1.5px solid #BAE6FD;
    border-radius: 100px;
    padding: 6px 14px;
    font-size: 0.8rem;
    color: #0284c7;
    font-weight: 700;
    font-family: 'Nunito', sans-serif;
    box-shadow: 0 1px 4px rgba(14,165,233,0.08);
}

/* ── sidebar snapshot ────────────────────────────────────────── */
.snap-grid { display: flex; gap: 0.6rem; margin-bottom: 0.75rem; }
.snap-cell {
    flex: 1;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 12px;
    padding: 0.7rem 0.5rem;
    text-align: center;
}
.snap-cell .sv { font-size: 1.4rem; font-weight: 900; line-height: 1; font-family: 'Nunito', sans-serif; }
.snap-cell .sl { font-size: 0.62rem; opacity: 0.45; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 3px; font-weight: 700; }

/* ── sidebar section header ──────────────────────────────────── */
.sb-label {
    font-size: 0.68rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: rgba(255,255,255,0.35);
    margin-bottom: 0.55rem;
    font-family: 'Nunito', sans-serif;
}
</style>
""", unsafe_allow_html=True)

# ── constants ──────────────────────────────────────────────────────────────────
PRIORITY_MAP   = {"low": 3, "medium": 6, "high": 9}
PRIORITY_LABEL = {3: "Low", 6: "Medium", 9: "High"}
PRIORITY_COLOR = {3: "#10b981", 6: "#3B82F6", 9: "#ef4444"}
PRIORITY_BADGE = {3: "badge-low", 6: "badge-medium", 9: "badge-high"}
SPECIES_EMOJI  = {"dog": "🐕", "cat": "🐈", "other": "🐾"}

# ── session state ──────────────────────────────────────────────────────────────
if "tools"        not in st.session_state: st.session_state.tools = None
if "agent"        not in st.session_state: st.session_state.agent = None
if "chat_history" not in st.session_state: st.session_state.chat_history = []

def sched():
    return st.session_state.tools.schedule if st.session_state.tools else None

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.html("""
    <div style="text-align:center; padding: 2rem 0 1.4rem;">
        <div style="display:inline-flex;align-items:center;justify-content:center;
                    width:64px;height:64px;background:rgba(255,255,255,0.10);
                    border-radius:18px;font-size:2rem;margin-bottom:0.75rem;
                    border:1px solid rgba(255,255,255,0.15);
                    box-shadow:0 4px 20px rgba(0,0,0,0.2);">🐾</div>
        <div style="font-size:1.6rem;font-weight:900;color:white;letter-spacing:-0.03em;
                    font-family:'Nunito',sans-serif;">Paw<span style="color:#7DD3FC;">Pal+</span></div>
        <div style="font-size:0.7rem;color:rgba(255,255,255,0.35);margin-top:4px;
                    letter-spacing:0.12em;font-weight:800;font-family:'Nunito',sans-serif;">
            SMART PET CARE
        </div>
    </div>
    """)

    st.html('<hr>')

    st.html('<div class="sb-label">Owner</div>')
    owner_name        = st.text_input("Your name",        value="Jordan", label_visibility="collapsed", placeholder="Your name")
    available_minutes = st.number_input("Daily time (min)", min_value=10, max_value=480, value=120, label_visibility="collapsed")

    st.html('<div style="height:0.5rem"></div>')

    st.html('<div class="sb-label">🐾 Pet Profile</div>')
    pet_name = st.text_input("Pet name", value="Mochi", label_visibility="collapsed", placeholder="Pet name")
    breed    = st.text_input("Breed",    value="Mixed", label_visibility="collapsed", placeholder="Breed")

    c1, c2 = st.columns(2)
    with c1: size    = st.selectbox("Size",    ["small","medium","large"], label_visibility="collapsed")
    with c2: species = st.selectbox("Species", ["dog","cat","other"],      label_visibility="collapsed")
    age = st.number_input("Age (years)", min_value=0, max_value=30, value=2, label_visibility="collapsed")

    st.html("<div style='height:0.5rem'></div>")

    if st.button("Save Profile", use_container_width=True):
        existing = list(st.session_state.tools.schedule.tasks) if st.session_state.tools else []
        tools = SchedulerTools(
            owner_name=owner_name, pet_name=pet_name,
            available_minutes=int(available_minutes),
            species=species, breed=breed, size=size, age_years=int(age),
        )
        for t in existing:
            tools.schedule.add_task(t)
        st.session_state.tools = tools
        st.session_state.agent = None
        st.session_state.chat_history = []
        st.success(f"Profile saved for {pet_name}!")

    if st.session_state.tools:
        s = sched()
        st.html('<hr>')
        total         = s.get_total_duration()
        budget        = s.owner.available_minutes
        pct           = min(int(total / budget * 100), 100) if budget else 0
        remaining     = max(budget - total, 0)
        over          = max(total - budget, 0)
        done_ct       = sum(1 for t in s.tasks if t.is_completed)
        budget_status = f'{over} min over' if over else f'{remaining} min free'

        st.html(f"""
        <div style="padding:0 0.1rem;">
          <div class="sb-label">Today's Snapshot</div>
          <div class="snap-grid">
            <div class="snap-cell">
              <div class="sv">{len(s.tasks)}</div>
              <div class="sl">Tasks</div>
            </div>
            <div class="snap-cell">
              <div class="sv">{done_ct}</div>
              <div class="sl">Done</div>
            </div>
            <div class="snap-cell">
              <div class="sv">{total}</div>
              <div class="sl">Min</div>
            </div>
          </div>
          <div style="background:rgba(255,255,255,0.08);border-radius:100px;height:7px;overflow:hidden;margin-bottom:0.45rem;">
            <div style="height:100%;width:{pct}%;background:linear-gradient(90deg,#38bdf8,#7dd3fc);
                        border-radius:100px;transition:width 0.4s;"></div>
          </div>
          <div style="font-size:0.72rem;opacity:0.5;display:flex;justify-content:space-between;
                      font-family:'Nunito',sans-serif;font-weight:700;">
            <span>{pct}% used</span>
            <span>{budget_status}</span>
          </div>
        </div>
        """)

# ══════════════════════════════════════════════════════════════════════════════
# HERO BANNER
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.tools:
    s            = sched()
    emoji        = SPECIES_EMOJI.get(species, "🐾")
    completed    = sum(1 for t in s.tasks if t.is_completed)
    pending      = len(s.tasks) - completed
    task_word    = "tasks" if len(s.tasks) != 1 else "task"
    done_pill    = f'<span class="pill">{completed} done</span>' if completed else ''
    pending_pill = f'<span class="pill">{pending} pending</span>' if pending else ''
    st.html(f"""
    <div class="paw-hero">
      <div class="pet-avatar">{emoji}</div>
      <div class="hero-content">
        <div style="margin:0;font-size:1.7rem;font-weight:900;letter-spacing:-0.02em;font-family:'Nunito',sans-serif;line-height:1.2;">Hey {s.owner.name}!</div>
        <p class="hero-sub">{s.pet.name} · {s.pet.breed} · {s.pet.age_years} yr old {s.pet.species}</p>
        <div class="pill-row">
          <span class="pill">{len(s.tasks)} {task_word}</span>
          {done_pill}
          {pending_pill}
        </div>
      </div>
      <div class="hero-stats">
        <div class="hstat">
          <div class="hval">{s.owner.available_minutes}</div>
          <div class="hlbl">min/day</div>
        </div>
        <div class="hstat">
          <div class="hval">{s.get_total_duration()}</div>
          <div class="hlbl">scheduled</div>
        </div>
      </div>
    </div>
    """)
else:
    st.html("""
    <div class="paw-hero">
      <div class="pet-avatar">🐾</div>
      <div class="hero-content">
        <div style="margin:0;font-size:1.7rem;font-weight:900;letter-spacing:-0.02em;font-family:'Nunito',sans-serif;line-height:1.2;">Welcome to PawPal+</div>
        <p class="hero-sub">Your smart pet care scheduling assistant</p>
        <div class="pill-row">
          <span class="pill">Set up your profile to get started</span>
        </div>
      </div>
    </div>
    """)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab_tasks, tab_schedule, tab_ai = st.tabs(["📋  Tasks", "📅  Schedule", "🤖  AI Assistant"])

# ── TAB 1 — Tasks ─────────────────────────────────────────────────────────────
with tab_tasks:
    s = sched()

    if s:
        total      = s.get_total_duration()
        budget     = s.owner.available_minutes
        time_left  = budget - total
        high_count = sum(1 for t in s.tasks if t.is_high_priority())
        done_count = sum(1 for t in s.tasks if t.is_completed)

        tl_class  = "red" if time_left < 0 else "green"
        tl_label  = "Min Over" if time_left < 0 else "Min Free"

        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.html(f"""
        <div class="stat-card blue">
          <div class="val blue">{len(s.tasks)}</div>
          <div class="lbl">Total Tasks</div>
        </div>""")
        col_b.html(f"""
        <div class="stat-card {tl_class}">
          <div class="val {tl_class}">{abs(time_left)}</div>
          <div class="lbl">{tl_label}</div>
        </div>""")
        col_c.html(f"""
        <div class="stat-card red">
          <div class="val red">{high_count}</div>
          <div class="lbl">High Priority</div>
        </div>""")
        col_d.html(f"""
        <div class="stat-card green">
          <div class="val green">{done_count}</div>
          <div class="lbl">Completed</div>
        </div>""")

        st.html("<div style='height:0.15rem'></div>")

        fill       = min(total / budget, 1.0) if budget else 0
        over_txt   = f'{abs(time_left)} min over budget' if time_left < 0 else f'{time_left} min remaining'
        over_color = '#ef4444' if time_left < 0 else '#10b981'
        st.html(f"""
        <div class="budget-bar-wrap">
          <div class="bar-label">
            <span>Daily Budget</span>
            <span style="color:{over_color};">{over_txt}</span>
          </div>
        </div>
        """)
        st.progress(fill)

    # Add task form
    st.html("""
    <div class="section-label">New Task</div>
    <div class="add-form-card">
      <div class="form-header">Add a Care Task</div>
    """)

    fc1, fc2, fc3, fc4 = st.columns([3, 1.5, 1.5, 1.1])
    with fc1: task_title   = st.text_input("Task",     value="Morning walk", label_visibility="collapsed", placeholder="e.g. Morning walk, Feeding, Grooming…")
    with fc2: duration     = st.number_input("Duration", min_value=1, max_value=240, value=20, label_visibility="collapsed")
    with fc3: priority_sel = st.selectbox("Priority", ["high","medium","low"], label_visibility="collapsed")
    with fc4:
        st.html("<div style='height:1.78rem'></div>")
        add_clicked = st.button("Add", use_container_width=True)
    st.html("</div>")

    if add_clicked:
        if not st.session_state.tools:
            st.warning("Save your pet profile first (sidebar).")
        else:
            st.session_state.tools.schedule.add_task(
                Task(task_type=task_title, duration_minutes=int(duration), priority=PRIORITY_MAP[priority_sel])
            )
            st.rerun()

    # Task list
    st.html('<div class="section-label">Task List</div>')

    if s and s.tasks:
        for i, task in enumerate(s.tasks):
            p_color    = PRIORITY_COLOR.get(task.priority, "#94a3b8")
            p_label    = PRIORITY_LABEL.get(task.priority, str(task.priority))
            p_badge    = PRIORITY_BADGE.get(task.priority, "")
            done_cls   = "done-card" if task.is_completed else ""
            icon       = task_icon(task.task_type)
            notes_text = task.notes if task.notes else "No notes"

            left, right = st.columns([10, 1])
            with left:
                st.html(f"""
                <div class="task-card {done_cls}">
                  <div class="priority-bar" style="background:{p_color};"></div>
                  <div class="task-icon">{icon}</div>
                  <div style="flex:1;min-width:0;">
                    <div class="name">{task.task_type}</div>
                    <div class="meta">{task.duration_minutes} min · {notes_text}</div>
                  </div>
                  <div class="right">
                    <span class="badge {p_badge}">{p_label}</span>
                  </div>
                </div>
                """)
            with right:
                if not task.is_completed:
                    if st.button("✓", key=f"done_{i}", help="Mark complete"):
                        task.complete()
                        st.rerun()
                else:
                    st.button("✓", key=f"undo_{i}", disabled=True)
    else:
        st.html("""
        <div class="empty-state">
          <span class="paw-icon">🐾</span>
          <div class="etitle">No tasks yet</div>
          <p class="esub">Add your first pet care task above to get started.</p>
        </div>
        """)

# ── TAB 2 — Schedule ──────────────────────────────────────────────────────────
with tab_schedule:
    s = sched()

    gen_col, _ = st.columns([2.5, 5])
    with gen_col:
        generate = st.button("Generate Schedule", use_container_width=True)

    if generate:
        if not s:
            st.warning("Save your pet profile first (sidebar).")
        elif not s.tasks:
            st.warning("Add at least one task in the Tasks tab first.")
        else:
            conflicts = s.check_conflicts()
            for c in conflicts:
                st.warning(c)
            if not conflicts:
                st.success("No conflicts — your schedule looks great!")
            st.session_state.last_plan = s.generate_plan()

    plan = getattr(st.session_state, "last_plan", None)

    if plan and s:
        total  = s.get_total_duration()
        budget = s.owner.available_minutes

        budget_class = "red" if total > budget else "green"
        m1, m2, m3 = st.columns(3)
        m1.html(f"""
        <div class="stat-card blue">
          <div class="val blue">{len(plan)}</div>
          <div class="lbl">Scheduled</div>
        </div>""")
        m2.html(f"""
        <div class="stat-card sky">
          <div class="val sky">{total}</div>
          <div class="lbl">Total Min</div>
        </div>""")
        m3.html(f"""
        <div class="stat-card {budget_class}">
          <div class="val {budget_class}">{budget}</div>
          <div class="lbl">Budget Min</div>
        </div>""")

        st.html("<div style='height:0.5rem'></div>")

        if total > budget:
            st.error(f"Schedule is **{total - budget} min over budget** — consider removing lower-priority tasks.")
        else:
            st.success(f"Schedule fits within budget with **{budget - total} min to spare!**")

        st.html('<div class="section-label">Today\'s Plan</div>')

        for i, task in enumerate(plan):
            p_label = PRIORITY_LABEL.get(task.priority, str(task.priority))
            p_badge = PRIORITY_BADGE.get(task.priority, "")
            icon    = task_icon(task.task_type)

            st.html(f"""
            <div class="timeline-item">
              <div class="timeline-dot">{i+1}</div>
              <div class="timeline-card">
                <div class="ticon">{icon}</div>
                <div style="flex:1;min-width:0;">
                  <div class="tname">{task.task_type}</div>
                  <div class="tmeta">{task.duration_minutes} min · Priority {task.priority}/10</div>
                </div>
                <div class="tright">
                  <span class="badge {p_badge}">{p_label}</span>
                </div>
              </div>
            </div>
            """)
    else:
        st.html("""
        <div class="empty-state">
          <span class="paw-icon">🐾</span>
          <div class="etitle">No schedule yet</div>
          <p class="esub">Hit <strong>Generate Schedule</strong> to build your optimised daily plan.</p>
        </div>
        """)

# ── TAB 3 — AI Assistant ──────────────────────────────────────────────────────
with tab_ai:
    has_key = bool(os.environ.get("GROQ_API_KEY"))

    if not has_key:
        st.html("""
        <div class="empty-state">
          <span class="paw-icon">🐾</span>
          <div class="etitle">API Key Required</div>
          <p class="esub">Add <code>GROQ_API_KEY=your_key</code> to your <code>.env</code> file to enable the AI assistant.</p>
        </div>
        """)
    elif not st.session_state.tools:
        st.html("""
        <div class="empty-state">
          <span class="paw-icon">🐾</span>
          <div class="etitle">Profile Required</div>
          <p class="esub">Save your pet profile in the sidebar to activate the AI assistant.</p>
        </div>
        """)
    else:
        if st.session_state.agent is None:
            try:
                from agent.scheduler_agent import SchedulerAgent
                st.session_state.agent = SchedulerAgent(tools_instance=st.session_state.tools)
            except Exception as exc:
                st.error(f"Could not start AI agent: {exc}")

        agent = st.session_state.agent
        if agent:
            if not st.session_state.chat_history:
                st.html("""
                <div class="section-label">Try asking</div>
                <div class="chip-row">
                  <span class="prompt-chip">Add a 30-min walk at high priority</span>
                  <span class="prompt-chip">Build me a full day schedule</span>
                  <span class="prompt-chip">Check for conflicts</span>
                  <span class="prompt-chip">What tasks are left?</span>
                  <span class="prompt-chip">Add a feeding task</span>
                </div>
                """)

            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            user_input = st.chat_input(f"Ask PawPal+ about {pet_name}'s schedule…")

            if user_input:
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    st.markdown(user_input)

                with st.chat_message("assistant"):
                    with st.spinner("Thinking…"):
                        try:
                            reply = agent.run(user_input)
                        except Exception as exc:
                            reply = f"Sorry, something went wrong: {exc}"
                    st.markdown(reply)
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})

                st.rerun()

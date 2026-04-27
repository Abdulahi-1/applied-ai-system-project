import os
import streamlit as st
from dotenv import load_dotenv

from models.schemas import Task
from agent.tools import SchedulerTools

load_dotenv()

# ── page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PawPal+",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
#MainMenu, footer, header { visibility: hidden; }

/* ── sidebar ─────────────────────────────────────────────── */
[data-testid="stSidebar"] > div:first-child {
    background: linear-gradient(175deg, #1a1040 0%, #2d1b69 50%, #1e3a5f 100%);
    padding-top: 0;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div { color: rgba(255,255,255,0.9) !important; }
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stNumberInput input {
    background: rgba(255,255,255,0.10) !important;
    border: 1px solid rgba(255,255,255,0.20) !important;
    border-radius: 10px !important;
    color: white !important;
    caret-color: white !important;
    -webkit-text-fill-color: white !important;
    padding: 0.55rem 0.9rem !important;
}
[data-testid="stSidebar"] .stTextInput input::placeholder { color: rgba(255,255,255,0.45) !important; }
[data-testid="stSidebar"] .stNumberInput input { -webkit-text-fill-color: white !important; }
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.10) !important;
    border: 1px solid rgba(255,255,255,0.20) !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] .stSlider > div { padding: 0 !important; }
[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%) !important;
    border: none !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.75rem 1rem !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.45) !important;
    transition: all 0.2s !important;
    letter-spacing: 0.01em !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    box-shadow: 0 6px 25px rgba(124,58,237,0.6) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.12) !important;
    margin: 1rem 0 !important;
}

/* ── main layout ─────────────────────────────────────────── */
.main .block-container { padding: 1.5rem 2rem 4rem; max-width: 1000px; }

/* ── tabs ────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #f1f5f9;
    border-radius: 14px;
    padding: 5px;
    gap: 4px;
    border: none;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    padding: 0.55rem 1.4rem !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    color: #64748b !important;
    background: transparent !important;
    border: none !important;
    transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #4f46e5 !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.10) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }

/* ── form inputs ─────────────────────────────────────────── */
.stTextInput input, .stNumberInput input {
    border-radius: 11px !important;
    border: 1.5px solid #e2e8f0 !important;
    padding: 0.6rem 0.9rem !important;
    font-size: 0.93rem !important;
    background: white !important;
    color: #1e293b !important;
    caret-color: #6366f1 !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
    background: white !important;
}
.stSelectbox > div > div {
    border-radius: 11px !important;
    border: 1.5px solid #e2e8f0 !important;
    background: white !important;
    color: #1e293b !important;
}

/* ── buttons (main) ──────────────────────────────────────── */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    transition: all 0.2s !important;
    border: 1.5px solid #e2e8f0 !important;
    background: white !important;
    color: #334155 !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.10) !important;
    border-color: #c7d2fe !important;
}

/* ── progress bar ────────────────────────────────────────── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #6366f1, #a78bfa) !important;
    border-radius: 100px !important;
}
.stProgress > div > div {
    background: #e2e8f0 !important;
    border-radius: 100px !important;
}

/* ── alerts ──────────────────────────────────────────────── */
.stSuccess { border-radius: 12px !important; }
.stWarning { border-radius: 12px !important; }
.stError   { border-radius: 12px !important; }
.stInfo    { border-radius: 12px !important; }

/* ── chat ────────────────────────────────────────────────── */
[data-testid="stChatInput"] textarea {
    border-radius: 14px !important;
    border: 1.5px solid #e2e8f0 !important;
    background: #fafbff !important;
    font-size: 0.93rem !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
}

/* ── custom component styles ─────────────────────────────── */
.paw-hero {
    background: linear-gradient(135deg, #1a1040 0%, #2d1b69 40%, #1e3a5f 100%);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    color: white;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    margin-bottom: 1.75rem;
    box-shadow: 0 8px 32px rgba(79,70,229,0.25);
}
.paw-hero .emoji-bubble {
    width: 72px; height: 72px;
    background: rgba(255,255,255,0.14);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 2.2rem;
    flex-shrink: 0;
    backdrop-filter: blur(4px);
}
.paw-hero h2 { margin: 0; font-size: 1.65rem; font-weight: 800; letter-spacing: -0.02em; }
.paw-hero p  { margin: 0.25rem 0 0; opacity: 0.75; font-size: 0.92rem; }
.paw-hero .pill {
    display: inline-block;
    background: rgba(255,255,255,0.18);
    border-radius: 100px;
    padding: 3px 12px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-top: 0.5rem;
    letter-spacing: 0.03em;
}

.stat-row { display: flex; gap: 1rem; margin-bottom: 1.25rem; }
.stat-card {
    flex: 1;
    background: white;
    border-radius: 16px;
    padding: 1.1rem 1.25rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    text-align: center;
}
.stat-card .val { font-size: 1.9rem; font-weight: 800; color: #1e293b; line-height: 1; }
.stat-card .lbl { font-size: 0.73rem; color: #94a3b8; margin-top: 0.3rem; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; }
.stat-card .val.red   { color: #ef4444; }
.stat-card .val.green { color: #10b981; }
.stat-card .val.blue  { color: #6366f1; }

.section-title {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #94a3b8;
    margin: 1.5rem 0 0.75rem;
}

.task-card {
    background: white;
    border-radius: 14px;
    padding: 0.9rem 1.1rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.5rem;
    transition: box-shadow 0.2s;
}
.task-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
.task-card .dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
}
.task-card .name { font-weight: 600; font-size: 0.95rem; color: #1e293b; }
.task-card .meta { font-size: 0.8rem; color: #94a3b8; margin-top: 1px; }
.task-card .badge {
    margin-left: auto;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 100px;
    flex-shrink: 0;
    letter-spacing: 0.03em;
}
.badge-high   { background: #fee2e2; color: #b91c1c; }
.badge-medium { background: #fef3c7; color: #92400e; }
.badge-low    { background: #d1fae5; color: #065f46; }
.done-card { opacity: 0.45; }

.timeline-item {
    display: flex;
    gap: 1rem;
    margin-bottom: 0.75rem;
    align-items: flex-start;
}
.timeline-dot {
    width: 36px; height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6366f1, #a78bfa);
    color: white;
    font-weight: 700;
    font-size: 0.85rem;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(99,102,241,0.35);
    margin-top: 2px;
}
.timeline-card {
    flex: 1;
    background: white;
    border-radius: 14px;
    padding: 0.85rem 1.1rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.timeline-card .tname { font-weight: 600; color: #1e293b; font-size: 0.95rem; }
.timeline-card .tmeta { font-size: 0.8rem; color: #94a3b8; margin-top: 2px; }

.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #94a3b8;
}
.empty-state .icon { font-size: 3rem; margin-bottom: 0.75rem; }
.empty-state p { font-size: 0.95rem; margin: 0; }

.add-form-card {
    background: #fafbff;
    border: 1.5px dashed #c7d2fe;
    border-radius: 16px;
    padding: 1.25rem 1.5rem 0.5rem;
    margin-bottom: 1.25rem;
}

.budget-bar-wrap {
    background: white;
    border-radius: 14px;
    padding: 1rem 1.25rem;
    border: 1px solid #e2e8f0;
    margin-bottom: 1rem;
}
.budget-bar-wrap .bar-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
    font-weight: 600;
    color: #64748b;
    margin-bottom: 0.5rem;
}

.prompt-chip {
    display: inline-block;
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 100px;
    padding: 5px 14px;
    font-size: 0.8rem;
    color: #475569;
    cursor: pointer;
    margin: 3px;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# ── constants ──────────────────────────────────────────────────────────────────
PRIORITY_MAP = {"low": 3, "medium": 6, "high": 9}
PRIORITY_LABEL = {3: "Low", 6: "Medium", 9: "High"}
PRIORITY_COLOR = {3: "#10b981", 6: "#f59e0b", 9: "#ef4444"}
PRIORITY_BADGE = {3: "badge-low", 6: "badge-medium", 9: "badge-high"}
SPECIES_EMOJI = {"dog": "🐕", "cat": "🐈", "other": "🐾"}

# ── session state ──────────────────────────────────────────────────────────────
if "tools"         not in st.session_state: st.session_state.tools = None
if "agent"         not in st.session_state: st.session_state.agent = None
if "chat_history"  not in st.session_state: st.session_state.chat_history = []

def sched():
    return st.session_state.tools.schedule if st.session_state.tools else None

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — pet profile
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1.75rem 0 1.25rem;">
        <div style="font-size:2.6rem; margin-bottom:0.35rem;">🐾</div>
        <div style="font-size:1.5rem; font-weight:800; color:white; letter-spacing:-0.02em;">PawPal<span style="color:#a78bfa;">+</span></div>
        <div style="font-size:0.78rem; color:rgba(255,255,255,0.5); margin-top:3px; letter-spacing:0.04em;">SMART PET CARE SCHEDULING</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:rgba(255,255,255,0.4);margin-bottom:0.6rem;">Owner</div>', unsafe_allow_html=True)

    owner_name        = st.text_input("Your name",            value="Jordan",  label_visibility="collapsed", placeholder="Your name")
    available_minutes = st.number_input("Daily time (min)",   min_value=10, max_value=480, value=120, label_visibility="collapsed")

    st.markdown('<div style="font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:rgba(255,255,255,0.4);margin:0.9rem 0 0.6rem;">Pet Profile</div>', unsafe_allow_html=True)

    pet_name = st.text_input("Pet name",  value="Mochi",   label_visibility="collapsed", placeholder="Pet name")
    breed    = st.text_input("Breed",     value="Mixed",   label_visibility="collapsed", placeholder="Breed")

    c1, c2 = st.columns(2)
    with c1: size    = st.selectbox("Size",    ["small","medium","large"],         label_visibility="collapsed")
    with c2: species = st.selectbox("Species", ["dog","cat","other"],              label_visibility="collapsed")
    age = st.number_input("Age (years)", min_value=0, max_value=30, value=2,       label_visibility="collapsed")

    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

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
        st.success(f"Profile saved!")

    if st.session_state.tools:
        s = sched()
        st.markdown('<hr>', unsafe_allow_html=True)
        total = s.get_total_duration()
        budget = s.owner.available_minutes
        pct = min(int(total / budget * 100), 100) if budget else 0
        remaining = max(budget - total, 0)
        over = max(total - budget, 0)

        st.markdown(f"""
        <div style="padding:0 0.25rem;">
          <div style="font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:rgba(255,255,255,0.4);margin-bottom:0.75rem;">Today's Snapshot</div>
          <div style="display:flex;gap:0.6rem;margin-bottom:0.75rem;">
            <div style="flex:1;background:rgba(255,255,255,0.08);border-radius:10px;padding:0.7rem;text-align:center;">
              <div style="font-size:1.4rem;font-weight:800;">{len(s.tasks)}</div>
              <div style="font-size:0.68rem;opacity:0.5;text-transform:uppercase;letter-spacing:0.05em;">Tasks</div>
            </div>
            <div style="flex:1;background:rgba(255,255,255,0.08);border-radius:10px;padding:0.7rem;text-align:center;">
              <div style="font-size:1.4rem;font-weight:800;">{total}</div>
              <div style="font-size:0.68rem;opacity:0.5;text-transform:uppercase;letter-spacing:0.05em;">Min</div>
            </div>
          </div>
          <div style="background:rgba(255,255,255,0.08);border-radius:8px;height:6px;overflow:hidden;margin-bottom:0.4rem;">
            <div style="height:100%;width:{pct}%;background:linear-gradient(90deg,#818cf8,#a78bfa);border-radius:8px;transition:width 0.3s;"></div>
          </div>
          <div style="font-size:0.72rem;opacity:0.55;text-align:right;">
            {"⚠️ " + str(over) + " min over" if over else "✓ " + str(remaining) + " min left"}
          </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN — hero banner
# ══════════════════════════════════════════════════════════════════════════════

if st.session_state.tools:
    s = sched()
    emoji = SPECIES_EMOJI.get(species, "🐾")
    completed = sum(1 for t in s.tasks if t.is_completed)
    st.markdown(f"""
    <div class="paw-hero">
      <div class="emoji-bubble">{emoji}</div>
      <div>
        <h2>Hey {s.owner.name}! 👋</h2>
        <p>{s.pet.name} · {s.pet.breed} · {s.pet.age_years}yr</p>
        <span class="pill">{'✅ ' + str(completed) + ' done · ' if completed else ''}{len(s.tasks)} task{'s' if len(s.tasks) != 1 else ''} today</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="paw-hero">
      <div class="emoji-bubble">🐾</div>
      <div>
        <h2>Welcome to PawPal+</h2>
        <p>Fill in the profile on the left to get started.</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════

tab_tasks, tab_schedule, tab_ai = st.tabs(["📋  Tasks", "📅  Schedule", "🤖  AI Assistant"])

# ── TAB 1 — Tasks ─────────────────────────────────────────────────────────────
with tab_tasks:
    s = sched()

    # Stats row
    if s:
        total      = s.get_total_duration()
        budget     = s.owner.available_minutes
        time_left  = budget - total
        high_count = sum(1 for t in s.tasks if t.is_high_priority())
        done_count = sum(1 for t in s.tasks if t.is_completed)

        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.markdown(f'<div class="stat-card"><div class="val blue">{len(s.tasks)}</div><div class="lbl">Tasks</div></div>', unsafe_allow_html=True)
        col_b.markdown(f'<div class="stat-card"><div class="val">{total}</div><div class="lbl">Minutes</div></div>', unsafe_allow_html=True)
        col_c.markdown(f'<div class="stat-card"><div class="val {"red" if time_left < 0 else "green"}">{abs(time_left)}</div><div class="lbl">{"Over" if time_left < 0 else "Remaining"}</div></div>', unsafe_allow_html=True)
        col_d.markdown(f'<div class="stat-card"><div class="val">{done_count}</div><div class="lbl">Done</div></div>', unsafe_allow_html=True)

        st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

        # Budget bar
        fill = min(total / budget, 1.0) if budget else 0
        bar_color = "#ef4444" if time_left < 0 else "#6366f1"
        st.markdown(f"""
        <div class="budget-bar-wrap">
          <div class="bar-label">
            <span>⏱ Daily Budget</span>
            <span>{total} / {budget} min</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(fill)

    # Add task form
    st.markdown('<div class="section-title">Add New Task</div>', unsafe_allow_html=True)
    st.markdown('<div class="add-form-card">', unsafe_allow_html=True)
    fc1, fc2, fc3, fc4 = st.columns([3, 1.5, 1.5, 1])
    with fc1: task_title    = st.text_input("Task", value="Morning walk", label_visibility="collapsed", placeholder="Task name")
    with fc2: duration      = st.number_input("Duration", min_value=1, max_value=240, value=20, label_visibility="collapsed")
    with fc3: priority_sel  = st.selectbox("Priority", ["high","medium","low"], label_visibility="collapsed")
    with fc4:
        st.markdown("<div style='height:1.78rem'></div>", unsafe_allow_html=True)
        add_clicked = st.button("＋ Add", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if add_clicked:
        if not st.session_state.tools:
            st.warning("Save your profile first.")
        else:
            st.session_state.tools.schedule.add_task(
                Task(task_type=task_title, duration_minutes=int(duration), priority=PRIORITY_MAP[priority_sel])
            )
            st.rerun()

    # Task list
    st.markdown('<div class="section-title">Task List</div>', unsafe_allow_html=True)

    if s and s.tasks:
        for i, task in enumerate(s.tasks):
            p_color = PRIORITY_COLOR.get(task.priority, "#94a3b8")
            p_label = PRIORITY_LABEL.get(task.priority, str(task.priority))
            p_badge = PRIORITY_BADGE.get(task.priority, "")
            done_cls = "done-card" if task.is_completed else ""
            status_icon = "✅" if task.is_completed else "⏳"

            left, right = st.columns([10, 1])
            with left:
                st.markdown(f"""
                <div class="task-card {done_cls}">
                  <div class="dot" style="background:{p_color};"></div>
                  <div>
                    <div class="name">{status_icon} {task.task_type}</div>
                    <div class="meta">⏱ {task.duration_minutes} min · {'Notes: ' + task.notes if task.notes else 'No notes'}</div>
                  </div>
                  <span class="badge {p_badge}">{p_label}</span>
                </div>
                """, unsafe_allow_html=True)
            with right:
                if not task.is_completed:
                    if st.button("✓", key=f"done_{i}", help="Mark done"):
                        task.complete()
                        st.rerun()
                else:
                    st.button("↩", key=f"undo_{i}", help="Undo", disabled=True)
    else:
        st.markdown("""
        <div class="empty-state">
          <div class="icon">🦴</div>
          <p>No tasks yet — add one above!</p>
        </div>
        """, unsafe_allow_html=True)

# ── TAB 2 — Schedule ──────────────────────────────────────────────────────────
with tab_schedule:
    s = sched()

    gen_col, _ = st.columns([2, 5])
    with gen_col:
        generate = st.button("⚡ Generate Schedule", use_container_width=True)

    if generate:
        if not s:
            st.warning("Save your profile first.")
        elif not s.tasks:
            st.warning("Add at least one task first.")
        else:
            conflicts = s.check_conflicts()
            for c in conflicts:
                st.warning(c)
            if not conflicts:
                st.success("No conflicts — good to go!")
            st.session_state.last_plan = s.generate_plan()

    plan = getattr(st.session_state, "last_plan", None)

    if plan and s:
        total = s.get_total_duration()
        budget = s.owner.available_minutes

        m1, m2, m3 = st.columns(3)
        m1.markdown(f'<div class="stat-card"><div class="val blue">{len(plan)}</div><div class="lbl">Scheduled</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="stat-card"><div class="val">{total}</div><div class="lbl">Total min</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="stat-card"><div class="val {"red" if total > budget else "green"}">{budget}</div><div class="lbl">Budget min</div></div>', unsafe_allow_html=True)

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        if total > budget:
            st.error(f"Schedule is {total - budget} min over budget.")
        else:
            st.success(f"Fits within budget — {budget - total} min to spare.")

        st.markdown('<div class="section-title">Today\'s Plan</div>', unsafe_allow_html=True)

        for i, task in enumerate(plan):
            p_color = PRIORITY_COLOR.get(task.priority, "#94a3b8")
            p_label = PRIORITY_LABEL.get(task.priority, str(task.priority))
            p_badge = PRIORITY_BADGE.get(task.priority, "")

            st.markdown(f"""
            <div class="timeline-item">
              <div class="timeline-dot">{i+1}</div>
              <div class="timeline-card">
                <div style="display:flex;align-items:center;justify-content:space-between;">
                  <div class="tname">{task.task_type}</div>
                  <span class="badge {p_badge}" style="margin-left:auto;">{p_label}</span>
                </div>
                <div class="tmeta">⏱ {task.duration_minutes} min · Priority {task.priority}/10</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
          <div class="icon">📅</div>
          <p>Hit <strong>Generate Schedule</strong> to build your day.</p>
        </div>
        """, unsafe_allow_html=True)

# ── TAB 3 — AI Assistant ──────────────────────────────────────────────────────
with tab_ai:
    has_key = bool(os.environ.get("GEMINI_API_KEY"))

    if not has_key:
        st.markdown("""
        <div class="empty-state">
          <div class="icon">🔑</div>
          <p>Add <code>GEMINI_API_KEY=your_key</code> to <code>.env</code> to enable AI.</p>
        </div>
        """, unsafe_allow_html=True)
    elif not st.session_state.tools:
        st.markdown("""
        <div class="empty-state">
          <div class="icon">🤖</div>
          <p>Save your pet profile (sidebar) to activate the AI assistant.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Lazy-init agent (shares SchedulerTools state with the manual UI)
        if st.session_state.agent is None:
            try:
                from agent.scheduler_agent import SchedulerAgent
                st.session_state.agent = SchedulerAgent(tools_instance=st.session_state.tools)
            except Exception as exc:
                st.error(f"Could not start AI agent: {exc}")

        agent = st.session_state.agent
        if agent:
            # Suggested prompts (click to fill)
            if not st.session_state.chat_history:
                st.markdown("""
                <div style="margin-bottom:1rem;">
                  <div class="section-title">Try asking…</div>
                  <span class="prompt-chip">Add a 30-min walk at high priority</span>
                  <span class="prompt-chip">Build me a full day schedule</span>
                  <span class="prompt-chip">Check for conflicts</span>
                  <span class="prompt-chip">What tasks are left?</span>
                </div>
                """, unsafe_allow_html=True)

            # Chat history
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            user_input = st.chat_input("Ask PawPal+ anything about your schedule…")

            if user_input:
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    st.markdown(user_input)

                with st.chat_message("assistant"):
                    with st.spinner("PawPal+ is thinking…"):
                        try:
                            reply = agent.run(user_input)
                        except Exception as exc:
                            reply = f"Sorry, something went wrong: {exc}"
                    st.markdown(reply)
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})

                st.rerun()

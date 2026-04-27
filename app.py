"""
SME AI Adoption Advisor — v4
============================
3-step wizard. API key hardcoded in backend (ANTHROPIC_API_KEY env var or constant).
Clean light UI — no dark theme, minimal clutter.
"""

import json
import os
import tempfile

import streamlit as st
import streamlit.components.v1 as components
import matplotlib
matplotlib.use("Agg")
from anthropic import Anthropic

from questionnaires import INDUSTRY_QUESTIONNAIRES, COMMON_QUESTIONS
from prompts import build_system_prompt, build_user_prompt
from pdf_generator import generate_pdf
from pricing import collect_all_pricing, format_pricing_for_prompt

# ── API key — set here or via ANTHROPIC_API_KEY environment variable ──
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ── Page config ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SME AI Advisor · DFW Technologies",
    page_icon="🤖",
    layout="centered",
)

# ── CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  background: #f0f4f8 !important;
  color: #1e293b;
}

.block-container {
  max-width: 860px !important;
  padding: 2.5rem 2rem 6rem !important;
  background: transparent !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ── Hero ── */
.hero {
  background: linear-gradient(140deg, #0f2044 0%, #163560 45%, #0c6e8a 100%);
  border-radius: 18px;
  padding: 2.8rem 3.2rem 2.6rem;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
  box-shadow: 0 12px 40px rgba(15,32,68,0.22);
}
.hero::before {
  content: '';
  position: absolute; top: -80px; right: -50px;
  width: 320px; height: 320px;
  background: radial-gradient(circle, rgba(12,110,138,0.5) 0%, transparent 60%);
  border-radius: 50%;
}
.hero-eyebrow {
  font-size: 0.7rem; font-weight: 600; letter-spacing: 0.2em;
  text-transform: uppercase; color: #5eead4;
  margin-bottom: 1rem; position: relative;
}
.hero h1 {
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-weight: 800 !important; font-size: 2.5rem !important;
  color: #ffffff !important; margin: 0 0 0.9rem 0 !important;
  line-height: 1.15 !important; letter-spacing: -0.01em !important;
  position: relative;
}
.hero-desc {
  color: rgba(255,255,255,0.6); font-size: 0.96rem;
  font-weight: 400; max-width: 500px; line-height: 1.65;
  position: relative;
}
.hero-badges {
  display: flex; gap: 8px; margin-top: 1.8rem; flex-wrap: wrap;
  position: relative;
}
.hero-badge {
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 100px; padding: 5px 15px;
  font-size: 0.74rem; font-weight: 600; color: rgba(255,255,255,0.7);
  letter-spacing: 0.02em;
}

/* ── Stepper ── */
.stepper {
  display: flex; align-items: center;
  background: #ffffff; border-radius: 12px;
  padding: 1rem 1.8rem; margin-bottom: 2rem;
  box-shadow: 0 1px 6px rgba(0,0,0,0.06);
  border: 1px solid #e2e8f0;
}
.step-item { display: flex; align-items: center; gap: 9px; }
.step-dot {
  width: 28px; height: 28px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 0.76rem; transition: all 0.2s;
}
.step-dot.done   { background: #0891b2; color: #fff; }
.step-dot.active { background: #0f2044; color: #fff; box-shadow: 0 0 0 3px rgba(15,32,68,0.15); }
.step-dot.idle   { background: #e2e8f0; color: #94a3b8; }
.step-label { font-size: 0.8rem; font-weight: 500; color: #94a3b8; white-space: nowrap; }
.step-label.active { color: #0f2044; font-weight: 700; }
.step-connector { flex: 1; height: 1.5px; background: #e2e8f0; margin: 0 10px; min-width: 20px; }
.step-connector.done { background: #0891b2; }

/* ── Industry grid ── */
.ind-card {
  background: #fff; border: 1.5px solid #e2e8f0; border-radius: 12px;
  padding: 1.4rem 1.1rem; text-align: center; cursor: pointer;
  transition: all 0.16s; box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  margin-bottom: 0.8rem;
}
.ind-card:hover {
  border-color: #0891b2; box-shadow: 0 6px 20px rgba(8,145,178,0.1);
  transform: translateY(-2px);
}
.ind-icon { font-size: 1.9rem; margin-bottom: 0.5rem; }
.ind-name { font-size: 0.85rem; font-weight: 700; color: #0f2044; line-height: 1.3; }
.ind-desc { font-size: 0.72rem; color: #94a3b8; margin-top: 0.3rem; line-height: 1.4; }

/* ── Page section heading ── */
.sec-heading {
  font-weight: 700; font-size: 1.2rem;
  color: #f1f5f9 !important; margin: 0 0 0.3rem 0; letter-spacing: -0.01em;
}
.sec-sub { font-size: 0.875rem; color: #94a3b8 !important; margin-bottom: 1.4rem; line-height: 1.6; }

/* ── Section label above question groups ── */
.q-section-label {
  font-size: 0.72rem; font-weight: 700; letter-spacing: 0.1em;
  text-transform: uppercase; color: #67e8f9 !important;
  margin: 1.8rem 0 0.5rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid rgba(103,232,249,0.25);
  display: block;
}

/* ── Streamlit widget overrides ── */
div[data-testid="stSelectbox"] > label,
div[data-testid="stMultiSelect"] > label,
div[data-testid="stSlider"] > label,
div[data-testid="stRadio"] > label,
div[data-testid="stTextInput"] > label,
div[data-testid="stTextArea"] > label {
  font-size: 0.9rem !important; font-weight: 600 !important;
  color: #1e293b !important;
}

/* ── Submit button ── */
div[data-testid="stFormSubmitButton"] > button {
  background: linear-gradient(135deg, #0f2044 0%, #0891b2 100%) !important;
  color: #ffffff !important; border: none !important;
  border-radius: 10px !important; padding: 0.85rem 2rem !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-weight: 700 !important; font-size: 0.95rem !important;
  width: 100% !important; transition: opacity 0.2s !important;
  box-shadow: 0 4px 16px rgba(8,145,178,0.28) !important;
}
div[data-testid="stFormSubmitButton"] > button:hover { opacity: 0.88 !important; }

/* ── Back / secondary buttons ── */
div[data-testid="stButton"] > button {
  border-radius: 8px !important; font-size: 0.85rem !important; font-weight: 600 !important;
  border: 1.5px solid #cbd5e1 !important; color: #334155 !important;
  background: #ffffff !important; padding: 0.45rem 1.1rem !important;
}
div[data-testid="stButton"] > button:hover {
  border-color: #0891b2 !important; color: #0891b2 !important; background: #f0fdff !important;
}

/* ── How it works card ── */
.how-card {
  background: #fff; border: 1px solid #e8eef4; border-radius: 14px;
  padding: 1.4rem 1.8rem; margin-top: 1.8rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.how-title {
  font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em;
  text-transform: uppercase; color: #0e7490; margin-bottom: 0.8rem;
}
.how-steps { display: flex; gap: 0; }
.how-step {
  flex: 1; text-align: center; padding: 0 0.8rem;
  border-right: 1px solid #e8eef4;
}
.how-step:last-child { border-right: none; }
.how-step-num {
  width: 28px; height: 28px; background: #0e7490; border-radius: 50%;
  color: #fff; font-weight: 700; font-size: 0.78rem;
  display: flex; align-items: center; justify-content: center; margin: 0 auto 0.5rem;
}
.how-step-text { font-size: 0.8rem; color: #475569; line-height: 1.4; }

/* ── Progress page ── */
.gen-card {
  background: #fff; border-radius: 16px; padding: 2.5rem 2.5rem 2rem;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1px solid #e8eef4;
  text-align: center;
}
.gen-spinner { font-size: 2.8rem; margin-bottom: 1rem; animation: spin 2s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Report ready ── */
.report-card {
  background: linear-gradient(135deg, #f0fdf9 0%, #ecfdf5 100%);
  border: 2px solid #10b981; border-radius: 18px;
  padding: 2.4rem 2.8rem; text-align: center;
  box-shadow: 0 4px 20px rgba(16,185,129,0.12);
}
.report-card-icon { font-size: 3rem; margin-bottom: 0.8rem; }
.report-card h2 {
  font-family: 'Syne', sans-serif !important; font-weight: 800 !important;
  font-size: 1.6rem !important; color: #064e3b !important; margin-bottom: 0.3rem !important;
}
.report-card-sub { color: #065f46; font-size: 0.9rem; margin-bottom: 0; }
.report-card strong { color: #047857; }

/* ── Download button ── */
div[data-testid="stDownloadButton"] > button {
  background: linear-gradient(135deg, #059669 0%, #0d9488 100%) !important;
  color: #fff !important; border: none !important; border-radius: 10px !important;
  padding: 0.8rem 1.5rem !important; font-weight: 600 !important;
  font-size: 0.95rem !important;
  box-shadow: 0 4px 14px rgba(5,150,105,0.3) !important;
}

/* ── Error card ── */
.err-card {
  background: #fff5f5; border: 1.5px solid #feb2b2; border-radius: 12px;
  padding: 1.4rem 1.6rem;
}
</style>
""", unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────
DEFAULTS = {
    "step": 1, "industry": None,
    "common_answers": {}, "industry_answers": {}, "extra_context": "",
    "pdf_bytes": None, "rec_plan_name": "", "error": None,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Hero (full iframe for reliable font + animation rendering) ──────────
components.html("""
<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background: transparent; font-family: 'Plus Jakarta Sans', sans-serif; }

  .hero {
    background: linear-gradient(140deg, #0a1628 0%, #12305a 50%, #0b6882 100%);
    border-radius: 18px;
    padding: 2.6rem 3.2rem 2.4rem;
    position: relative; overflow: hidden;
    box-shadow: 0 12px 48px rgba(10,22,40,0.35);
  }
  .hero::before {
    content: '';
    position: absolute; top: -80px; right: -60px;
    width: 340px; height: 340px;
    background: radial-gradient(circle, rgba(11,104,130,0.55) 0%, transparent 60%);
    border-radius: 50%;
    animation: pulse 4s ease-in-out infinite;
  }
  .hero::after {
    content: '';
    position: absolute; bottom: -50px; left: 15%;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(94,234,212,0.12) 0%, transparent 65%);
    border-radius: 50%;
    animation: pulse 5s ease-in-out infinite reverse;
  }
  @keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50%       { transform: scale(1.08); opacity: 0.75; }
  }

  .eyebrow {
    font-size: 0.68rem; font-weight: 600; letter-spacing: 0.22em;
    text-transform: uppercase; color: #5eead4;
    margin-bottom: 1rem; position: relative;
    opacity: 0; animation: fadeUp 0.6s ease 0.1s forwards;
  }
  .title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 2.6rem; font-weight: 800; color: #ffffff;
    line-height: 1.12; letter-spacing: -0.02em;
    margin-bottom: 0.9rem; position: relative;
    opacity: 0; animation: fadeUp 0.7s ease 0.25s forwards;
  }
  .title span { color: #67e8f9; }
  .desc {
    color: rgba(255,255,255,0.58); font-size: 0.97rem;
    font-weight: 400; max-width: 520px; line-height: 1.68;
    position: relative;
    opacity: 0; animation: fadeUp 0.7s ease 0.4s forwards;
  }
  .badges {
    display: flex; gap: 8px; margin-top: 1.8rem; flex-wrap: wrap;
    position: relative;
    opacity: 0; animation: fadeUp 0.7s ease 0.55s forwards;
  }
  .badge {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.16);
    border-radius: 100px; padding: 5px 15px;
    font-size: 0.73rem; font-weight: 600;
    color: rgba(255,255,255,0.72); letter-spacing: 0.02em;
    transition: background 0.2s, border-color 0.2s;
  }
  .badge:hover {
    background: rgba(255,255,255,0.15);
    border-color: rgba(255,255,255,0.3);
  }
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
  }
</style>
</head>
<body>
<div class="hero">
  <div class="eyebrow">DFW Technologies × UT Dallas &nbsp;·&nbsp; BUAN 6390.502</div>
  <div class="title">SME <span>AI</span> Adoption Advisor</div>
  <div class="desc">Get a tailored AI adoption roadmap — Public, Hybrid, or Private — grounded in live cloud pricing and built for your industry.</div>
  <div class="badges">
    <span class="badge">☁️ Public AI</span>
    <span class="badge">⚡ Hybrid</span>
    <span class="badge">🔒 Private AI</span>
    <span class="badge">📄 PDF Report</span>
  </div>
</div>
</body>
</html>
""", height=260, scrolling=False)


# ── Stepper ────────────────────────────────────────────────────────────
def render_stepper(current: int):
    steps = ["Select Industry", "Answer Questions", "Your Report"]
    parts = []
    for i, label in enumerate(steps, 1):
        if i < current:
            dot_cls, lbl_cls, num = "done", "", "✓"
        elif i == current:
            dot_cls, lbl_cls, num = "active", "active", str(i)
        else:
            dot_cls, lbl_cls, num = "idle", "", str(i)
        parts.append(
            f'<div class="step-item">'
            f'  <div class="step-dot {dot_cls}">{num}</div>'
            f'  <span class="step-label {lbl_cls}">{label}</span>'
            f'</div>'
        )
        if i < len(steps):
            conn = "done" if i < current else ""
            parts.append(f'<div class="step-connector {conn}"></div>')
    st.markdown(f'<div class="stepper">{"".join(parts)}</div>', unsafe_allow_html=True)

render_stepper(st.session_state.step)


# ── Question renderer ──────────────────────────────────────────────────
def render_question(q, prefix):
    qid      = q["id"]
    key      = f"{prefix}_{qid}"
    help_txt = q.get("help", "")
    if q["type"] == "select":
        return st.selectbox(q["label"], q["options"], key=key, help=help_txt)
    elif q["type"] == "multiselect":
        return st.multiselect(q["label"], q["options"], key=key, help=help_txt)
    elif q["type"] == "slider":
        return st.slider(q["label"], q["min"], q["max"],
                         value=q.get("default", q["min"]),
                         step=q.get("step", 1), key=key, help=help_txt)
    elif q["type"] == "radio":
        return st.radio(q["label"], q["options"], key=key, help=help_txt)
    elif q["type"] == "text":
        return st.text_input(q["label"], key=key, help=help_txt)
    return None


# ── Claude call ────────────────────────────────────────────────────────
def get_recommendations(industry, common, industry_ans, extra, pricing_text=""):
    client  = Anthropic(api_key=ANTHROPIC_API_KEY)
    system  = build_system_prompt()
    user_msg = build_user_prompt(industry, common, industry_ans, extra, pricing_text)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=16000,
        system=system,
        messages=[{"role": "user", "content": user_msg}],
    )
    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]
    return json.loads(raw)


# ══════════════════════════════════════════════════════════════════════
# STEP 1 · Industry Selection
# ══════════════════════════════════════════════════════════════════════
if st.session_state.step == 1:

    st.markdown('<div class="sec-heading">Which industry describes your business?</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Your selection tailors every question and the AI analysis to your sector\'s specific challenges, regulations, and use cases.</div>', unsafe_allow_html=True)

    industries = list(INDUSTRY_QUESTIONNAIRES.keys())
    icons = {
        "Manufacturing":          ("🏭", "Predictive maintenance, quality inspection, supply chain"),
        "Retail & E-Commerce":    ("🛒", "Demand forecasting, personalisation, fraud detection"),
        "Healthcare":             ("🏥", "Clinical documentation, patient triage, coding automation"),
        "Financial Services":     ("💰", "Fraud detection, credit scoring, regulatory reporting"),
        "Telecommunications":     ("📡", "Network monitoring, churn prediction, support automation"),
        "Logistics & Supply Chain":("🚚", "Route optimisation, fleet maintenance, warehouse AI"),
    }

    cols = st.columns(3)
    for i, ind in enumerate(industries):
        with cols[i % 3]:
            ico, desc = icons.get(ind, ("🏢", ""))
            st.markdown(f"""
            <div class="ind-card" style="margin-bottom:0.8rem;">
              <div class="ind-icon">{ico}</div>
              <div class="ind-name">{ind}</div>
              <div style="font-size:0.72rem;color:#94a3b8;margin-top:0.35rem;line-height:1.4;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Select →", key=f"ind_{i}", use_container_width=True):
                st.session_state.industry = ind
                st.session_state.step = 2
                st.rerun()

    st.markdown("""
    <div class="how-card">
      <div class="how-title">How it works</div>
      <div class="how-steps">
        <div class="how-step">
          <div class="how-step-num">1</div>
          <div class="how-step-text">Pick your industry</div>
        </div>
        <div class="how-step">
          <div class="how-step-num">2</div>
          <div class="how-step-text">Answer ~10 tailored questions</div>
        </div>
        <div class="how-step">
          <div class="how-step-num">3</div>
          <div class="how-step-text">Download a detailed PDF report with 3 AI plans</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# STEP 2 · Questionnaire
# ══════════════════════════════════════════════════════════════════════
elif st.session_state.step == 2:
    industry = st.session_state.industry
    ico = {"Manufacturing":"🏭","Retail & E-Commerce":"🛒","Healthcare":"🏥",
           "Financial Services":"💰","Telecommunications":"📡","Logistics & Supply Chain":"🚚"}.get(industry,"🏢")

    st.markdown(f'<div class="sec-heading">{ico} {industry} Profile</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Answer the questions below. Hover the ℹ️ icon on any question to see why it matters for your recommendation.</div>', unsafe_allow_html=True)

    if st.button("← Change industry"):
        st.session_state.step = 1
        st.rerun()

    st.markdown("""
    <style>
    div[data-testid="stForm"] {
      background: #1a2744 !important;
      border: 1px solid rgba(255,255,255,0.08) !important;
      border-radius: 14px !important;
      padding: 1.5rem !important;
    }
    div[data-testid="stSelectbox"] > label,
    div[data-testid="stMultiSelect"] > label,
    div[data-testid="stSlider"] > label,
    div[data-testid="stRadio"] > label,
    div[data-testid="stTextArea"] > label {
      color: #e2e8f0 !important; font-size: 0.9rem !important; font-weight: 500 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.form("questionnaire_form"):

        # General questions
        st.markdown('<div class="q-section-label">📋 General Business Profile</div>', unsafe_allow_html=True)
        common_answers = {}
        for q in COMMON_QUESTIONS:
            common_answers[q["id"]] = render_question(q, "c")


        # Industry-specific questions
        st.markdown(f'<div class="q-section-label">🏢 {industry} — Sector Questions</div>', unsafe_allow_html=True)
        industry_answers = {}
        for q in INDUSTRY_QUESTIONNAIRES[industry]:
            industry_answers[q["id"]] = render_question(q, "i")


        # Extra context
        st.markdown('<div class="q-section-label">💬 Additional Context (optional)</div>', unsafe_allow_html=True)
        extra_context = st.text_area(
            "Pain points, past experiments, vendor preferences, specific concerns…",
            height=100, key="extra_ctx",
            help="The more context you provide, the more specific and actionable your report will be.",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🚀  Generate My AI Adoption Report", use_container_width=True)

    if submitted:
        st.session_state.common_answers   = common_answers
        st.session_state.industry_answers = industry_answers
        st.session_state.extra_context    = extra_context
        st.session_state.step             = 3
        st.rerun()


# ══════════════════════════════════════════════════════════════════════
# STEP 3 · Generate + Download
# ══════════════════════════════════════════════════════════════════════
elif st.session_state.step == 3:

    # ── PDF ready ──────────────────────────────────────────────────────
    if st.session_state.pdf_bytes:
        plan_name = st.session_state.get("rec_plan_name", "")
        st.markdown(f"""
        <div class="report-card">
          <div class="report-card-icon">📄</div>
          <h2>Your Report Is Ready</h2>
          <p class="report-card-sub">Recommended: <strong>{plan_name}</strong></p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        dl_col, restart_col = st.columns([3, 1])
        with dl_col:
            st.download_button(
                "📥  Download PDF Report",
                data=st.session_state.pdf_bytes,
                file_name="SME_AI_Adoption_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        with restart_col:
            if st.button("🔄  Start Over", use_container_width=True):
                for k, v in DEFAULTS.items():
                    st.session_state[k] = v
                st.rerun()

        st.markdown("""
        <div style="margin-top:1.2rem;background:#fff;border:1px solid #e8eef4;border-radius:12px;
             padding:1rem 1.4rem;font-size:0.82rem;color:#64748b;line-height:1.7;">
          Your report includes a <b>business summary</b>, <b>key problems identified</b>,
          <b>compliance & policy notes</b>, three detailed AI adoption plans with cost breakdowns,
          an <b>AI routing decision table</b>, <b>comparison matrix</b>, and a
          <b>strategic recommendation</b> with next steps.
        </div>
        """, unsafe_allow_html=True)

    # ── Error ───────────────────────────────────────────────────────────
    elif st.session_state.error:
        st.markdown(f"""
        <div class="err-card">
          <b style="color:#c53030;">Something went wrong</b><br>
          <span style="font-size:0.85rem;color:#742a2a;">{st.session_state.error}</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Back to questionnaire"):
            st.session_state.step  = 2
            st.session_state.error = None
            st.rerun()

    # ── Generate ────────────────────────────────────────────────────────
    else:
        industry     = st.session_state.industry
        common       = st.session_state.common_answers
        industry_ans = st.session_state.industry_answers
        extra        = st.session_state.extra_context

        st.markdown(f"""
        <div style="background:#fff;border:1px solid #e8eef4;border-radius:16px;
             padding:2.5rem;text-align:center;box-shadow:0 2px 12px rgba(0,0,0,0.05);">
          <div style="font-size:2.4rem;margin-bottom:1rem;">⚙️</div>
          <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1.25rem;color:#0d1b2a;margin-bottom:0.4rem;">
            Generating your report…
          </div>
          <div style="font-size:0.88rem;color:#64748b;">
            Industry: <b>{industry}</b> · This typically takes 20–40 seconds
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        prog = st.progress(0, text="Fetching cloud pricing data…")

        try:
            pricing_data = collect_all_pricing(gcp_api_key=None, vastai_key=None, runpod_key=None)
            pricing_text = format_pricing_for_prompt(pricing_data)
        except Exception:
            pricing_text = ""
            pricing_data = None

        prog.progress(20, text="Analysing your profile with Claude…")

        try:
            result = get_recommendations(industry, common, industry_ans, extra, pricing_text)

            prog.progress(70, text="Building your PDF report…")

            tmp_path = os.path.join(tempfile.gettempdir(), f"sme_report_{os.getpid()}.pdf")
            generate_pdf(result, industry, tmp_path, pricing_metadata=pricing_data)
            with open(tmp_path, "rb") as f:
                pdf_bytes = f.read()
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

            prog.progress(100, text="Done!")

            plans    = result.get("plans", [])
            rec_num  = result.get("recommendation", {}).get("recommended_plan", 1)
            rec_plan = plans[rec_num - 1] if plans else {}
            rec_name = f"{rec_plan.get('plan_name','')} ({rec_plan.get('approach','')})"

            st.session_state.pdf_bytes     = pdf_bytes
            st.session_state.rec_plan_name = rec_name
            st.session_state.error         = None

        except json.JSONDecodeError as e:
            st.session_state.error = (
                f"Failed to parse AI response as JSON: {e}\n\n"
                "Try again — the model occasionally wraps output in extra text."
            )
            st.session_state.pdf_bytes = None
        except Exception as e:
            st.session_state.error = str(e)
            st.session_state.pdf_bytes = None

        st.rerun()

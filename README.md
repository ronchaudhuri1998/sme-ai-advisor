# 🤖 SME AI Adoption Advisor

**Public vs. Private AI: Scalable Business Agents for SMEs**  
DFW Technologies × UT Dallas Analytics Practicum (BUAN 6390 · Spring 2026)

---

## What It Does

An interactive recommendation engine that helps Small and Medium Enterprises (SMEs)
evaluate whether to adopt **public AI** (cloud APIs), **private AI** (self-hosted models),
or a **hybrid approach**. The tool:

1. Asks the SME to select their **industry segment** (Manufacturing, Retail, Healthcare, Financial Services, Telecom, Logistics)
2. Presents a **tailored questionnaire** covering company size, budget, data sensitivity, compliance needs, and industry-specific factors
3. Sends all inputs to **Claude (Anthropic API)** with a carefully engineered system prompt that returns structured JSON
4. Generates a **professional PDF report** (10-12 pages) containing:
   - Executive business profile summary
   - Business readiness radar chart (5 KPI dimensions)
   - 3 detailed AI adoption plans with cost tables, pros/cons, and implementation roadmaps
   - Cost comparison bar chart
   - Setup timeline comparison chart
   - 6-dimension score comparison (grouped bar chart)
   - Side-by-side comparison matrix
   - Final recommendation with actionable next steps

---

## Tech Stack

| Component       | Technology                          |
|-----------------|-------------------------------------|
| Frontend / UI   | Streamlit                           |
| AI Backend      | Anthropic Claude API (Sonnet)       |
| PDF Generation  | ReportLab (tables, layout, styles)  |
| Charts          | Matplotlib + NumPy                  |
| Language        | Python 3.10+                        |
| Hosting         | Local machine                       |

---

## Project Structure

```
sme_ai_advisor/
├── app.py              # Main Streamlit application (3-step wizard)
├── questionnaires.py   # Common + industry-specific question definitions
├── prompts.py          # System prompt (JSON output) & user prompt builder
├── pdf_generator.py    # Full PDF report builder (cover, charts, tables)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## Setup & Run

### 1. Clone / download this folder

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Get an Anthropic API key

- Sign up at https://console.anthropic.com
- Create an API key

### 4. Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`. Paste your API key in the sidebar.

---

## How It Works (Architecture)

```
┌──────────────┐     ┌────────────────────┐     ┌───────────────────┐
│  Streamlit UI │────▶│  Questionnaire     │────▶│  Claude API       │
│  (Browser)    │     │  Engine            │     │  (Sonnet model)   │
│               │     │  (questionnaires.py)│     │  Returns JSON     │
│  Step 1: Pick │     │                    │     │                   │
│   industry    │     │  Step 2: Collect   │     │  Structured plans │
│               │     │   answers          │     │  + scores + costs │
└──────┬───────┘     └────────────────────┘     └────────┬──────────┘
       │                                                  │
       │              ┌────────────────────┐              │
       │              │  PDF Generator     │◀─────────────┘
       │              │  (reportlab +      │   parsed JSON
       │              │   matplotlib)      │
       │              │                    │
       │              │  • Cover page      │
       │              │  • Radar chart     │
       │              │  • Plan details    │
       │              │  • Cost charts     │
       │              │  • Score bars      │
       │              │  • Comparison tbl  │
       │              │  • Recommendation  │
       │              └────────┬───────────┘
       │                       │
       ▼                       ▼
   Step 3: Preview    📄 Download PDF Report
   + Download
```

---

## PDF Report Contents

The generated PDF includes:

| Page(s) | Content |
|---------|---------|
| 1 | Cover page with industry and date |
| 2 | Table of contents |
| 3 | Business profile summary + readiness radar chart + KPI table |
| 4-5 | Plan 1 (Public AI): details table, pros/cons, roadmap |
| 6-7 | Plan 2 (Hybrid): details table, pros/cons, roadmap ⭐ |
| 8-9 | Plan 3 (Private AI): details table, pros/cons, roadmap |
| 10 | Cost comparison chart + setup timeline chart |
| 11 | 6-dimension score comparison (grouped bar chart) |
| 12 | Side-by-side comparison matrix + recommendation & next steps |

---

## Customisation

**Add a new industry:**
1. Add a new key to `INDUSTRY_QUESTIONNAIRES` in `questionnaires.py`
2. Define 5-7 questions following the existing dict format
3. The app auto-detects it — no other changes needed

**Modify the AI output:**
- Edit `build_system_prompt()` in `prompts.py` to change the JSON schema or add new fields
- Update `pdf_generator.py` to render any new fields

**Change the model:**
- In `app.py`, update the `model` parameter in `get_recommendations()`

**Customise PDF styling:**
- Colors, fonts, and layout are controlled by constants at the top of `pdf_generator.py`

---

## Team

BUAN 6390.502.26S · Analytics Practicum · Spring 2026  
Sponsor: Joe Zhu, DFW Technologies  
Professor: Mandar Samant, UT Dallas

---

## License

Academic project — not for production use.

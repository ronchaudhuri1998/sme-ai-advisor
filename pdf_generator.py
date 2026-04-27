"""
PDF Report Generator — SME AI Adoption Advisor v4
Pages:
  1  · Cover + Business Summary + Key Problems + Policies & Compliance
  2  · AI Routing Table + Plan Comparison Matrix + Charts
  3-5 · Plan detail pages (one per plan)
  6  · Recommendation & Next Steps
"""

import io, math
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, HRFlowable,
)

LM = RM = 0.5 * inch
TM = BM = 0.5 * inch
PW = letter[0] - LM - RM  # 504pt

NAVY   = colors.HexColor("#0A1628")
NAVY2  = colors.HexColor("#1a2d4d")
STEEL  = colors.HexColor("#2C3E5D")
RED    = colors.HexColor("#C8102E")
SILVER = colors.HexColor("#E8ECF2")
SLT    = colors.HexColor("#F4F6FA")
WHITE  = colors.white
TEXT   = colors.HexColor("#1A2332")
MUTED  = colors.HexColor("#5A6880")
ACCENT = colors.HexColor("#FF6B35")
GREEN  = colors.HexColor("#00875A")
GOLD   = colors.HexColor("#D4A017")

PLAN_HEX = {"Public AI": "#00875A", "Hybrid": "#FF6B35", "Private AI": "#2C3E5D"}
PLAN_COL = {k: colors.HexColor(v) for k, v in PLAN_HEX.items()}
BADGE_BG = {"Private": colors.HexColor("#e8f0ff"), "Public": colors.HexColor("#e6f9f0"),
            "Hybrid": colors.HexColor("#fff4e6"),
            "Private AI": colors.HexColor("#e8f0ff"), "Public AI": colors.HexColor("#e6f9f0")}
BADGE_FG = {"Private": colors.HexColor("#2952cc"), "Public": GREEN,
            "Hybrid": colors.HexColor("#b85c00"),
            "Private AI": colors.HexColor("#2952cc"), "Public AI": GREEN}


def _p(name, **kw):
    return ParagraphStyle(name=name, **kw)

def _st():
    return {
        "body":    _p("body",   fontName="Helvetica",      fontSize=9,  leading=14, textColor=MUTED),
        "body_dk": _p("bdk",    fontName="Helvetica",      fontSize=9,  leading=14, textColor=TEXT),
        "sm":      _p("sm",     fontName="Helvetica",      fontSize=8,  leading=12, textColor=MUTED),
        "bold_nv": _p("bold_nv",fontName="Helvetica-Bold", fontSize=9,  leading=13, textColor=NAVY),
        "grn_sm":  _p("grn_sm", fontName="Helvetica-Bold", fontSize=8,  leading=11, textColor=GREEN),
        "red_sm":  _p("red_sm", fontName="Helvetica-Bold", fontSize=8,  leading=11, textColor=RED),
    }

def _hr(col=SILVER, t=0.5, sb=4, sa=4):
    return HRFlowable(width="100%", thickness=t, color=col, spaceBefore=sb, spaceAfter=sa)

def _sec(text, col=RED):
    return [Paragraph(text.upper(), _p(f"sc{text[:6]}", fontName="Helvetica-Bold",
                                       fontSize=8, leading=10, textColor=MUTED)),
            _hr(col, 1.5, 2, 8)]

def _hdr(tag, title, pg, tc=RED):
    tp = _p(f"t{tag[:4]}", fontName="Helvetica-Bold", fontSize=7, leading=9, textColor=WHITE)
    tt = Table([[Paragraph(tag, tp)]], colWidths=[0.85*inch])
    tt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),tc),
                             ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
                             ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6)]))
    hp = _p(f"h{title[:6]}", fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=NAVY)
    pp = _p(f"p{pg}", fontName="Courier", fontSize=9, leading=11, textColor=MUTED, alignment=TA_RIGHT)
    t = Table([[tt, Paragraph(title,hp), Paragraph(pg,pp)]],
              colWidths=[1.0*inch, PW-1.9*inch, 0.9*inch])
    t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                            ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
                            ("LINEBELOW",(0,0),(-1,-1),0.5,SILVER)]))
    return t


def _cost_chart(plans):
    """Horizontal bar chart with error bars — matches screenshot style."""
    import tempfile, uuid, os
    names = [f"{p['approach']}\n{p['plan_name']}" +
             (" *" if p.get("is_recommended") else "") for p in plans]
    lows  = [p["details"]["monthly_cost_low"]  for p in plans]
    highs = [p["details"]["monthly_cost_high"] for p in plans]
    mid   = [(lo + hi) / 2 for lo, hi in zip(lows, highs)]
    err   = [(hi - lo) / 2 for lo, hi in zip(lows, highs)]
    clrs  = [PLAN_HEX.get(p["approach"], "#888") for p in plans]

    fig, ax = plt.subplots(figsize=(8.5, 3.2))
    fig.patch.set_facecolor("white"); ax.set_facecolor("white")
    ax.barh(range(len(plans)), mid, xerr=err, color=clrs, height=0.45,
            capsize=6, alpha=0.88, edgecolor="white", error_kw={"elinewidth": 1.5, "ecolor": "#444"})
    for i, (lo, hi) in enumerate(zip(lows, highs)):
        ax.text(hi + max(highs) * 0.025, i,
                f" {lo:,}–{hi:,}/mo",
                va="center", fontsize=9, fontweight="bold", color="#1a1a2e")
    ax.set_yticks(range(len(plans)))
    ax.set_yticklabels(names, fontsize=9)
    ax.set_xlabel("Estimated Monthly Cost ($)", fontsize=9, color="#555")
    ax.set_title("Monthly Cost Comparison", fontsize=13, fontweight="bold", color="#0f3460", pad=10)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.set_xlim(0, max(highs) * 1.38)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.tick_params(axis="both", colors="#555")
    fig.tight_layout(pad=0.6)
    tmp = os.path.join(tempfile.gettempdir(), f"cost_{uuid.uuid4().hex[:8]}.png")
    fig.savefig(tmp, format="png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return tmp


def _timeline_chart(plans):
    """Horizontal bar chart for setup weeks — matches screenshot style."""
    import tempfile, uuid, os
    names = [p["approach"] for p in plans]
    weeks = [p["details"]["setup_weeks"] for p in plans]
    clrs  = [PLAN_HEX.get(p["approach"], "#888") for p in plans]

    fig, ax = plt.subplots(figsize=(8.5, 2.6))
    fig.patch.set_facecolor("white"); ax.set_facecolor("white")
    bars = ax.barh(names, weeks, color=clrs, height=0.45, alpha=0.88, edgecolor="white")
    for bar, w in zip(bars, weeks):
        ax.text(bar.get_width() + max(weeks) * 0.02, bar.get_y() + bar.get_height() / 2,
                f" {w} weeks", va="center", fontsize=9, fontweight="bold", color="#1a1a2e")
    ax.set_xlabel("Weeks", fontsize=9, color="#555")
    ax.set_title("Setup Timeline Comparison", fontsize=13, fontweight="bold", color="#0f3460", pad=10)
    ax.set_xlim(0, max(weeks) * 1.3)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.tick_params(axis="both", colors="#555")
    fig.tight_layout(pad=0.6)
    tmp = os.path.join(tempfile.gettempdir(), f"tl_{uuid.uuid4().hex[:8]}.png")
    fig.savefig(tmp, format="png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return tmp


def generate_pdf(data: dict, industry: str, output_path: str, pricing_metadata=None):
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM)
    s = _st()
    els = []
    plans = data.get("plans", [])
    rec   = data.get("recommendation", {})
    rec_num = rec.get("recommended_plan", 1)
    for p in plans:
        p["is_recommended"] = (p.get("plan_number") == rec_num)
    date_str = datetime.now().strftime("%B %Y")

    # ─ helpers ─────────────────────────────────────────────────────────
    HALF = PW / 2

    def _band(items, bg=NAVY, lp=18):
        rows = [[item] for item in items]
        t = Table(rows, colWidths=[PW])
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),bg),
                                ("LEFTPADDING",(0,0),(-1,-1),lp),("RIGHTPADDING",(0,0),(-1,-1),lp),
                                ("TOPPADDING",(0,0),(0,0),16),("BOTTOMPADDING",(0,-1),(-1,-1),16),
                                ("TOPPADDING",(0,1),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-2),3)]))
        return t


    def _two_col(left_els, right_els):
        CW = HALF - 8  # inner content width per side
        def _side(items):
            rows = [[e] for e in items]
            t = Table(rows, colWidths=[CW])
            t.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
                                    ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))
            return t
        t = Table([[_side(left_els), _side(right_els)]], colWidths=[HALF, HALF])
        t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
                                ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
                                ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
                                ("LINEAFTER",(0,0),(0,-1),0.5,SILVER)]))
        return t

    # ═══════════════════════════════════════════════════════════════════
    # PAGE 1 · COVER + SUMMARY + KEY PROBLEMS + POLICIES
    # ═══════════════════════════════════════════════════════════════════
    els.append(_band([
        Paragraph("DFW TECHNOLOGIES  ·  AI ADOPTION REPORT",
                  _p("eye", fontName="Helvetica-Bold", fontSize=7, leading=10,
                     textColor=colors.HexColor("#E8192E"))),
        Paragraph("SME AI Advisor",
                  _p("h1", fontName="Helvetica-Bold", fontSize=22, leading=26, textColor=WHITE)),
        Paragraph(f"{industry} Sector  ·  {date_str}",
                  _p("sub", fontName="Helvetica", fontSize=11, leading=14,
                     textColor=colors.HexColor("#aabbcc"))),
    ]))
    els.append(Spacer(1, 10))
    els.append(_hdr("OVERVIEW", "Business Summary", "Page 01"))
    els.append(Spacer(1, 8))
    els.append(Paragraph(data.get("business_summary", ""), s["body"]))
    els.append(Spacer(1, 14))

    # Key Problems
    for e in _sec("Key Problems Identified"): els.append(e)
    problems = data.get("key_problems", [])
    PI = PW - 24  # problem inner width
    for prob in problems:
        np_ = Paragraph(str(prob.get("number","")),
                        _p(f"pn{prob.get('number','')}", fontName="Helvetica-Bold",
                           fontSize=9, leading=11, textColor=WHITE, alignment=TA_CENTER))
        nt = Table([[np_]], colWidths=[0.22*inch], rowHeights=[0.22*inch])
        nt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),RED),
                                 ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                                 ("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2)]))
        tit = Paragraph(f"<b>{prob.get('title','')}</b>",
                        _p(f"pt{prob.get('number','')}", fontName="Helvetica-Bold",
                           fontSize=9, leading=12, textColor=NAVY))
        hdr = Table([[nt, tit]], colWidths=[0.28*inch, PI - 0.28*inch])
        hdr.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                                   ("LEFTPADDING",(1,0),(1,0),6),
                                   ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0)]))
        card_in = Table([[hdr],[Spacer(1,2)],
                         [Paragraph(prob.get("description",""), s["sm"])],[Spacer(1,2)],
                         [Paragraph(f"<b>Impact:</b> {prob.get('business_impact','')}",
                                    _p(f"pi{prob.get('number','')}", fontName="Helvetica",
                                       fontSize=8, leading=11, textColor=RED))]],
                        colWidths=[PI])
        card_in.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
                                      ("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10)]))
        card = Table([[card_in]], colWidths=[PW])
        card.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),SLT),
                                   ("LINEBEFORE",(0,0),(0,-1),3,RED),
                                   ("BOX",(0,0),(-1,-1),0.5,SILVER),
                                   ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),6),
                                   ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))
        els.append(card); els.append(Spacer(1,5))

    els.append(Spacer(1, 10))

    # Policies & Compliance
    for e in _sec("Policies, Compliance & Restrictions to Address"): els.append(e)
    policies = data.get("policies_compliance", [])
    POW = PW / 3           # 168pt outer per cell
    PIW = POW - 16         # 152pt inner (8+8 padding)
    DW  = 0.10 * inch      # dot width
    PTW = PIW - DW         # policy title text width

    def _pc(title, desc):
        dot = Table([[""]], colWidths=[DW], rowHeights=[DW])
        dot.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),RED)]))
        hdr2 = Table([[dot, Paragraph(f"<b>{title}</b>",
                                      _p(f"pch{title[:6]}", fontName="Helvetica-Bold",
                                         fontSize=8, leading=11, textColor=NAVY))]],
                     colWidths=[DW, PTW])
        hdr2.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                                    ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
                                    ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0)]))
        inner = Table([[hdr2],[Paragraph(desc, _p(f"pcd{title[:6]}", fontName="Helvetica",
                                                   fontSize=8, leading=11, textColor=MUTED))]],
                      colWidths=[PIW])
        inner.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
                                    ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8)]))
        outer = Table([[inner]], colWidths=[POW])
        outer.setStyle(TableStyle([("BOX",(0,0),(-1,-1),0.5,SILVER),
                                    ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
                                    ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))
        return outer

    for i in range(0, len(policies), 3):
        batch = policies[i:i+3]
        cards = [_pc(p.get("title",""), p.get("description","")) for p in batch]
        while len(cards) < 3: cards.append(Spacer(POW, 10))
        row = Table([cards], colWidths=[POW]*3)
        row.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
                                   ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
                                   ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))
        els.append(row); els.append(Spacer(1,5))

    els.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════
    # PAGE 2 · ROUTING TABLE + COMPARISON MATRIX + CHARTS
    # ═══════════════════════════════════════════════════════════════════
    els.append(_hdr("ANALYSIS", "AI Routing Decisions & Plan Comparison", "Page 02", STEEL))
    els.append(Spacer(1, 10))

    for e in _sec("AI Routing Decision Summary", STEEL): els.append(e)
    rt_rows = data.get("ai_routing_table", [])
    rt_hdr = [Paragraph(h, _p(f"rth{h[:3]}", fontName="Helvetica-Bold", fontSize=8,
                               leading=10, textColor=colors.HexColor("#ffffffb0")))
              for h in ["Workload","AI Routing","Rationale","Primary Output"]]
    rt_data = [rt_hdr]
    for row in rt_rows:
        rv = row.get("routing","Hybrid")
        rt_data.append([Paragraph(row.get("workload",""), s["bold_nv"]),
                         Paragraph(rv.upper(), _p(f"rb{rv[:3]}", fontName="Helvetica-Bold",
                                                   fontSize=7, leading=9,
                                                   textColor=BADGE_FG.get(rv,TEXT))),
                         Paragraph(row.get("rationale",""), s["sm"]),
                         Paragraph(row.get("primary_output",""), s["sm"])])
    rt = Table(rt_data, colWidths=[1.9*inch, 0.9*inch, 2.5*inch, 1.7*inch])
    rt_st = [("BACKGROUND",(0,0),(-1,0),NAVY),
             ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
             ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
             ("LINEBELOW",(0,0),(-1,-2),0.5,SILVER),("VALIGN",(0,0),(-1,-1),"MIDDLE")]
    for i in range(1, len(rt_data), 2): rt_st.append(("BACKGROUND",(0,i),(-1,i),SLT))
    for ri, row in enumerate(rt_rows, 1):
        rt_st.append(("BACKGROUND",(1,ri),(1,ri),BADGE_BG.get(row.get("routing","Hybrid"),SLT)))
    rt.setStyle(TableStyle(rt_st))
    els.append(rt); els.append(Spacer(1,14))

    for e in _sec("Side-by-Side Plan Comparison"): els.append(e)
    matrix = data.get("comparison_matrix",{})
    factors = matrix.get("factors",[])
    pvals = [matrix.get("plan_1_values",[]), matrix.get("plan_2_values",[]), matrix.get("plan_3_values",[])]
    pnames = [p["approach"] for p in plans]
    if factors and pvals[0]:
        cm_hdr = [Paragraph("Factor", _p("cmf", fontName="Helvetica-Bold", fontSize=8,
                                          leading=10, textColor=colors.HexColor("#ffffffb0")))]
        for pn in pnames:
            cm_hdr.append(Paragraph(pn, _p(f"cmh{pn[:3]}", fontName="Helvetica-Bold",
                                            fontSize=8, leading=10,
                                            textColor=colors.HexColor("#ffffffb0"))))
        cm_data = [cm_hdr]
        cwe = (PW - 2.0*inch) / len(plans)
        for fi, factor in enumerate(factors):
            row = [Paragraph(factor, s["bold_nv"])]
            for pi in range(len(plans)):
                v = pvals[pi][fi] if fi < len(pvals[pi]) else ""
                row.append(Paragraph(v, s["sm"]))
            cm_data.append(row)
        cm = Table(cm_data, colWidths=[2.0*inch]+[cwe]*len(plans))
        cm_st = [("BACKGROUND",(0,0),(-1,0),NAVY),
                 ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
                 ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
                 ("LINEBELOW",(0,0),(-1,-2),0.5,SILVER),("VALIGN",(0,0),(-1,-1),"MIDDLE")]
        for i in range(1, len(cm_data), 2): cm_st.append(("BACKGROUND",(0,i),(-1,i),SLT))
        cm.setStyle(TableStyle(cm_st))
        els.append(cm)

    # Charts on same page — two side by side, compact heights
    try:
        cost_path     = _cost_chart(plans)
        timeline_path = _timeline_chart(plans)
        ci = Image(cost_path,     width=PW/2 - 6, height=2.2*inch)
        ti = Image(timeline_path, width=PW/2 - 6, height=2.2*inch)
        chart_row = Table([[ci, ti]], colWidths=[PW/2, PW/2])
        chart_row.setStyle(TableStyle([
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("LEFTPADDING",(0,0),(-1,-1),2),
            ("RIGHTPADDING",(0,0),(-1,-1),2),
            ("TOPPADDING",(0,0),(-1,-1),0),
            ("BOTTOMPADDING",(0,0),(-1,-1),0),
        ]))
        els.append(Spacer(1,10))
        els.append(chart_row)
    except Exception:
        pass
    els.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════
    # PAGES 3-5 · PLAN DETAIL PAGES
    # ═══════════════════════════════════════════════════════════════════
    for plan in plans:
        approach = plan.get("approach","")
        pc = PLAN_COL.get(approach, NAVY)
        pn = plan.get("plan_number", 1)
        is_rec = plan.get("is_recommended", False)
        d = plan.get("details", {})

        tag = f"PLAN {pn}" + (" ★ RECOMMENDED" if is_rec else "")
        els.append(_hdr(tag, f"{plan.get('plan_name','')}  —  {approach}",
                        f"Page 0{2+pn}", pc))
        els.append(Spacer(1,6))

        # Quick stats bar — cost + setup only (no scores)
        qs = [("Monthly Cost", f"${d.get('monthly_cost_low',0):,} – ${d.get('monthly_cost_high',0):,}"),
              ("Setup Time",   f"{d.get('setup_weeks','?')} weeks")]
        qs_cells = []
        for ql, qv in qs:
            qs_cells.append(Table([
                [Paragraph(qv, _p(f"qsv{ql[:3]}", fontName="Helvetica-Bold", fontSize=13,
                                  leading=16, textColor=NAVY, alignment=TA_CENTER))],
                [Paragraph(ql.upper(), _p(f"qsl{ql[:3]}", fontName="Helvetica", fontSize=7,
                                          leading=9, textColor=MUTED, alignment=TA_CENTER))],
            ], colWidths=[PW/2]))
        qs_row = Table([qs_cells], colWidths=[PW/2]*2)
        qs_row.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),SLT),
                                     ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
                                     ("LINEAFTER",(0,0),(0,-1),0.5,SILVER)]))
        els.append(qs_row); els.append(Spacer(1,8))

        els.append(Paragraph(f"<b>Best For:</b> {plan.get('best_for','')}", s["body_dk"]))
        els.append(Spacer(1,4))
        els.append(Paragraph(f"<b>Architecture:</b> {plan.get('architecture_summary','')}", s["body"]))
        els.append(Spacer(1,5))
        els.append(Paragraph(plan.get("detailed_description",""), s["body"]))
        els.append(Spacer(1,8))

        # Cost breakdown
        cbd = d.get("cost_breakdown",[])
        if cbd:
            for e in _sec("Cost Breakdown", pc): els.append(e)
            cb_hdr = [Paragraph(h, _p(f"cbh{h[:3]}", fontName="Helvetica-Bold", fontSize=8,
                                       leading=10, textColor=colors.HexColor("#ffffffb0")))
                      for h in ["Line Item","Unit Price","Quantity","Monthly Cost"]]
            cb_data = [cb_hdr]
            for item in cbd:
                cb_data.append([Paragraph(item.get("item",""), s["bold_nv"]),
                                  Paragraph(item.get("unit_price",""), s["sm"]),
                                  Paragraph(item.get("quantity",""), s["sm"]),
                                  Paragraph(f"${item.get('monthly_cost',0):,}",
                                            _p(f"mc{item.get('item','')[:4]}", fontName="Helvetica-Bold",
                                               fontSize=8, leading=10, textColor=GREEN, alignment=TA_RIGHT))])
            cb = Table(cb_data, colWidths=[2.3*inch, 1.4*inch, 1.9*inch, 1.4*inch])
            cb_st = [("BACKGROUND",(0,0),(-1,0),NAVY),
                     ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
                     ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
                     ("LINEBELOW",(0,0),(-1,-2),0.5,SILVER),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                     ("ALIGN",(3,0),(3,-1),"RIGHT")]
            for i in range(1, len(cb_data), 2): cb_st.append(("BACKGROUND",(0,i),(-1,i),SLT))
            cb.setStyle(TableStyle(cb_st))
            els.append(cb); els.append(Spacer(1,8))

        # Pros & Cons two-column
        CW = HALF - 8
        def _side(items):
            t = Table([[e] for e in items], colWidths=[CW])
            t.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
                                    ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))
            return t
        pros_els = [Paragraph("<b>✅ PROS</b>", s["grn_sm"]), _hr(GREEN,1,2,5)]
        cons_els = [Paragraph("<b>❌ CONS</b>", s["red_sm"]), _hr(RED,1,2,5)]
        for pro in plan.get("pros",[]): pros_els += [Paragraph(f"• {pro}", s["sm"]), Spacer(1,3)]
        for con in plan.get("cons",[]): cons_els += [Paragraph(f"• {con}", s["sm"]), Spacer(1,3)]
        pc_tbl = Table([[_side(pros_els), _side(cons_els)]], colWidths=[HALF,HALF])
        pc_tbl.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
                                     ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
                                     ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
                                     ("LINEAFTER",(0,0),(0,-1),0.5,SILVER)]))
        els.append(pc_tbl); els.append(Spacer(1,8))

        # Risks
        risks = plan.get("risks",[])
        if risks:
            for e in _sec("Key Risks & Mitigations", GOLD): els.append(e)
            for r in risks:
                sev = r.get("severity","Medium")
                icon = "🔴" if sev=="High" else "🟡" if sev=="Medium" else "🟢"
                rr = Table([[Paragraph(icon, _p(f"ri{r.get('risk','')[:4]}", fontName="Helvetica",
                                                  fontSize=11, leading=14)),
                              Table([[Paragraph(f"<b>{r.get('risk','')}  ({sev})</b>", s["bold_nv"])],
                                     [Paragraph(f"Mitigation: {r.get('mitigation','')}", s["sm"])]],
                                    colWidths=[PW-0.4*inch])]],
                            colWidths=[0.3*inch, PW-0.3*inch])
                rr.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
                                         ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
                                         ("LINEBELOW",(0,0),(-1,-1),0.5,SILVER)]))
                els.append(rr)
            els.append(Spacer(1,8))

        # Recommended timeline (3 phases)
        timeline = d.get("recommended_timeline",{})
        phases = timeline.get("phases",[])
        if phases:
            for e in _sec("Recommended Implementation Timeline", NAVY): els.append(e)
            phase_cols = [STEEL, NAVY2, pc]
            for i, phase in enumerate(phases[:3]):
                ph_col = phase_cols[i % 3]
                ph_p = Paragraph(f"<b>{phase.get('phase','')}</b><br/>{phase.get('duration','')}",
                                  _p(f"ph{i}", fontName="Helvetica-Bold", fontSize=8,
                                     leading=11, textColor=WHITE, alignment=TA_CENTER))
                ph_t = Table([[ph_p]], colWidths=[0.9*inch])
                ph_t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),ph_col),
                                           ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                                           ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
                ct = Table([[Paragraph(f"<b>{phase.get('title','')}</b>", s["bold_nv"])],
                             [Paragraph(phase.get("description",""), s["sm"])]],
                            colWidths=[PW-1.05*inch])
                ct.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2)]))
                tr = Table([[ph_t, ct]], colWidths=[0.95*inch, PW-0.95*inch])
                tr.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
                                         ("LEFTPADDING",(1,0),(1,0),8),
                                         ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
                                         ("LINEBELOW",(0,0),(-1,-1),0.5,SILVER)]))
                els.append(tr)
            els.append(Spacer(1,6))

        # Data handling & compliance
        for e in _sec("Data Handling & Compliance Notes", SILVER): els.append(e)
        els.append(Paragraph(d.get("data_handling",""), s["body"]))
        els.append(Spacer(1,3))
        els.append(Paragraph(d.get("compliance_notes",""), s["body"]))
        els.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════
    # FINAL PAGE · RECOMMENDATION & NEXT STEPS
    # ═══════════════════════════════════════════════════════════════════
    total_pages = 2 + len(plans) + 1
    els.append(_hdr("RECOMMENDATION", "Strategic Recommendation & Next Steps",
                    f"Page 0{total_pages}", GREEN))
    els.append(Spacer(1,6))

    rec_plan = plans[rec_num-1] if plans else {}
    rpc = PLAN_COL.get(rec_plan.get("approach",""), GREEN)

    rec_ban = Table([[
        Paragraph("⭐ RECOMMENDED PLAN",
                  _p("rbl", fontName="Helvetica-Bold", fontSize=9, leading=11,
                     textColor=colors.HexColor("#ffffff80"))),
        Paragraph(f"{rec_plan.get('plan_name','')}  —  {rec_plan.get('approach','')}",
                  _p("rbn", fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=WHITE)),
    ]], colWidths=[1.6*inch, PW-1.6*inch])
    rec_ban.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),rpc),
                                   ("TOPPADDING",(0,0),(-1,-1),12),("BOTTOMPADDING",(0,0),(-1,-1),12),
                                   ("LEFTPADDING",(0,0),(-1,-1),14),("RIGHTPADDING",(0,0),(-1,-1),14),
                                   ("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    els.append(rec_ban); els.append(Spacer(1,10))

    for e in _sec("Why This Plan?", rpc): els.append(e)
    els.append(Paragraph(rec.get("reasoning",""), s["body"])); els.append(Spacer(1,10))

    factors = rec.get("key_decision_factors",[])
    if factors:
        for e in _sec("Key Decision Factors", NAVY): els.append(e)
        for f in factors:
            fr = Table([[Paragraph(f"<b>{f.get('factor','')}</b>", s["bold_nv"]),
                          Paragraph(f.get("impact",""), s["sm"])]],
                       colWidths=[1.8*inch, PW-1.8*inch])
            fr.setStyle(TableStyle([("LINEBELOW",(0,0),(-1,-1),0.5,SILVER),
                                     ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
                                     ("VALIGN",(0,0),(-1,-1),"TOP")]))
            els.append(fr)
        els.append(Spacer(1,10))

    why_not = rec.get("why_not_others",[])
    if why_not:
        for e in _sec("Why Not the Other Plans?", RED): els.append(e)
        for wn in why_not:
            opn = wn.get("plan_number",0)
            other = plans[opn-1] if 1 <= opn <= len(plans) else None
            lbl = f"Plan {opn}" + (f" — {other['plan_name']} ({other['approach']})" if other else "")
            els.append(Paragraph(f"<b>{lbl}</b>", s["bold_nv"]))
            els.append(Paragraph(wn.get("reason",""), s["sm"])); els.append(Spacer(1,6))

    roi_text = rec.get("expected_roi","")
    if roi_text:
        rb = Table([[Paragraph(f"<b>Expected ROI:</b> {roi_text}", s["body_dk"])]], colWidths=[PW])
        rb.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#f0fdf9")),
                                  ("LINEBEFORE",(0,0),(0,-1),3,GREEN),
                                  ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
                                  ("LEFTPADDING",(0,0),(-1,-1),14),("RIGHTPADDING",(0,0),(-1,-1),14)]))
        els.append(Spacer(1,6)); els.append(rb); els.append(Spacer(1,10))

    next_steps = rec.get("next_steps",[])
    if next_steps:
        for e in _sec("Next Steps", ACCENT): els.append(e)
        for i, step in enumerate(next_steps, 1):
            nb_p = Paragraph(str(i), _p(f"nb{i}", fontName="Helvetica-Bold", fontSize=9,
                                         leading=11, textColor=WHITE, alignment=TA_CENTER))
            nb = Table([[nb_p]], colWidths=[0.24*inch], rowHeights=[0.24*inch])
            nb.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),ACCENT),
                                     ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                                     ("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2)]))
            sr = Table([[nb, Paragraph(step, s["body_dk"])]], colWidths=[0.34*inch, PW-0.34*inch])
            sr.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                                     ("LEFTPADDING",(1,0),(1,0),10),
                                     ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
                                     ("LINEBELOW",(0,0),(-1,-1),0.5,SILVER)]))
            els.append(sr); els.append(Spacer(1,3))

    els.append(Spacer(1,16))
    ft = Table([[
        Paragraph(f"DFW Technologies SME AI Advisor  ·  {date_str}",
                  _p("ft1", fontName="Helvetica", fontSize=8, leading=10,
                     textColor=colors.HexColor("#aabbcc"))),
        Paragraph("BUAN 6390.502  ·  Analytics Practicum  ·  Spring 2026",
                  _p("ft2", fontName="Courier", fontSize=8, leading=10,
                     textColor=colors.HexColor("#aabbcc"), alignment=TA_RIGHT)),
    ]], colWidths=[PW/2, PW/2])
    ft.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),NAVY),
                              ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
                              ("LEFTPADDING",(0,0),(-1,-1),14),("RIGHTPADDING",(0,0),(-1,-1),14),
                              ("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    els.append(ft)
    doc.build(els)

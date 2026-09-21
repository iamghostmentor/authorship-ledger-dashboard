import math
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

NAVY = "#1E2761"
ICE = "#CADCFC"
TINT = "#EDF3FE"
RED = "#C0392B"
GRAY = "#B7C3E0"
GREEN = "#1E7A3C"
FONT = "Inter, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"

DATA_PATH = Path(__file__).parent / "data" / "authorship_ledger_cases.csv"

DEFAULTS = {
    "subs": 2500,
    "fpr": 1.0,
    "cost": 2000,
    "build": 40000,
    "maint": 15000,
    "avoid": 90,
}

SECTIONS = ["Overview", "Expected Value Model", "Build vs. Buy", "Dataset Explorer"]

st.set_page_config(
    page_title="Authorship Ledger | BUS 440",
    page_icon="🔏",
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
.stApp, .stApp p, .stApp li, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stApp button, .stApp input, .stApp textarea, [class^="al-"], [class*=" al-"] {{
    font-family: {FONT};
}}
.block-container {{ padding-top: 2.4rem; padding-bottom: 3rem; max-width: 1240px; }}
#MainMenu, footer {{ visibility: hidden; }}
[data-testid="stSlider"] label p {{ font-size: .86rem; font-weight: 500; }}
.al-cq {{ container-type: inline-size; }}
.al-grid {{ display: grid; gap: 1rem; grid-template-columns: repeat(4, minmax(0, 1fr)); }}
@container (max-width: 820px) {{ .al-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
@container (max-width: 380px) {{ .al-grid {{ grid-template-columns: minmax(0, 1fr); }} }}
.al-kicker {{ font-size: .78rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: rgba(30,39,97,.6); }}
.al-title {{ font-size: 2.1rem; font-weight: 800; letter-spacing: -.02em; line-height: 1.15; margin: .15rem 0 .35rem; color: {NAVY}; }}
.al-sub {{ font-size: 1.02rem; color: rgba(30,39,97,.78); max-width: 62rem; margin-bottom: 1.6rem; line-height: 1.55; }}
.al-h3 {{ font-size: 1.15rem; font-weight: 700; margin: 2rem 0 .5rem; color: {NAVY}; }}
.al-note {{ font-size: .88rem; color: rgba(30,39,97,.7); line-height: 1.5; }}
.al-kpi {{ border-radius: 14px; padding: 20px 20px; color: #fff; height: 158px; box-sizing: border-box; }}
.al-kpi.red {{ background: {RED}; }}
.al-kpi.navy {{ background: {NAVY}; }}
.al-kpi.green {{ background: {GREEN}; }}
.al-kpi .lbl {{ font-size: .72rem; font-weight: 600; letter-spacing: .05em; text-transform: uppercase; opacity: .88; min-height: 2.3em; line-height: 1.15; }}
.al-kpi .val {{ font-size: 2.1rem; font-weight: 800; line-height: 1.1; margin: .3rem 0 .25rem; letter-spacing: -.02em; white-space: nowrap; }}
.al-kpi .sub {{ font-size: .95rem; opacity: .92; }}
.al-stat {{ background: {TINT}; border: 1px solid {ICE}; border-radius: 12px; padding: 14px 16px; height: 150px; box-sizing: border-box; }}
.al-stat .lbl {{ font-size: .72rem; font-weight: 600; letter-spacing: .05em; text-transform: uppercase; color: rgba(30,39,97,.72); min-height: 2.3em; line-height: 1.15; }}
.al-stat .val {{ font-size: 1.6rem; font-weight: 700; margin: .2rem 0 .1rem; color: {NAVY}; letter-spacing: -.01em; }}
.al-stat .fx {{ font-size: .74rem; color: rgba(30,39,97,.62); line-height: 1.35; }}
.al-stat.alert .val {{ color: {RED}; }}
.al-stat.win {{ background: {GREEN}; border-color: {GREEN}; }}
.al-stat.win .lbl, .al-stat.win .fx {{ color: rgba(255,255,255,.85); }}
.al-stat.win .val {{ color: #fff; }}
.al-stat.bad {{ background: {RED}; border-color: {RED}; }}
.al-stat.bad .lbl, .al-stat.bad .fx {{ color: rgba(255,255,255,.85); }}
.al-stat.bad .val {{ color: #fff; }}
.al-callout {{ background: {TINT}; border-left: 6px solid {NAVY}; border-radius: 8px; padding: 18px 24px; font-size: 1.05rem; line-height: 1.6; color: {NAVY}; }}
.al-card {{ background: {TINT}; border: 1px solid {ICE}; border-radius: 12px; padding: 18px 20px; color: {NAVY}; line-height: 1.55; font-size: .95rem; }}
.al-card.tall {{ min-height: 132px; }}
.al-card b.h {{ display: block; font-size: 1rem; margin-bottom: .25rem; }}
.al-brand {{ font-size: 1.35rem; font-weight: 800; letter-spacing: -.02em; color: {NAVY}; }}
.al-tag {{ font-size: .82rem; color: rgba(30,39,97,.7); margin: .1rem 0 1.2rem; line-height: 1.4; }}
.al-score {{ width: 100%; max-width: 560px; border-collapse: collapse; font-size: .92rem; color: {NAVY}; }}
.al-score th {{ text-align: left; font-size: .72rem; letter-spacing: .05em; text-transform: uppercase; color: rgba(30,39,97,.65); padding: 6px 8px; border-bottom: 2px solid {NAVY}; }}
.al-score td {{ padding: 9px 8px; border-bottom: 1px solid {ICE}; }}
.al-score td.n {{ text-align: center; }}
.al-score td.w {{ font-weight: 800; }}
.al-footer {{ margin-top: 3.5rem; padding-top: 1rem; border-top: 1px solid {ICE}; text-align: center; font-size: .82rem; color: rgba(30,39,97,.65); }}
</style>
""",
    unsafe_allow_html=True,
)

for _key, _val in DEFAULTS.items():
    st.session_state.setdefault(_key, _val)
    st.session_state[_key] = st.session_state[_key]


def html(markup: str) -> None:
    st.markdown(markup.replace("$", "&#36;"), unsafe_allow_html=True)


def money(x: float) -> str:
    return f"-${abs(x):,.0f}" if round(x) < 0 else f"${x:,.0f}"


def page_header(kicker: str, title: str, sub: str) -> None:
    html(
        f'<div class="al-kicker">{kicker}</div><div class="al-title">{title}</div>'
        f'<div class="al-sub">{sub}</div>'
    )


def grid(items: list[str]) -> None:
    html('<div class="al-cq"><div class="al-grid">' + "".join(items) + "</div></div>")


def kpi(tone: str, label: str, value: str, sub: str) -> str:
    return (
        f'<div class="al-kpi {tone}"><div class="lbl">{label}</div>'
        f'<div class="val">{value}</div><div class="sub">{sub}</div></div>'
    )


def stat(label: str, value: str, formula: str, tone: str = "") -> str:
    return (
        f'<div class="al-stat {tone}"><div class="lbl">{label}</div>'
        f'<div class="val">{value}</div><div class="fx">{formula}</div></div>'
    )


@dataclass(frozen=True)
class Model:
    false_acc: float
    sq_cost: float
    resid: float
    resid_cost: float
    build: float
    y1: float
    y2: float
    savings: float

    @property
    def break_even(self):
        if self.savings <= 0:
            return None
        return max(1, math.ceil(round(self.build / self.savings, 9)))

    @property
    def pct_change(self) -> float:
        return self.savings / self.sq_cost * 100 if self.sq_cost else 0.0

    def cumulative_net(self, year: int) -> float:
        return year * self.savings - self.build


def run_model(subs, fpr, cost, build, maint, avoid) -> Model:
    false_acc = subs * (fpr / 100)
    sq_cost = false_acc * cost
    resid = false_acc * (1 - avoid / 100)
    resid_cost = resid * cost
    y1 = build + maint + resid_cost
    y2 = maint + resid_cost
    return Model(false_acc, sq_cost, resid, resid_cost, build, y1, y2, sq_cost - y2)


def current_model() -> Model:
    return run_model(**{k: st.session_state[k] for k in DEFAULTS})


@st.cache_data
def load_cases() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH, keep_default_na=False)


@st.cache_data
def department_rates(df: pd.DataFrame) -> pd.DataFrame:
    g = (
        df.assign(flagged=df["Flagged by Detector"].eq("Yes"))
        .groupby("Department")
        .agg(Cases=("Submission ID", "count"), Flagged=("flagged", "sum"))
        .reset_index()
    )
    g["Rate"] = g["Flagged"] / g["Cases"]
    return g.sort_values(["Rate", "Cases"], ascending=False).reset_index(drop=True)


def style_fig(fig: go.Figure, height: int, margin: dict | None = None) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color=NAVY, size=13),
        margin=margin or dict(l=10, r=10, t=44, b=10),
        hoverlabel=dict(bgcolor="white", bordercolor=NAVY, font=dict(family=FONT, color=NAVY, size=13)),
    )
    return fig


def show_chart(fig: go.Figure, key: str) -> None:
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False}, key=key)


def section_overview() -> None:
    page_header(
        "Authorship Ledger",
        "Overview",
        "A process-provenance system for verifying human-AI collaborative academic and creative work.",
    )
    m = current_model()
    be = m.break_even
    cards = [
        ("red", "Status Quo Cost", money(m.sq_cost), "/ year, indefinitely"),
        ("navy", "Ledger Cost (Yr 2+)", money(m.y2), "/ year, after Year 1"),
        ("green" if m.savings > 0 else "red", "Annual Savings", money(m.savings), "starting Year 2"),
        ("navy", "Break-even Point", f"Year {be}" if be else "Not reached", "of adoption" if be else "at these assumptions"),
    ]
    grid([kpi(*card) for card in cards])

    is_default = all(st.session_state[k] == v for k, v in DEFAULTS.items())
    html(
        '<div class="al-note" style="margin-top:.7rem">'
        + (
            "Cards show the default assumptions."
            if is_default
            else "Cards reflect the assumptions you adjusted in the Expected Value Model."
        )
        + "</div>"
    )

    st.markdown("")
    st.markdown(
        "This dashboard supports the written analytics report for Authorship Ledger, a "
        "process-provenance system for verifying human-AI collaborative academic and creative "
        "work. All figures are fictional, modeled for this assignment. Adjust the assumptions in "
        "the Expected Value Model tab to see how the recommendation changes."
    )

    html('<div class="al-h3">What is inside</div>')
    a, b, c = st.columns(3, gap="medium")
    with a:
        html(
            '<div class="al-card tall"><b class="h">Expected Value Model</b>'
            "A live calculator. Move six assumptions and watch cost, savings and break-even recompute.</div>"
        )
    with b:
        html(
            '<div class="al-card tall"><b class="h">Build vs. Buy</b>'
            "A radar comparison of building the provenance engine against buying a timestamp authority.</div>"
        )
    with c:
        html(
            '<div class="al-card tall"><b class="h">Dataset Explorer</b>'
            "55 fictional case records. Filter, sort and see detector flag rate by department.</div>"
        )


def reset_assumptions() -> None:
    for k, v in DEFAULTS.items():
        st.session_state[k] = v


def ev_chart(m: Model) -> go.Figure:
    years = [1, 2, 3, 4]
    ledger = [m.y1, m.y2, m.y2, m.y2]
    cum = [m.cumulative_net(y) for y in years]
    be = m.break_even
    top = max(m.sq_cost, m.y1, m.y2) * 1.3 or 1

    fig = go.Figure()
    if be and be <= 4:
        fig.add_vrect(
            x0=be - 0.5,
            x1=be + 0.5,
            fillcolor=ICE,
            opacity=0.45,
            layer="below",
            line=dict(color=NAVY, width=1, dash="dash"),
        )
        fig.add_annotation(
            x=be, y=1, yref="paper", yanchor="bottom", showarrow=False,
            text=f"<b>Break-even: Year {be}</b>", font=dict(color=NAVY, size=13),
        )
    elif be:
        fig.add_annotation(
            x=1, xref="paper", xanchor="right", y=1, yref="paper", yanchor="bottom", showarrow=False,
            text=f"<b>Break-even: Year {be} (beyond this chart)</b>", font=dict(color=NAVY, size=13),
        )
    else:
        fig.add_annotation(
            x=1, xref="paper", xanchor="right", y=1, yref="paper", yanchor="bottom", showarrow=False,
            text="<b>No break-even at these assumptions</b>", font=dict(color=RED, size=13),
        )

    fig.add_annotation(
        x=4.45, y=m.sq_cost, xanchor="right", yanchor="bottom", showarrow=False, yshift=4,
        text=f"Status quo: {money(m.sq_cost)} / year", font=dict(color="rgba(30,39,97,.72)", size=12),
    )
    fig.add_trace(
        go.Scatter(
            x=years, y=[m.sq_cost] * 4, mode="lines", name="Status Quo (detection only)",
            line=dict(color=GRAY, width=4),
            hovertemplate="<b>Status quo</b><br>Year %{x}: $%{y:,.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=years, y=ledger, mode="lines+markers+text", name="Ledger Adoption",
            line=dict(color=NAVY, width=5),
            marker=dict(size=13, color=NAVY, line=dict(color="white", width=2)),
            text=[money(v) for v in ledger],
            textposition=["top center"] + ["bottom center" if m.y2 / top > 0.15 else "top center"] * 3,
            textfont=dict(color=NAVY, size=14, family=FONT),
            customdata=[money(c) for c in cum],
            hovertemplate=(
                "<b>Ledger adoption</b><br>Year %{x}: $%{y:,.0f}"
                "<br>Cumulative vs. status quo: %{customdata}<extra></extra>"
            ),
        )
    )
    fig.update_xaxes(
        tickvals=years, ticktext=[f"Year {y}" for y in years], range=[0.5, 4.5],
        showgrid=False, showline=True, linecolor=ICE, ticks="",
    )
    fig.update_yaxes(
        range=[0, top], tickprefix="$", tickformat=",.0f", gridcolor="rgba(202,220,252,.7)",
        zeroline=False, showline=False, title=dict(text="Expected annual cost", font=dict(size=12)),
    )
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
    )
    return style_fig(fig, 470, margin=dict(l=10, r=10, t=48, b=10))


@st.fragment
def ev_model() -> None:
    html('<div class="al-h3" style="margin-top:0">Assumptions</div>')
    r1 = st.columns(3, gap="medium")
    r2 = st.columns(3, gap="medium")
    with r1[0]:
        st.slider("Annual written submissions", 500, 10000, step=100, key="subs", format="%,d")
    with r1[1]:
        st.slider("Detector false-positive rate", 0.1, 10.0, step=0.1, key="fpr", format="%.1f%%")
    with r1[2]:
        st.slider("Admin cost per false accusation", 500, 10000, step=250, key="cost", format="$%,d")
    with r2[0]:
        st.slider("Ledger Year 1 build cost", 10000, 100000, step=5000, key="build", format="$%,d")
    with r2[1]:
        st.slider("Ledger annual maintenance", 5000, 50000, step=500, key="maint", format="$%,d")
    with r2[2]:
        st.slider("Dispute-avoidance rate after adoption", 50, 99, step=1, key="avoid", format="%d%%")
    st.button("Reset to defaults", on_click=reset_assumptions, key="reset_btn")

    m = current_model()
    be = m.break_even

    html('<div class="al-h3">Live results</div>')
    tiles = [
        ("Expected false accusations / year", f"{m.false_acc:,.1f}", "submissions × false-positive rate", ""),
        ("Status quo annual cost", money(m.sq_cost), "false accusations × cost per accusation", "alert"),
        ("Residual disputes / year", f"{m.resid:,.2f}", "false accusations × (1 − avoidance rate)", ""),
        ("Residual dispute cost / year", money(m.resid_cost), "residual disputes × cost per accusation", ""),
        ("Year 1 ledger cost", money(m.y1), "build + maintenance + residual dispute cost", ""),
        ("Year 2+ ledger cost", money(m.y2), "maintenance + residual dispute cost", ""),
        (
            "Annual savings (Year 2+)",
            money(m.savings),
            "status quo cost − Year 2+ ledger cost",
            "win" if m.savings > 0 else "bad",
        ),
        (
            "Break-even",
            f"Year {be}" if be else "Not reached",
            "first year cumulative savings cover the build cost",
            "",
        ),
    ]
    grid([stat(*tile) for tile in tiles])

    html('<div class="al-h3">Expected annual cost, Year 1 to Year 4</div>')
    show_chart(ev_chart(m), key="ev_chart")

    if m.savings > 0.5:
        verb = f"saves <b>{money(m.savings)} per year</b> starting in Year 2, a <b>{abs(m.pct_change):.0f}% reduction</b> in expected annual cost"
        tail = f" Cumulative break-even arrives in Year {be}."
    elif m.savings < -0.5:
        verb = f"costs <b>{money(-m.savings)} more per year</b> starting in Year 2, a <b>{abs(m.pct_change):.0f}% increase</b> in expected annual cost"
        tail = " It never breaks even against the status quo."
    else:
        verb = "is <b>cost-neutral</b> against the status quo starting in Year 2"
        tail = ""
    html(f'<div class="al-callout">At these assumptions, Authorship Ledger {verb}.{tail}</div>')


def section_ev_model() -> None:
    page_header(
        "Section 2",
        "Expected Value Model",
        "A live calculator. Every output below recomputes the moment a slider moves, "
        "so you can test how sensitive the recommendation is to each assumption.",
    )
    ev_model()


CRITERIA = ["Cost", "Time to Value", "Control & Differentiation", "Scalability & Risk"]
CRITERIA_WRAPPED = ["Cost", "Time to<br>Value", "Control &<br>Differentiation", "Scalability<br>& Risk"]
BUILD_SCORES = [2, 2, 5, 3]
BUY_SCORES = [5, 5, 1, 5]
BUILD_WHY = [
    "Highest cost: the team funds the engine's design, build and upkeep itself.",
    "Slowest path: nothing is live until the engine is built.",
    "Full control over the engine, the actual reason the product exists.",
    "Moderate: scaling and reliability risk stay with the in-house team.",
]
BUY_WHY = [
    "Lowest cost: the timestamp function is a solved problem elsewhere.",
    "Fastest path: an existing trusted timestamp authority is ready to use.",
    "Little control or differentiation: a commodity function others already offer.",
    "Proven at scale, with the operational risk carried by the provider.",
]


def radar_chart() -> go.Figure:
    def close(v):
        return v + v[:1]

    theta = close(CRITERIA_WRAPPED)
    buy_meta = close([[why, name] for why, name in zip(BUY_WHY, CRITERIA)])
    build_meta = close([[why, name] for why, name in zip(BUILD_WHY, CRITERIA)])
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=close(BUY_SCORES), theta=theta, name="Buy (Timestamp Authority)",
            mode="lines+markers", fill="toself", hoveron="points", fillcolor="rgba(183,195,224,.35)",
            line=dict(color=GRAY, width=3), marker=dict(size=10, color=GRAY, line=dict(color=NAVY, width=1)),
            customdata=buy_meta,
            hovertemplate="<b>%{customdata[1]}</b> · Buy<br>Score: <b>%{r}</b> / 5<br>%{customdata[0]}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=close(BUILD_SCORES), theta=theta, name="Build (Provenance Engine)",
            mode="lines+markers", fill="toself", hoveron="points", fillcolor="rgba(30,39,97,.14)",
            line=dict(color=NAVY, width=4), marker=dict(size=11, color=NAVY, line=dict(color="white", width=2)),
            customdata=build_meta,
            hovertemplate="<b>%{customdata[1]}</b> · Build<br>Score: <b>%{r}</b> / 5<br>%{customdata[0]}<extra></extra>",
        )
    )
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                range=[0, 5], tickvals=[1, 2, 3, 4, 5], gridcolor="rgba(202,220,252,.9)",
                linecolor=ICE, tickfont=dict(size=11, color="rgba(30,39,97,.6)"), angle=90,
            ),
            angularaxis=dict(gridcolor="rgba(202,220,252,.9)", linecolor=ICE, tickfont=dict(size=13, color=NAVY)),
        ),
        legend=dict(orientation="h", yanchor="top", y=-0.17, xanchor="center", x=0.5, font=dict(size=12)),
    )
    return style_fig(fig, 570, margin=dict(l=95, r=95, t=60, b=100))


def section_build_buy() -> None:
    page_header(
        "Section 3",
        "Build vs. Buy",
        "Two ways to deliver the product, scored 1 to 5 on four considerations. "
        "Higher favors that option. Hover any vertex for the score and the reason behind it.",
    )
    show_chart(radar_chart(), key="radar")
    rows = ""
    for crit, bs, ys in zip(CRITERIA, BUILD_SCORES, BUY_SCORES):
        crit_html = crit.replace("&", "&amp;")
        rows += (
            f"<tr><td>{crit_html}</td>"
            f'<td class="n {"w" if bs > ys else ""}">{bs}</td>'
            f'<td class="n {"w" if ys > bs else ""}">{ys}</td></tr>'
        )
    html(
        '<div class="al-h3" style="margin-top:.4rem">Scorecard</div>'
        '<table class="al-score"><tr><th>Consideration</th><th>Build</th><th>Buy</th></tr>'
        f"{rows}</table>"
        '<div class="al-note" style="margin-top:.6rem">Bold marks the higher-scoring option on each row.</div>'
    )
    st.markdown("")
    html(
        '<div class="al-callout"><b>Build the provenance engine internally, buy the trusted '
        "timestamp authority function.</b> Build wins on Control and Differentiation, the actual "
        "reason the product exists. Buy wins on Cost, Time to Value, and Scalability and Risk, "
        "since the timestamp function is a solved problem elsewhere.</div>"
    )


def rate_chart(rates: pd.DataFrame) -> go.Figure:
    top = rates["Rate"].idxmax()
    colors = [RED if i == top else GRAY for i in rates.index]
    labels = [f"{r.Rate:.1%}  ({int(r.Flagged)} of {int(r.Cases)})" for r in rates.itertuples()]
    fig = go.Figure(
        go.Bar(
            x=rates["Rate"], y=rates["Department"], orientation="h", marker_color=colors,
            text=labels, textposition="outside", cliponaxis=False,
            textfont=dict(color=NAVY, size=13, family=FONT),
            customdata=rates[["Flagged", "Cases"]].to_numpy(),
            hovertemplate=(
                "<b>%{y}</b><br>Flag rate: %{x:.1%}"
                "<br>%{customdata[0]} of %{customdata[1]} cases flagged<extra></extra>"
            ),
        )
    )
    fig.update_xaxes(range=[0, max(rates["Rate"].max() * 1.35, 0.05)], visible=False)
    fig.update_yaxes(autorange="reversed", showgrid=False, ticks="", tickfont=dict(size=14))
    fig.update_layout(bargap=0.35)
    return style_fig(fig, 340, margin=dict(l=10, r=10, t=10, b=10))


@st.fragment
def dataset_table(df: pd.DataFrame) -> None:
    depts = sorted(df["Department"].unique())
    chosen = st.multiselect("Department", depts, default=depts, key="f_dept")
    c2, c3 = st.columns([3, 2], gap="medium")
    with c2:
        status = st.segmented_control(
            "Flagged by detector", ["All", "Flagged", "Not flagged"], default="All", key="f_flag"
        ) or "All"
    with c3:
        query = st.text_input("Search Submission ID", placeholder="e.g. AL-1037", key="f_query")

    view = df[df["Department"].isin(chosen)]
    if status == "Flagged":
        view = view[view["Flagged by Detector"] == "Yes"]
    elif status == "Not flagged":
        view = view[view["Flagged by Detector"] == "No"]
    if query.strip():
        view = view[view["Submission ID"].str.contains(query.strip(), case=False, regex=False)]

    n_flag = int((view["Flagged by Detector"] == "Yes").sum())
    html(f'<div class="al-note" style="margin:.4rem 0 .5rem">Showing {len(view)} of {len(df)} cases, {n_flag} flagged by the detector.</div>')
    if view.empty:
        st.info("No cases match these filters.")
        return
    styled = view.style.map(
        lambda v: f"color: {RED}; font-weight: 700" if v == "Yes" else "",
        subset=["Flagged by Detector"],
    )
    st.dataframe(styled, width="stretch", hide_index=True, height=min(420, 36 * (len(view) + 1) + 4))


def section_dataset() -> None:
    page_header(
        "Section 4",
        "Fictional Dataset Explorer",
        "55 fictional Authorship Ledger case records. Each row is one submission and the "
        "process evidence the ledger captured for it.",
    )
    df = load_cases()
    rates = department_rates(df)

    html(
        '<div class="al-card" style="margin-bottom:1.4rem">Fictional dataset created for this '
        "assignment. The ~9% detector-flag rate is set above the real measured baseline "
        "(approximately 1%, per GradPilot, 2026) so the dataset contains enough flagged cases "
        "to illustrate the resolution workflow.</div>"
    )

    dataset_table(df)

    html('<div class="al-h3">Detector Flag Rate by Department</div>')
    html('<div class="al-note" style="margin-bottom:.3rem">Rate, not raw count, since department size varies.</div>')
    show_chart(rate_chart(rates), key="rate_chart")

    top = rates.iloc[0]
    html(
        f'<div class="al-note">{top["Department"]} ranks highest at {top["Rate"]:.1%}, but that rests on '
        f'{int(top["Flagged"])} flagged {"case" if int(top["Flagged"]) == 1 else "cases"} out of {int(top["Cases"])}. '
        "With samples this small, treat the ranking as illustrative, not statistical.</div>"
    )


with st.sidebar:
    html(
        '<div class="al-brand">Authorship Ledger</div>'
        '<div class="al-tag">Process provenance for human-AI collaborative work</div>'
    )
    section = st.radio("Section", SECTIONS, label_visibility="collapsed", key="section")
    html('<div class="al-note" style="margin-top:2rem">BUS 440 Final Assessment<br>All figures are fictional.</div>')

if section == "Overview":
    section_overview()
elif section == "Expected Value Model":
    section_ev_model()
elif section == "Build vs. Buy":
    section_build_buy()
else:
    section_dataset()

html(
    '<div class="al-footer">BUS 440 Final Assessment | Ephren Taylor | Dr. Ryan Wheaton | Authorship Ledger</div>'
)

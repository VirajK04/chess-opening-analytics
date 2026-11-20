import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Chess Opening Analytics", layout="wide")

BANDS = ["All ratings", "Under 1200", "1200-1599", "1600-1999", "2000+"]
BAND_ORDER = BANDS[1:]
METRICS = {
    "White win %": "white_win_pct",
    "Black win %": "black_win_pct",
    "White score vs rating expectation (pts)": "white_over_expected",
}


@st.cache_data
def load(name):
    return pd.read_csv(f"outputs/{name}.csv")


overall = load("01_white_vs_black")
ends = load("03_how_games_end_by_band")
length = load("04_game_length")
conf = load("09_family_confidence")
fam = load("05_opening_family_winrates").merge(
    load("07_family_adjusted")[["rating_band", "opening_family", "white_over_expected"]],
    on=["rating_band", "opening_family"])
name = load("06_opening_name_winrates").merge(
    load("08_name_adjusted")[["rating_band", "opening_name", "opening_family", "white_over_expected"]],
    on=["rating_band", "opening_name", "opening_family"])

# ---------------- Sidebar filters ----------------
st.sidebar.header("Filters")
band = st.sidebar.selectbox("Rating band", BANDS)
level = st.sidebar.radio("Opening level", ["Opening family", "Full opening name"])
metric_label = st.sidebar.radio("Rank openings by", list(METRICS))
metric = METRICS[metric_label]
min_games = st.sidebar.slider("Minimum games per opening", 50, 300, 50, step=10)
top_n = st.sidebar.slider("Openings per chart", 3, 15, 10)

label_col = "opening_family" if level == "Opening family" else "opening_name"
data = fam if level == "Opening family" else name
data = data[(data["rating_band"] == band) & (data["games"] >= min_games)]
chosen = st.sidebar.multiselect("Opening family (empty = all)", sorted(data["opening_family"].unique()))
if chosen:
    data = data[data["opening_family"].isin(chosen)]

# ---------------- Header and KPIs ----------------
total = int(overall.loc[overall["rating_band"] == "All ratings", "games"].iloc[0])
st.title("Chess Opening Win-Rate Analytics")
st.caption(f"{total:,} unique Lichess games (Kaggle: datasnaek/chess) after cleaning. "
           "Every number comes from the SQL exports in outputs/.")

row = overall[overall["rating_band"] == band].iloc[0]
k1, k2, k3, k4 = st.columns(4)
k1.metric("Games in band", f"{int(row['games']):,}")
k2.metric("White wins", f"{row['white_win_pct']:.1f}%")
k3.metric("Black wins", f"{row['black_win_pct']:.1f}%")
k4.metric("Draws", f"{row['draw_pct']:.1f}%")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Opening rankings", "Is it real? (95% intervals)", "How games end", "White vs Black"])

# ---------------- Tab 1: rankings ----------------
with tab1:
    st.subheader(f"Top and bottom openings: {band}")
    st.caption("An opening name describes the position both players reached. Sicilian Defense is Black's "
               "choice, so a low White win % there is good for Black. White also beats its rating "
               "expectation by about 1.5 points on average, so compare against that, not against zero. "
               "Only openings with the minimum number of games appear.")
    if len(data) < 2:
        st.info("Fewer than 2 openings reach the minimum games here. Try the 'Opening family' level, "
                "a lower minimum, or another rating band.")
    else:
        n = min(top_n, len(data) // 2)
        ranked = data.sort_values(metric, ascending=False)

        def chart(df, title, order):
            d = df.copy()
            d["label"] = d[label_col] + " (n=" + d["games"].astype(str) + ")"
            fig = px.bar(d, x=metric, y="label", orientation="h", title=title,
                         hover_data=["games", "white_win_pct", "black_win_pct", "draw_pct"])
            fig.update_layout(yaxis={"categoryorder": order, "title": ""},
                              xaxis_title=metric_label,
                              height=60 + 38 * len(d),
                              margin=dict(l=0, r=0, t=50, b=0))
            return fig

        left, right = st.columns(2)
        left.plotly_chart(chart(ranked.head(n), f"Top {n} by {metric_label}", "total ascending"))
        right.plotly_chart(chart(ranked.tail(n), f"Bottom {n} by {metric_label}", "total descending"))

        with st.expander("Full table for this selection"):
            cols = [label_col] + (["opening_family"] if label_col != "opening_family" else []) + [
                "games", "white_win_pct", "black_win_pct", "draw_pct",
                "white_over_expected", "avg_white_rating_edge"]
            st.dataframe(ranked[cols], hide_index=True)

# ---------------- Tab 2: confidence intervals ----------------
with tab2:
    st.subheader(f"Is the result bigger than chance? {band}")
    c = conf[conf["rating_band"] == band].copy()
    if chosen:
        c = c[c["opening_family"].isin(chosen)]
    if c.empty:
        st.info("No opening family has 150+ games in this selection.")
    else:
        c["verdict"] = c["clear_signal"].map(
            {True: "Clear signal (interval excludes 0)", False: "Within noise"})
        c["err_plus"] = c["ci_high"] - c["vs_baseline_pts"]
        c["err_minus"] = c["vs_baseline_pts"] - c["ci_low"]
        c = c.sort_values("vs_baseline_pts")
        fig = px.scatter(c, x="vs_baseline_pts", y="opening_family",
                         error_x="err_plus", error_x_minus="err_minus", color="verdict",
                         hover_data=["games", "ci_low", "ci_high"])
        fig.add_vline(x=0, line_dash="dash")
        fig.update_yaxes(categoryorder="array", categoryarray=list(c["opening_family"]))
        fig.update_layout(height=max(300, 32 * len(c) + 80), yaxis_title="",
                          xaxis_title="White score minus the band's normal White edge (points)")
        st.plotly_chart(fig)
        st.caption("Dots are the measured gap, lines are 95% intervals, and only families with 150+ games "
                   "are tested. Right of zero favours White, left favours Black. If the line crosses zero "
                   "we cannot separate the result from luck. About 1 in 20 tests looks clear by chance alone.")

# ---------------- Tab 3: endings and length ----------------
with tab3:
    a, b = st.columns(2)
    fig = px.bar(ends, x="rating_band", y="pct_within_band", color="ending",
                 category_orders={"rating_band": BAND_ORDER},
                 title="How games end (% of games in each band)")
    fig.update_layout(xaxis_title="", yaxis_title="% of games")
    a.plotly_chart(fig)

    ln = length[length["group_type"] == "Rating band"]
    fig = px.bar(ln, x="category", y="avg_full_moves",
                 category_orders={"category": BAND_ORDER},
                 hover_data=["games", "avg_plies"],
                 title="Average game length (full moves)")
    fig.update_layout(xaxis_title="", yaxis_title="Full moves")
    b.plotly_chart(fig)

    st.caption("Length is in full moves (plies divided by 2). These charts always show every band.")
    st.dataframe(length[length["group_type"] == "Ending"][["category", "games", "avg_full_moves"]],
                 hide_index=True)

# ---------------- Tab 4: White vs Black ----------------
with tab4:
    m = overall.melt(id_vars=["rating_band", "games"],
                     value_vars=["white_win_pct", "black_win_pct", "draw_pct"],
                     var_name="result", value_name="pct")
    m["result"] = m["result"].map({"white_win_pct": "White wins",
                                   "black_win_pct": "Black wins",
                                   "draw_pct": "Draw"})
    fig = px.bar(m, x="rating_band", y="pct", color="result", barmode="group",
                 category_orders={"rating_band": BANDS}, hover_data=["games"],
                 title="Result split by rating band")
    fig.update_layout(xaxis_title="", yaxis_title="% of games")
    st.plotly_chart(fig)
    st.caption("The 2000+ band has only 1,420 games, so its White-vs-Black gap is the least certain.")

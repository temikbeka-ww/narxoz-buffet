
"""TEMIKBEK — Narxoz Buffet Rush."""

from statistics import mean

import plotly.graph_objects as go
import streamlit as st

from model import (
    CHOICE_WEIGHTS,
    DEFAULT_OBSERVATIONS,
    Settings,
    all_buffets,
    best_buffet,
    evaluate,
    group_for,
    independence_check,
    law_of_total_probability,
)

st.set_page_config(
    page_title="TEMIKBEK | Narxoz Buffet Rush",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# DESIGN
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

html,body,[data-testid="stAppViewContainer"] {
    background:#F5F7FC!important;
    color:#20334D;
    font-family:Manrope,system-ui,sans-serif;
}
[data-testid="stHeader"] {
    background:transparent!important;
}
.block-container {
    max-width:1120px;
    padding-top:1.2rem;
    padding-bottom:3rem;
}
.hero {
    padding:27px 30px;
    border-radius:19px;
    background:linear-gradient(115deg,#123671,#2458B7);
    box-shadow:0 12px 32px #16418A22;
    margin:6px 0 22px;
}
.hero .brand {
    font-size:11px;
    color:#CEDFFF;
    letter-spacing:.15em;
    font-weight:800;
}
.hero h1 {
    font-size:clamp(27px,4vw,40px);
    font-weight:800;
    letter-spacing:-.045em;
    color:white!important;
    margin:15px 0 0;
}
.panel-title {
    font-size:18px;
    font-weight:800;
    color:#183A79;
    margin:0 0 13px;
}
[data-testid="stVerticalBlockBorderWrapper"] {
    border:1px solid #DCE5F2!important;
    border-radius:17px!important;
    background:white!important;
    box-shadow:0 7px 24px #173A7510;
}
[data-testid="stVerticalBlockBorderWrapper"] > div {
    background:transparent!important;
}
.stButton>button {
    border-radius:10px!important;
    min-height:42px!important;
    border:1px solid #CDDAEE!important;
    font-weight:750!important;
}
.stButton>button[kind="primary"] {
    background:#2556C4!important;
    color:#fff!important;
    border-color:#2556C4!important;
}
.stButton>button[kind="secondary"] {
    background:#F5F8FF!important;
    color:#214575!important;
}
.stButton>button:hover {
    border-color:#2556C4!important;
}
.prob {
    border:1px solid #CCDCFF;
    border-radius:15px;
    background:linear-gradient(120deg,#E9F0FF,#F5F8FF);
    padding:20px;
}
.prob .label {
    font-size:13px;
    color:#45628E;
    font-weight:750;
}
.prob .number {
    font-size:clamp(47px,6vw,70px);
    font-weight:800;
    letter-spacing:-.06em;
    line-height:1.15;
    color:#17449B;
    margin:10px 0;
}
.prob .description {
    font-size:13px;
    color:#3D5983;
}
.minicard {
    border-radius:12px;
    background:#F0F5FD;
    border:1px solid #DEE8F8;
    padding:15px;
    margin:14px 0;
}
.minicard b {
    font-size:23px;
    color:#184BA0;
}
.minicard small {
    display:block;
    color:#587096;
    margin-top:5px;
}
[data-testid="stMetric"] {
    background:#F5F8FE;
    padding:13px;
    border-radius:12px;
    border:1px solid #E1EAF7;
}
[data-testid="stMetricValue"] {
    color:#183E83;
}
[data-testid="stExpander"] {
    background:white;
    border:1px solid #DAE4F3;
    border-radius:12px;
}
[data-testid="stExpander"] summary {
    background:#F3F7FF!important;
    border-radius:10px;
}
[data-testid="stExpander"] summary p {
    color:#204275!important;
}
hr {
    border-color:#E1EAF6!important;
}
@media(max-width:650px) {
    .block-container {
        padding:10px 12px 30px;
    }
    .hero {
        padding:21px;
    }
    .hero h1 {
        font-size:28px;
    }
}
</style>
""", unsafe_allow_html=True)


# RU / EN
TEXT = {
    "ru": {
        "title": "Успеешь на следующую пару?",
        "route": "1. Выбери маршрут",
        "origin": "Где закончилась пара?",
        "buffet": "На каком этаже буфет?",
        "destination": "Где следующая пара?",
        "quick": "Быстрые сценарии",
        "same": "Остаться на 3-м",
        "cross": "С 5-го на 3-й",
        "best": "Лучший буфет",
        "settings": "2. Время и очередь",
        "queue": "Сколько минут ждёшь в очереди?",
        "eat": "Сколько минут хочешь поесть?",
        "more": "Дополнительные настройки",
        "break": "Перемена (мин)",
        "buy": "Покупка и оплата (мин)",
        "pace": "Темп ходьбы",
        "fast": "Быстрый",
        "normal": "Обычный",
        "slow": "Медленный",
        "result": "Твой прогноз",
        "prob": "Шанс успеть на пару вовремя",
        "cases": "Успеваешь в {s} из {n} вариантов очереди",
        "remain": "Остаётся на еду",
        "short": "Не хватает времени",
        "walk": "Переходы",
        "wait": "Очередь",
        "purchase": "Покупка",
        "total": "Всё время с едой",
        "min": "мин",
        "how": "Как рассчитано?",
        "compare": "3. Сравни буфеты",
        "floor": "Этаж буфета",
        "distribution": "4. Время ожидания",
        "wait_axis": "Минуты ожидания",
        "share": "Доля случаев, %",
        "math": "Формулы Week 1–5",
        "w1": "События и комбинации маршрутов",
        "w2": "Вероятность",
        "w3": "Условная вероятность",
        "w3full": "Полная вероятность",
        "w4": "Независимость событий",
        "w5": "Распределение частот",
    },
    "en": {
        "title": "Will you make it to class on time?",
        "route": "1. Choose your route",
        "origin": "Previous class floor?",
        "buffet": "Buffet floor?",
        "destination": "Next class floor?",
        "quick": "Quick scenarios",
        "same": "Stay on floor 3",
        "cross": "Floor 5 to 3",
        "best": "Best buffet",
        "settings": "2. Time and queue",
        "queue": "How many minutes in the queue?",
        "eat": "How many minutes to eat?",
        "more": "More settings",
        "break": "Break (min)",
        "buy": "Buying and paying (min)",
        "pace": "Walking speed",
        "fast": "Fast",
        "normal": "Normal",
        "slow": "Slow",
        "result": "Your forecast",
        "prob": "Chance of arriving on time",
        "cases": "On time in {s} of {n} queue cases",
        "remain": "Time available for eating",
        "short": "Time shortfall",
        "walk": "Walking",
        "wait": "Queue",
        "purchase": "Buying",
        "total": "Total including food",
        "min": "min",
        "how": "Show calculation",
        "compare": "3. Compare buffets",
        "floor": "Buffet floor",
        "distribution": "4. Waiting time",
        "wait_axis": "Waiting time (min)",
        "share": "Share of cases, %",
        "math": "Formulas: Weeks 1–5",
        "w1": "Events and route combinations",
        "w2": "Probability",
        "w3": "Conditional probability",
        "w3full": "Total probability",
        "w4": "Independence of events",
        "w5": "Frequency distribution",
    },
}


# DEFAULT VALUES
DEFAULTS = {
    "lang": "ru",
    "origin": 3,
    "buffet": 3,
    "destination": 3,
    "break_minutes": 15,
    "buy_minutes": 1.0,
    "eat_minutes": 5.0,
    "pace": "normal",
}

for key, value in DEFAULTS.items():
    if (
        st.session_state.get(key) is None
        or (
            key == "pace"
            and st.session_state.get(key)
            not in ("fast", "normal", "slow")
        )
    ):
        st.session_state[key] = value

if st.session_state.lang not in ("ru", "en"):
    st.session_state.lang = "ru"


# QUEUE DATA
# Keep queue values separate from temporary slider keys.
MEANS = {
    key: mean(values)
    for key, values in DEFAULT_OBSERVATIONS.items()
}

if "queue_values" not in st.session_state:
    st.session_state.queue_values = {
        key: round(avg * 2) / 2
        for key, avg in MEANS.items()
    }

for group, avg in MEANS.items():
    value = st.session_state.queue_values.get(group)

    if (
        not isinstance(value, (int, float))
        or not 0 <= value <= 25
    ):
        st.session_state.queue_values[group] = (
            round(avg * 2) / 2
        )


# LANGUAGE SWITCH
st.radio(
    "Language",
    ("ru", "en"),
    key="lang",
    horizontal=True,
    format_func=lambda x: x.upper(),
    label_visibility="collapsed",
)

t = TEXT[st.session_state.lang]


# HEADER
st.markdown(
    f"""
    <div class="hero">
        <div class="brand">
            T / TEMIKBEK · PROJECT ONE · NARXOZ
        </div>
        <h1>{t['title']}</h1>
    </div>
    """,
    unsafe_allow_html=True,
)


# FUNCTIONS
def change_floor(key, floor):
    st.session_state[key] = floor


def set_route(origin, buffet, destination):
    st.session_state.update(
        origin=origin,
        buffet=buffet,
        destination=destination,
    )


def settings_now():
    s = st.session_state

    return Settings(
        origin=s.origin,
        buffet=s.buffet,
        destination=s.destination,
        break_minutes=s.break_minutes,
        buy_minutes=s.buy_minutes,
        eat_minutes=s.eat_minutes,
        pace_factor={
            "fast": 0.85,
            "normal": 1.0,
            "slow": 1.2,
        }.get(s.pace, 1.0),
    )


def queue_data():
    output = {}

    for group, vals in DEFAULT_OBSERVATIONS.items():
        chosen = st.session_state.queue_values.get(
            group,
            round(MEANS[group] * 2) / 2,
        )

        difference = chosen - MEANS[group]

        output[group] = [
            max(0.0, round(v + difference, 2))
            for v in vals
        ]

    return output


def on_wait_change(group):
    value = st.session_state.get(f"_wait_{group}")

    if isinstance(value, (int, float)):
        st.session_state.queue_values[group] = float(value)


def select_best():
    st.session_state.buffet = best_buffet(
        settings_now(),
        queue_data(),
    )


def floor_buttons(label, key):
    st.markdown(f"**{label}**")

    columns = st.columns(5, gap="small")

    for i, col in enumerate(columns, start=1):
        with col:
            st.button(
                str(i),
                key=f"floor_{key}_{i}",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state[key] == i
                    else "secondary"
                ),
                on_click=change_floor,
                args=(key, i),
            )


# MAIN LAYOUT
left, right = st.columns(
    [1.05, 0.95],
    gap="large",
    vertical_alignment="top",
)

with left:
    with st.container(border=True):
        st.markdown(
            f"<div class='panel-title'>{t['route']}</div>",
            unsafe_allow_html=True,
        )

        floor_buttons(t["origin"], "origin")
        floor_buttons(t["buffet"], "buffet")
        floor_buttons(t["destination"], "destination")

        st.markdown(f"**{t['quick']}**")

        a, b, c = st.columns(3, gap="small")

        a.button(
            t["same"],
            key="same",
            on_click=set_route,
            args=(3, 3, 3),
            use_container_width=True,
        )

        b.button(
            t["cross"],
            key="cross",
            on_click=set_route,
            args=(5, 3, 5),
            use_container_width=True,
        )

        c.button(
            t["best"],
            key="best",
            on_click=select_best,
            use_container_width=True,
        )

    with st.container(border=True):
        st.markdown(
            f"<div class='panel-title'>{t['settings']}</div>",
            unsafe_allow_html=True,
        )

        group = group_for(
            st.session_state.buffet,
            st.session_state.origin,
        )

        st.markdown(f"**{t['queue']}**")

        st.slider(
            "Queue waiting minutes",
            min_value=0.0,
            max_value=25.0,
            value=float(
                st.session_state.queue_values[group]
            ),
            step=0.5,
            key=f"_wait_{group}",
            on_change=on_wait_change,
            args=(group,),
            label_visibility="collapsed",
        )

        st.markdown(f"**{t['eat']}**")

        st.slider(
            "Eating minutes",
            min_value=0.0,
            max_value=15.0,
            step=0.5,
            key="eat_minutes",
            label_visibility="collapsed",
        )

        with st.expander(t["more"]):
            st.markdown(f"**{t['break']}**")

            st.slider(
                "Break minutes",
                min_value=5,
                max_value=30,
                step=1,
                key="break_minutes",
                label_visibility="collapsed",
            )

            st.markdown(f"**{t['buy']}**")

            st.slider(
                "Buying minutes",
                min_value=0.5,
                max_value=4.0,
                step=0.5,
                key="buy_minutes",
                label_visibility="collapsed",
            )

            st.markdown(f"**{t['pace']}**")

            st.radio(
                "Walking pace",
                ("fast", "normal", "slow"),
                key="pace",
                format_func=lambda x: t[x],
                horizontal=True,
                label_visibility="collapsed",
            )


# CALCULATIONS
settings = settings_now()
data = queue_data()

forecast = evaluate(settings, data)
comparisons = all_buffets(settings, data)

probability = forecast.probability * 100
unit = t["min"]


# RESULTS
with right:
    with st.container(border=True):
        st.markdown(
            f"<div class='panel-title'>{t['result']}</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="prob">
                <div class="label">{t['prob']}</div>
                <div class="number">
                    {probability:.1f}%
                </div>
                <div class="description">
                    {t['cases'].format(
                        s=forecast.success_count,
                        n=forecast.sample_count
                    )}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.progress(float(forecast.probability))

        if forecast.average_margin >= 0:
            label = t["remain"]
            duration = max(
                0.0,
                forecast.average_eating_window
            )
        else:
            label = t["short"]
            duration = abs(forecast.average_margin)

        st.markdown(
            f"""
            <div class="minicard">
                <b>{duration:.1f} {unit}</b>
                <small>{label}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

        m1, m2 = st.columns(2)
        m3, m4 = st.columns(2)

        m1.metric(
            t["walk"],
            f"{forecast.travel:.1f} {unit}",
        )

        m2.metric(
            t["wait"],
            f"{forecast.average_wait:.1f} {unit}",
        )

        m3.metric(
            t["purchase"],
            f"{settings.buy_minutes:.1f} {unit}",
        )

        m4.metric(
            t["total"],
            f"{forecast.average_total:.1f} {unit}",
        )

        with st.expander(t["how"]):
            st.write(
                f"{forecast.travel:.1f} + "
                f"{forecast.average_wait:.1f} + "
                f"{settings.buy_minutes:.1f} + "
                f"{settings.eat_minutes:.1f} = "
                f"{forecast.average_total:.1f} {unit}"
            )

            st.write(
                f"P ≈ {forecast.success_count}/"
                f"{forecast.sample_count} = "
                f"{probability:.1f}%"
            )


# CHARTS
st.divider()

chart_left, chart_right = st.columns(
    2,
    gap="large",
)

with chart_left:
    with st.container(border=True):
        st.markdown(
            f"<div class='panel-title'>{t['compare']}</div>",
            unsafe_allow_html=True,
        )

        values = [
            r.probability * 100
            for r in comparisons
        ]

        figure = go.Figure(
            go.Bar(
                x=[
                    str(i)
                    for i in range(1, 6)
                ],
                y=values,
                text=[
                    f"{v:.0f}%"
                    for v in values
                ],
                textposition="outside",
                marker_color=[
                    "#2456C4"
                    if i == settings.buffet
                    else "#95B2EB"
                    for i in range(1, 6)
                ],
            )
        )

        figure.update_layout(
            template="plotly_white",
            height=290,
            showlegend=False,
            margin=dict(
                l=12, r=10, t=25, b=30
            ),
            xaxis=dict(
                title=t["floor"],
                showgrid=False,
            ),
            yaxis=dict(
                title="%",
                range=[0, 112],
                gridcolor="#E5ECF6",
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        st.plotly_chart(
            figure,
            use_container_width=True,
            config={"displayModeBar": False},
        )


with chart_right:
    with st.container(border=True):
        st.markdown(
            f"<div class='panel-title'>{t['distribution']}</div>",
            unsafe_allow_html=True,
        )

        waits = forecast.observed_waits
        width = 2 if max(waits) <= 20 else 5

        positions = range(
            0,
            int(max(waits) // width) * width + 1,
            width,
        )

        items = [
            (
                low,
                sum(
                    low <= v < low + width
                    for v in waits
                ),
            )
            for low in positions
        ]

        items = [
            (low, count)
            for low, count in items
            if count > 0
        ]

        portions = [
            100 * count / len(waits)
            for _, count in items
        ]

        fig = go.Figure(
            go.Bar(
                x=[
                    f"{low}–{low + width}"
                    for low, _ in items
                ],
                y=portions,
                marker_color="#159A96",
                text=[
                    f"{p:.1f}%"
                    for p in portions
                ],
                textposition="outside",
            )
        )

        fig.update_layout(
            template="plotly_white",
            height=290,
            showlegend=False,
            margin=dict(
                l=12, r=10, t=25, b=30
            ),
            xaxis=dict(
                title=t["wait_axis"],
                showgrid=False,
            ),
            yaxis=dict(
                title=t["share"],
                range=[0, 112],
                ticksuffix="%",
                gridcolor="#E5ECF6",
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False},
        )


# FORMULAS WEEK 1–5
with st.expander(t["math"]):
    st.markdown(f"**Week 1 — {t['w1']}**")
    st.latex(r"N=5\times5\times5=125")

    st.markdown(f"**Week 2 — {t['w2']}**")
    st.latex(
        r"\widehat P(A)=\frac{n(A)}{n}"
    )
    st.write(
        f"{forecast.success_count}/"
        f"{forecast.sample_count} = "
        f"{probability:.1f}%"
    )

    st.markdown(f"**Week 3 — {t['w3']}**")
    st.latex(
        r"P(A\mid B)=\frac{P(A\cap B)}{P(B)}"
    )

    st.markdown(f"**Week 3 — {t['w3full']}**")
    st.latex(
        r"P(A)=\sum_{i=1}^{5}P(A\mid B_i)P(B_i)"
    )

    p_total = law_of_total_probability(
        comparisons,
        CHOICE_WEIGHTS["equal"],
    )

    st.write(
        f"P(A) = {100 * p_total:.1f}%"
    )

    st.markdown(f"**Week 4 — {t['w4']}**")
    st.latex(
        r"P(A\cap B)\stackrel{?}{=}P(A)P(B)"
    )

    _, _, joint, product = independence_check(
        comparisons,
        CHOICE_WEIGHTS["equal"],
    )

    sign = (
        "="
        if abs(joint - product) < 1e-12
        else "≠"
    )

    st.write(
        f"{joint:.4f} {sign} {product:.4f}"
    )

    st.markdown(f"**Week 5 — {t['w5']}**")
    st.latex(
        r"f_i=\frac{n_i}{n}"
    )


"""TEMIKBEK — Narxoz Buffet Rush."""

from statistics import mean

import streamlit as st
import plotly.graph_objects as go

from model import (
    DEFAULT_OBSERVATIONS,
    CHOICE_WEIGHTS,
    Settings,
    evaluate,
    all_buffets,
    best_buffet,
    law_of_total_probability,
    independence_check,
    group_for,
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

html, body, [data-testid="stAppViewContainer"] {
    background: #F5F7FC !important;
    color: #192B47;
    font-family: Manrope, system-ui, sans-serif;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

.block-container {
    max-width: 1120px;
    padding-top: 1.1rem;
    padding-bottom: 3rem;
}

h1, h2, h3, p {
    font-family: Manrope, system-ui, sans-serif;
}

.hero {
    background: linear-gradient(
        125deg, #123773 0%, #2255AE 100%
    );
    color: #FFFFFF;
    border-radius: 20px;
    padding: 27px 30px;
    margin: 6px 0 22px;
    box-shadow: 0 16px 35px #163C7825;
}

.hero .brand {
    color: #C9DEFF;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: .14em;
}

.hero .heading {
    font-size: clamp(26px, 3.8vw, 39px);
    font-weight: 800;
    letter-spacing: -.045em;
    line-height: 1.2;
    margin: 14px 0 0;
    color: white;
}

.panel-title {
    color: #183B79;
    font-size: 18px;
    font-weight: 800;
    margin: 0 0 12px;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid #DCE5F3 !important;
    background: #FFFFFF !important;
    border-radius: 17px !important;
    box-shadow: 0 6px 20px #183A7510;
}

[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: transparent !important;
}

.stButton > button {
    min-height: 43px;
    border-radius: 10px !important;
    border: 1px solid #C9D7ED !important;
    font-weight: 750 !important;
    transition: transform .12s, border-color .12s;
}

.stButton > button[kind="primary"] {
    background: #2455BE !important;
    color: white !important;
    border-color: #2455BE !important;
}

.stButton > button[kind="secondary"] {
    background: #F6F9FF !important;
    color: #214477 !important;
}

.stButton > button:hover {
    border-color: #2455BE !important;
    transform: translateY(-1px);
}

.probability {
    border-radius: 16px;
    padding: 19px 21px;
    background: linear-gradient(
        130deg, #EAF1FF, #F3F7FF
    );
    border: 1px solid #D0E0FF;
}

.probability .name {
    color: #49648E;
    font-size: 13px;
    font-weight: 750;
}

.probability .number {
    color: #18469A;
    font-size: clamp(45px, 6vw, 68px);
    font-weight: 800;
    letter-spacing: -.055em;
    line-height: 1.25;
    margin: 5px 0;
}

.probability .detail {
    color: #425A80;
    font-size: 13px;
}

.mini-stat {
    background: #F3F7FE;
    border: 1px solid #E0E9F8;
    border-radius: 13px;
    padding: 13px 16px;
    margin-top: 13px;
}

.mini-stat .value {
    font-size: 22px;
    font-weight: 800;
    color: #1B4BA7;
}

.mini-stat .label {
    font-size: 12px;
    color: #567094;
    margin-top: 2px;
}

[data-testid="stMetric"] {
    background: #F5F8FE;
    border: 1px solid #E2EAF7;
    border-radius: 12px;
    padding: 11px 13px;
}

[data-testid="stMetricValue"] {
    color: #1A427D;
}

[data-testid="stExpander"] {
    border: 1px solid #DAE4F2;
    border-radius: 12px;
    background: white;
}

[data-testid="stExpander"] summary {
    background: #F5F8FF !important;
    border-radius: 10px;
}

[data-testid="stExpander"] summary p {
    color: #28466F !important;
}

[data-testid="stProgressBar"] > div > div {
    background-color: #2455BE;
}

hr {
    border-color: #E2EAF5 !important;
}

@media (max-width: 650px) {
    .block-container {
        padding: 9px 13px 28px;
    }
    .hero {
        padding: 20px;
    }
    .probability .number {
        font-size: 48px;
    }
}
</style>
""", unsafe_allow_html=True)


# RU / EN
LANG = {
    "title": (
        "Успеешь на следующую пару?",
        "Will you make it to class on time?"
    ),
    "route": ("1. Твой маршрут", "1. Your route"),
    "start": (
        "Где закончилась пара?",
        "Previous class floor"
    ),
    "buffet": (
        "На каком этаже буфет?",
        "Buffet floor"
    ),
    "end": (
        "Где следующая пара?",
        "Next class floor"
    ),
    "shortcuts": ("Быстрый выбор", "Quick routes"),
    "three": ("Остаться на 3-м", "Stay on floor 3"),
    "five": ("С 5-го на 3-й", "Floor 5 to 3"),
    "best": ("Лучший буфет", "Best buffet"),
    "settings": (
        "2. Время и очередь",
        "2. Time and queue"
    ),
    "queue": (
        "Ожидание в очереди, мин",
        "Queue waiting time, min"
    ),
    "eat": (
        "Время на еду, мин",
        "Eating time, min"
    ),
    "extra": ("Другие настройки", "More settings"),
    "break": (
        "Длительность перемены, мин",
        "Break duration, min"
    ),
    "buy": (
        "Покупка и оплата, мин",
        "Buying and paying, min"
    ),
    "pace": ("Скорость ходьбы", "Walking speed"),
    "fast": ("Быстро", "Fast"),
    "normal": ("Обычно", "Normal"),
    "slow": ("Не спеша", "Slow"),
    "forecast": ("Твой результат", "Your result"),
    "chance": (
        "Шанс успеть на пару",
        "Chance of arriving on time"
    ),
    "cases": (
        "Успеваешь в {success} из {total} вариантов очереди",
        "On time in {success} of {total} queue cases"
    ),
    "left": (
        "Остаётся на еду",
        "Time available for eating"
    ),
    "late": (
        "Не хватает времени",
        "Time shortfall"
    ),
    "walk": ("Переходы", "Walking"),
    "wait": ("Очередь", "Queue"),
    "total": ("Общее время", "Total time"),
    "calc": ("Расчёт", "Calculation"),
    "compare": (
        "3. Сравнение этажей",
        "3. Compare buffet floors"
    ),
    "floor": ("Этаж", "Floor"),
    "distribution": (
        "4. Время в очереди",
        "4. Queue waiting times"
    ),
    "waitaxis": (
        "Ожидание, мин",
        "Waiting time, min"
    ),
    "frequency": (
        "Доля вариантов, %",
        "Share of cases, %"
    ),
    "formulas": (
        "Формулы Week 1–5",
        "Formulas: Weeks 1–5"
    ),
    "w1": ("Маршруты и события", "Routes and events"),
    "w2": (
        "Частота успеха",
        "Share of successful cases"
    ),
    "w3": (
        "Условная вероятность",
        "Conditional probability"
    ),
    "w3b": (
        "Полная вероятность",
        "Total probability"
    ),
    "w4": (
        "Независимость событий",
        "Independence of events"
    ),
    "w5": (
        "Частоты ожидания",
        "Waiting-time frequencies"
    ),
    "math_note": (
        "Для расчётов используются демонстрационные варианты очереди, а не измерения Narxoz.",
        "Calculations use example queue times, not measured Narxoz data."
    ),
}


# DEFAULT VALUES
DEFAULT_STATE = {
    "lang": "ru",
    "origin": 3,
    "buffet": 3,
    "destination": 3,
    "break_minutes": 15,
    "buy_minutes": 1.0,
    "eat_minutes": 5.0,
    "pace": "normal",
}

for key, default in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = default

if st.session_state.get("lang") not in ("ru", "en"):
    st.session_state.lang = "ru"

if st.session_state.get("pace") not in (
    "fast", "normal", "slow"
):
    st.session_state.pace = "normal"


# QUEUE DATA
MEANS = {
    key: mean(values)
    for key, values in DEFAULT_OBSERVATIONS.items()
}

for group, average in MEANS.items():
    key = f"waiting_{group}"
    value = st.session_state.get(key)

    if (
        not isinstance(value, (int, float))
        or not 0 <= value <= 25
    ):
        st.session_state[key] = round(average * 2) / 2


# LANGUAGE SWITCH
st.radio(
    "Language",
    ["ru", "en"],
    key="lang",
    horizontal=True,
    format_func=lambda value: value.upper(),
    label_visibility="collapsed",
)

language_index = (
    0 if st.session_state.lang == "ru" else 1
)

t = {
    key: pair[language_index]
    for key, pair in LANG.items()
}


# HEADER
st.markdown(
    f"""
    <div class="hero">
        <div class="brand">
            T / TEMIKBEK · PROJECT ONE · NARXOZ
        </div>
        <div class="heading">{t['title']}</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# FUNCTIONS
def change_floor(key, floor):
    st.session_state[key] = floor


def route(origin, buffet, destination):
    st.session_state.update(
        origin=origin,
        buffet=buffet,
        destination=destination,
    )


def current_settings():
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
            "normal": 1,
            "slow": 1.2,
        }.get(s.pace, 1),
    )


def adjusted_observations():
    result = {}

    for group, times in DEFAULT_OBSERVATIONS.items():
        shift = (
            st.session_state[f"waiting_{group}"]
            - MEANS[group]
        )

        result[group] = [
            max(0, round(value + shift, 2))
            for value in times
        ]

    return result


def choose_best():
    st.session_state.buffet = best_buffet(
        current_settings(),
        adjusted_observations(),
    )


def floor_buttons(text, key):
    st.markdown(f"**{text}**")
    columns = st.columns(5, gap="small")

    for floor, col in enumerate(columns, 1):
        with col:
            st.button(
                str(floor),
                key=f"{key}_{floor}",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state[key] == floor
                    else "secondary"
                ),
                on_click=change_floor,
                args=(key, floor),
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

        floor_buttons(t["start"], "origin")
        floor_buttons(t["buffet"], "buffet")
        floor_buttons(t["end"], "destination")

        st.markdown(f"**{t['shortcuts']}**")

        btn1, btn2, btn3 = st.columns(
            3, gap="small"
        )

        btn1.button(
            t["three"],
            on_click=route,
            args=(3, 3, 3),
            use_container_width=True,
        )

        btn2.button(
            t["five"],
            on_click=route,
            args=(5, 3, 5),
            use_container_width=True,
        )

        btn3.button(
            t["best"],
            on_click=choose_best,
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
            "Queue minutes",
            min_value=0.0,
            max_value=25.0,
            step=0.5,
            key=f"waiting_{group}",
            label_visibility="collapsed",
        )

        st.markdown(f"**{t['eat']}**")

        st.slider(
            "Eat minutes",
            min_value=0.0,
            max_value=15.0,
            step=0.5,
            key="eat_minutes",
            label_visibility="collapsed",
        )

        with st.expander(t["extra"]):
            st.markdown(f"**{t['break']}**")

            st.slider(
                "Break",
                min_value=5,
                max_value=30,
                key="break_minutes",
                label_visibility="collapsed",
            )

            st.markdown(f"**{t['buy']}**")

            st.slider(
                "Buy",
                min_value=0.5,
                max_value=4.0,
                step=0.5,
                key="buy_minutes",
                label_visibility="collapsed",
            )

            st.markdown(f"**{t['pace']}**")

            st.radio(
                "Pace",
                ["fast", "normal", "slow"],
                key="pace",
                horizontal=True,
                format_func=lambda value: t[value],
                label_visibility="collapsed",
            )


# PROBABILITY CALCULATION
settings = current_settings()
observations = adjusted_observations()

forecast = evaluate(settings, observations)
comparisons = all_buffets(settings, observations)

probability = 100 * forecast.probability


# RESULT
with right:
    with st.container(border=True):
        st.markdown(
            f"<div class='panel-title'>{t['forecast']}</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="probability">
                <div class="name">{t['chance']}</div>
                <div class="number">
                    {probability:.1f}%
                </div>
                <div class="detail">
                    {t['cases'].format(
                        success=forecast.success_count,
                        total=forecast.sample_count
                    )}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.progress(float(forecast.probability))

        margin = forecast.average_margin

        if margin >= 0:
            main_value = forecast.average_eating_window
            caption = t["left"]
        else:
            main_value = abs(margin)
            caption = t["late"]

        unit = (
            "мин"
            if st.session_state.lang == "ru"
            else "min"
        )

        st.markdown(
            f"""
            <div class="mini-stat">
                <div class="value">
                    {max(0, main_value):.1f} {unit}
                </div>
                <div class="label">{caption}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        one, two = st.columns(2)
        three, four = st.columns(2)

        one.metric(
            t["walk"],
            f"{forecast.travel:.1f} {unit}",
        )

        two.metric(
            t["wait"],
            f"{forecast.average_wait:.1f} {unit}",
        )

        three.metric(
            t["buy"],
            f"{settings.buy_minutes:.1f} {unit}",
        )

        four.metric(
            t["total"],
            f"{forecast.average_total:.1f} {unit}",
        )

        with st.expander(t["calc"]):
            st.write(
                f"{forecast.travel:.1f} + "
                f"{forecast.average_wait:.1f} + "
                f"{settings.buy_minutes:.1f} + "
                f"{settings.eat_minutes:.1f} "
                f"= {forecast.average_total:.1f} {unit}"
            )

            st.write(
                f"P ≈ {forecast.success_count} / "
                f"{forecast.sample_count} "
                f"= {probability:.1f}%"
            )


# CHARTS
st.divider()

graph1, graph2 = st.columns(2, gap="large")

with graph1:
    with st.container(border=True):
        st.markdown(
            f"<div class='panel-title'>{t['compare']}</div>",
            unsafe_allow_html=True,
        )

        pcts = [
            result.probability * 100
            for result in comparisons
        ]

        chart = go.Figure(
            go.Bar(
                x=[str(i) for i in range(1, 6)],
                y=pcts,
                marker_color=[
                    "#2455BE"
                    if i == settings.buffet
                    else "#9BB8EB"
                    for i in range(1, 6)
                ],
                text=[
                    f"{value:.0f}%"
                    for value in pcts
                ],
                textposition="outside",
            )
        )

        chart.update_layout(
            template="plotly_white",
            height=290,
            showlegend=False,
            margin=dict(l=12, r=10, t=25, b=30),
            xaxis=dict(
                title=t["floor"],
                showgrid=False,
            ),
            yaxis=dict(
                title="%",
                range=[0, 112],
                gridcolor="#E4EAF6",
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        st.plotly_chart(
            chart,
            use_container_width=True,
            config={"displayModeBar": False},
        )


with graph2:
    with st.container(border=True):
        st.markdown(
            f"<div class='panel-title'>{t['distribution']}</div>",
            unsafe_allow_html=True,
        )

        waits = forecast.observed_waits

        width = 2 if max(waits) <= 20 else 5

        starts = range(
            0,
            int(max(waits) // width) * width + 1,
            width,
        )

        ranges = [
            (
                start,
                sum(
                    start <= value < start + width
                    for value in waits
                ),
            )
            for start in starts
        ]

        active = [
            (start, count)
            for start, count in ranges
            if count
        ]

        bars = [
            100 * count / len(waits)
            for _, count in active
        ]

        chart = go.Figure(
            go.Bar(
                x=[
                    f"{start}–{start + width}"
                    for start, _ in active
                ],
                y=bars,
                marker_color="#189B96",
                text=[
                    f"{value:.1f}%"
                    for value in bars
                ],
                textposition="outside",
            )
        )

        chart.update_layout(
            template="plotly_white",
            height=290,
            showlegend=False,
            margin=dict(l=12, r=10, t=25, b=30),
            xaxis=dict(
                title=t["waitaxis"],
                showgrid=False,
            ),
            yaxis=dict(
                title=t["frequency"],
                range=[0, 110],
                ticksuffix="%",
                gridcolor="#E4EAF6",
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        st.plotly_chart(
            chart,
            use_container_width=True,
            config={"displayModeBar": False},
        )


# WEEKS 1–5
with st.expander(t["formulas"]):
    st.markdown(f"**Week 1 — {t['w1']}**")
    st.latex(r"N=5\times5\times5=125")

    st.markdown(f"**Week 2 — {t['w2']}**")
    st.latex(r"\widehat{P}(A)=\frac{n(A)}{n}")
    st.write(
        f"{forecast.success_count} / "
        f"{forecast.sample_count} = "
        f"{probability:.1f}%"
    )

    st.markdown(f"**Week 3 — {t['w3']}**")
    st.latex(
        r"P(A\mid B)=\frac{P(A\cap B)}{P(B)}"
    )

    st.markdown(f"**Week 3 — {t['w3b']}**")
    st.latex(
        r"P(A)=\sum_{i=1}^{5}P(A\mid B_i)P(B_i)"
    )

    combined = law_of_total_probability(
        comparisons,
        CHOICE_WEIGHTS["equal"],
    )
    st.write(
        f"P(A) = {combined:.3f} "
        f"= {combined * 100:.1f}%"
    )

    st.markdown(f"**Week 4 — {t['w4']}**")
    st.latex(r"P(A\cap B)=P(A)\cdot P(B)")

    p_a, p_b, joint, product = independence_check(
        comparisons,
        CHOICE_WEIGHTS["equal"],
    )

    sign = (
        "="
        if abs(joint - product) < 1e-12
        else "≠"
    )
    st.write(f"{joint:.4f} {sign} {product:.4f}")

    st.markdown(f"**Week 5 — {t['w5']}**")
    st.latex(r"f_i=\frac{n_i}{n}")

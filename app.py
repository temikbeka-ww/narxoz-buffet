
from __future__ import annotations

from statistics import mean
import plotly.graph_objects as go
import streamlit as st

from model import (
    CHOICE_WEIGHTS,
    DEFAULT_OBSERVATIONS,
    group_for,
    Settings,
    all_buffets,
    best_buffet,
    evaluate,
    independence_check,
    law_of_total_probability,
)

st.set_page_config(
    page_title="TEMIKBEK | Narxoz Buffet Rush",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Original visual design
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap');
html,body,[data-testid="stAppViewContainer"]{font-family:'DM Sans',sans-serif;color:#213046;background:#F6F8FC!important}
[data-testid="stHeader"]{background:transparent!important}
.block-container{max-width:1120px;padding-top:1.25rem;padding-bottom:2.8rem}
.stApp h1,.stApp h2,.stApp h3,.stApp p,.stApp label{color:#213046}
h1,h2,h3{font-family:Manrope,system-ui,sans-serif;letter-spacing:-.025em}
.hero{border-radius:19px;padding:22px 28px;margin:8px 0 20px;background:#173E80;color:white}
.hero .sub{font:800 12px Manrope,sans-serif;letter-spacing:.16em;color:#BCD5FF}
.hero h1{font-size:clamp(29px,4vw,41px);margin:10px 0 0;color:white!important;font-weight:800}
.hero .lead{margin:9px 0 0;color:#EEF4FF!important;font-size:14px}
.paneltitle{font:800 19px Manrope,sans-serif;color:#1B3662;margin:0 0 8px}
[data-testid="stVerticalBlockBorderWrapper"]{border:1px solid #D9E1ED!important;background:white!important;border-radius:17px!important;box-shadow:0 8px 24px #1A325808}
[data-testid="stVerticalBlockBorderWrapper"]>div{background:transparent!important}
.stButton>button{border-radius:10px!important;min-height:44px!important;font-weight:800!important;border:1px solid #CDD8E8!important}
.stButton>button[kind="primary"]{background:#2556C3!important;border-color:#2556C3!important;color:white!important}
.stButton>button[kind="secondary"]{background:#F5F7FC!important;color:#1B3662!important}
.stButton>button:hover{border-color:#2556C3!important}
[data-testid="stMetric"]{padding:10px 12px;border-radius:13px;background:#F1F5FD;border:1px solid #DFE8F9}
[data-testid="stMetricValue"]{color:#183A79}
.resultbox{background:#EAF0FE;border:1px solid #CAD9FF;border-radius:14px;padding:18px;margin:10px 0}
.resultbox small{color:#476189;font-weight:800;font-size:12px}
.resultbox strong{display:block;color:#184187;font:800 clamp(29px,4vw,44px) Manrope,sans-serif;margin:6px 0}
.resultbox span{color:#314B77;font-size:13px}
.scorebox{background:#F3F7FC;padding:12px 15px;border-radius:12px;margin:10px 0}
.scorebox strong{font:800 21px Manrope;color:#1C4FA7}
.scorebox p{font-size:12px;color:#425672;margin:4px 0 0}
.formula{background:#F1F5FB;border-radius:12px;padding:11px 13px;min-height:112px}
.formula b{font-size:13px;color:#163B7A}.formula p{font-size:12px;color:#425672;margin:5px 0}.formula code{font-size:12px;color:#26458A}
label[data-testid="stWidgetLabel"]{font-weight:700}
hr{border-color:#DEE6F1!important}
[data-testid="stExpander"]{background:white;border:1px solid #D9E1ED;border-radius:12px}
[data-testid="stExpander"] summary{background:#F2F6FD!important;color:#1B365D!important;border-radius:10px}
[data-testid="stExpander"] summary p{color:#1B365D!important}
small.mininote{color:#64778D}
@media(max-width:650px){.hero{padding:21px}.hero h1{font-size:29px}.block-container{padding:10px 13px 27px}}
</style>
""", unsafe_allow_html=True)


# Text translations: Russian, English
TEXT = {
    "header": (
        "Успеешь на следующую пару?",
        "Can you make it to class on time?"
    ),
    "lead": (
        "Выбери три этажа и настрой очередь. Результат обновится сразу.",
        "Choose three floors and adjust the queue. Results update automatically."
    ),
    "route": ("1. Выбери маршрут", "1. Choose your route"),
    "origin": (
        "На каком этаже закончилась пара?",
        "Where was your previous class?"
    ),
    "buffet": (
        "На каком этаже купишь еду?",
        "Which floor is your buffet on?"
    ),
    "dest": (
        "На каком этаже следующая пара?",
        "Where is your next class?"
    ),
    "quick": ("Готовые варианты", "Quick examples"),
    "same": ("Остаться на 3-м", "Stay on floor 3"),
    "cross": ("С 5-го на 3-й", "From floor 5 to 3"),
    "safe": ("Выбрать лучший буфет", "Choose the best buffet"),
    "settings": (
        "2. Сколько времени у тебя есть?",
        "2. How much time do you have?"
    ),
    "queue": (
        "Сколько обычно ждёшь в этом буфете?",
        "How long do you usually wait here?"
    ),
    "eat": (
        "Сколько минут хочешь поесть?",
        "How many minutes do you want to eat?"
    ),
    "more": ("Дополнительные настройки", "Other settings"),
    "break": (
        "Длительность перемены, мин",
        "Break length (min)"
    ),
    "buy": (
        "Время покупки и оплаты, мин",
        "Buying and paying (min)"
    ),
    "pace": ("Скорость ходьбы", "Walking speed"),
    "fast": ("Быстрая", "Fast"),
    "normal": ("Обычная", "Normal"),
    "slow": ("Медленная", "Slow"),
    "result": ("Твой прогноз", "Your forecast"),
    "enough": ("Успеваешь на пару", "You can make it to class"),
    "short": ("Можешь опоздать", "You may arrive late"),
    "left": (
        "После очереди и покупки на еду остаётся",
        "Time left to eat after queueing and paying"
    ),
    "need": (
        "Для желаемого времени на еду не хватает",
        "Extra time needed for your planned meal"
    ),
    "time": ("мин", "min"),
    "walk": ("На переходы", "Walking"),
    "avg_wait": ("Очередь", "Queue"),
    "buying": ("Покупка", "Buying"),
    "full": (
        "На всё вместе (с едой)",
        "Total (including eating)"
    ),
    "rate_title": (
        "Шанс успеть на пару вовремя",
        "Chance of arriving to class on time"
    ),
    "rate_text": (
        "Успеваешь в {s} из {n} вариантов очереди",
        "On time in {s} out of {n} queue cases"
    ),
    "zero": (
        "Даже без очереди времени не хватит. Попробуй ближайший буфет.",
        "Even without a queue, there isn't enough time. Try a closer buffet."
    ),
    "zero_queue": (
        "При текущей очереди не укладываешься. Уменьши ожидание или выбери другой этаж.",
        "This queue takes too long. Reduce the wait or choose another floor."
    ),
    "how": ("Как получен результат", "How it was calculated"),
    "line": (
        "Дорога {walk:.1f} + очередь {wait:.1f} + покупка {buy:.1f} + еда {eat:.1f} = {full:.1f} мин",
        "Walking {walk:.1f} + waiting {wait:.1f} + buying {buy:.1f} + eating {eat:.1f} = {full:.1f} min"
    ),
    "rate_formula": (
        "Успели в {s} из {n} вариантов времени ожидания: {s}/{n} = {p:.0f}%.",
        "On time in {s} of {n} wait-time cases: {s}/{n} = {p:.0f}%."
    ),
    "compare": ("3. Сравни буфеты", "3. Compare buffets"),
    "compare_sub": (
        "Как меняется результат, если пойти за едой на другой этаж?",
        "What happens if you choose another buffet floor?"
    ),
    "frequency": (
        "4. Вероятность ожидания",
        "4. Waiting-time percentages"
    ),
    "frequency_sub": (
        "Какой процент вариантов попадает в каждый интервал ожидания",
        "Percentage of cases in each waiting-time interval"
    ),
    "min_label": ("минуты ожидания", "waiting time (min)"),
    "freq_label": ("доля вариантов, %", "share of cases, %"),
    "math": (
        "Какие формулы используются (Week 1–5)",
        "Formulas used (Weeks 1–5)"
    ),
    "m1": ("Week 1 · Варианты маршрута", "Week 1 · Route combinations"),
    "m1d": (
        "5 этажей для начала, буфета и следующей пары: 125 вариантов.",
        "Five choices for each of three floors: 125 possible routes."
    ),
    "m2": ("Week 2 · Вероятность", "Week 2 · Probability"),
    "m2d": (
        "Доля успешных вариантов среди всех вариантов ожидания.",
        "Share of on-time outcomes across all wait-time cases."
    ),
    "m3": (
        "Week 3 · Условная вероятность",
        "Week 3 · Conditional probability"
    ),
    "m3d": (
        "Успеешь, если выберешь конкретный этаж буфета.",
        "On-time probability given a specific buffet floor."
    ),
    "m3b": (
        "Week 3 · Полная вероятность",
        "Week 3 · Total probability"
    ),
    "m3bd": (
        "Учитываем, с какой частотой выбирают каждый буфет.",
        "Combine all floors weighted by how often they're chosen."
    ),
    "m4": (
        "Week 4 · Независимость",
        "Week 4 · Independence"
    ),
    "m4d": (
        "Проверяем, влияет ли выбор третьего этажа на успех.",
        "Check whether floor 3 choice is related to being on time."
    ),
    "m5": ("Week 5 · Частоты", "Week 5 · Frequencies"),
    "m5d": (
        "Подсчитываем, сколько раз встречается каждый интервал ожидания.",
        "Count how many wait times belong to each interval."
    ),
    "examples": (
        "Пример с равным выбором пяти буфетов",
        "Example assuming equal buffet-choice rates"
    ),
    "ind": (
        "События независимы в выбранной модели.",
        "Events are independent in the selected model."
    ),
    "not_ind": (
        "События зависимы в выбранной модели.",
        "Events are dependent in the selected model."
    ),
    "floor": ("этаж", "floor"),
}


# Application state
DEFAULTS = {
    "lang": "ru",
    "origin": 3,
    "buffet": 3,
    "destination": 3,
    "break_minutes": 15,
    "eat_minutes": 5.0,
    "buy_minutes": 1.0,
    "pace": "normal",
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

if st.session_state.pace not in ("fast", "normal", "slow"):
    st.session_state.pace = "normal"

if st.session_state.lang not in ("ru", "en"):
    st.session_state.lang = "ru"


# Queue values for each floor
BASE_MEANS = {
    key: mean(values)
    for key, values in DEFAULT_OBSERVATIONS.items()
}

for group in DEFAULT_OBSERVATIONS:
    key = f"waiting_{group}"
    value = st.session_state.get(key)

    if not isinstance(value, (int, float)):
        st.session_state[key] = round(BASE_MEANS[group] * 2) / 2


# Language switch
st.radio(
    "Language",
    ("ru", "en"),
    key="lang",
    horizontal=True,
    format_func=lambda value: value.upper(),
    label_visibility="collapsed",
)

language_index = 0 if st.session_state.lang == "ru" else 1

t = {
    key: pair[language_index]
    for key, pair in TEXT.items()
}


# Header
st.markdown(
    f"""
    <div class="hero">
        <div class="sub">
            T / TEMIKBEK · PROJECT ONE · NARXOZ
        </div>
        <h1>{t["header"]}</h1>
        <p class="lead">{t["lead"]}</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# Mathematical settings
def adjusted_data():
    updated = {}

    for group, cases in DEFAULT_OBSERVATIONS.items():
        target = float(
            st.session_state.get(
                f"waiting_{group}",
                BASE_MEANS[group]
            )
        )
        difference = target - BASE_MEANS[group]

        updated[group] = [
            max(0.0, round(value + difference, 2))
            for value in cases
        ]

    return updated


def current_settings():
    values = st.session_state

    pace = {
        "fast": 0.85,
        "normal": 1.0,
        "slow": 1.2,
    }.get(values.get("pace"), 1.0)

    return Settings(
        origin=int(values.get("origin", 3)),
        buffet=int(values.get("buffet", 3)),
        destination=int(values.get("destination", 3)),
        break_minutes=float(values.get("break_minutes", 15)),
        buy_minutes=float(values.get("buy_minutes", 1)),
        eat_minutes=float(values.get("eat_minutes", 5)),
        pace_factor=pace,
    )


# Button actions
def change_floor(slot, floor):
    st.session_state[slot] = floor


def select_route(origin, buffet, destination, reset=False):
    st.session_state.update(
        origin=origin,
        buffet=buffet,
        destination=destination,
    )

    if reset:
        st.session_state.update(
            break_minutes=15,
            buy_minutes=1.0,
            eat_minutes=5.0,
            pace="normal",
        )


def select_best_buffet():
    st.session_state.buffet = best_buffet(
        current_settings(),
        adjusted_data(),
    )


def floor_buttons(title, slot):
    st.markdown(f"**{title}**")

    columns = st.columns(5, gap="small")

    for floor, column in enumerate(columns, start=1):
        with column:
            selected = st.session_state[slot] == floor

            st.button(
                str(floor),
                key=f"floor_{slot}_{floor}",
                use_container_width=True,
                type="primary" if selected else "secondary",
                on_click=change_floor,
                args=(slot, floor),
            )


# Main layout
left, right = st.columns(
    [1.02, 0.98],
    gap="large",
    vertical_alignment="top",
)

with left:
    with st.container(border=True):
        st.markdown(
            f'<div class="paneltitle">{t["route"]}</div>',
            unsafe_allow_html=True,
        )

        floor_buttons(t["origin"], "origin")
        floor_buttons(t["buffet"], "buffet")
        floor_buttons(t["dest"], "destination")

        st.markdown(f'**{t["quick"]}**')

        buttons = st.columns(3, gap="small")

        with buttons[0]:
            st.button(
                t["same"],
                key="scenario_same",
                use_container_width=True,
                on_click=select_route,
                args=(3, 3, 3, True),
            )

        with buttons[1]:
            st.button(
                t["cross"],
                key="scenario_cross",
                use_container_width=True,
                on_click=select_route,
                args=(5, 3, 5, True),
            )

        with buttons[2]:
            st.button(
                t["safe"],
                key="scenario_best",
                use_container_width=True,
                on_click=select_best_buffet,
            )

    with st.container(border=True):
        st.markdown(
            f'<div class="paneltitle">{t["settings"]}</div>',
            unsafe_allow_html=True,
        )

        group = group_for(
            st.session_state.buffet,
            st.session_state.origin,
        )

        wait_key = f"waiting_{group}"

        st.markdown(f'**{t["queue"]}**')

        st.slider(
            "Queue waiting time",
            min_value=0.0,
            max_value=25.0,
            step=0.5,
            key=wait_key,
            label_visibility="collapsed",
        )

        st.markdown(f'**{t["eat"]}**')

        st.slider(
            "Desired eating time",
            min_value=0.0,
            max_value=15.0,
            step=0.5,
            key="eat_minutes",
            label_visibility="collapsed",
        )

        with st.expander(t["more"]):
            st.markdown(f'**{t["break"]}**')

            st.slider(
                "Break duration",
                min_value=5,
                max_value=30,
                step=1,
                key="break_minutes",
                label_visibility="collapsed",
            )

            st.markdown(f'**{t["buy"]}**')

            st.slider(
                "Buying time",
                min_value=0.5,
                max_value=4.0,
                step=0.5,
                key="buy_minutes",
                label_visibility="collapsed",
            )

            st.markdown(f'**{t["pace"]}**')

            st.radio(
                "Pace",
                ("fast", "normal", "slow"),
                key="pace",
                horizontal=True,
                format_func=lambda value: t[value],
                label_visibility="collapsed",
            )


# Probability calculation
settings = current_settings()
observations = adjusted_data()

result = evaluate(settings, observations)
all_results = all_buffets(settings, observations)

percent = 100 * result.probability


# Results panel
with right:
    with st.container(border=True):
        st.markdown(
            f'<div class="paneltitle">{t["result"]}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="resultbox">
                <small>{t["rate_title"]}</small>
                <strong>{percent:.1f}%</strong>
                <span>
                    {t["rate_text"].format(
                        s=result.success_count,
                        n=result.sample_count
                    )}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.progress(float(result.probability))

        if result.average_margin >= 0:
            value = max(0, result.average_eating_window)
            description = t["enough"]
            caption = t["left"]
        else:
            value = abs(result.average_margin)
            description = t["short"]
            caption = t["need"]

        st.markdown(
            f"""
            <div class="scorebox">
                <strong>{value:.1f} {t["time"]}</strong>
                <p>{caption} · {description}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        metrics = st.columns(2)
        metrics2 = st.columns(2)

        metrics[0].metric(
            t["walk"],
            f"{result.travel:.1f} {t['time']}"
        )

        metrics[1].metric(
            t["avg_wait"],
            f"{result.average_wait:.1f} {t['time']}"
        )

        metrics2[0].metric(
            t["buying"],
            f"{settings.buy_minutes:.1f} {t['time']}"
        )

        metrics2[1].metric(
            t["full"],
            f"{result.average_total:.1f} {t['time']}"
        )

        if percent == 0:
            minimum = (
                result.travel
                + settings.buy_minutes
                + settings.eat_minutes
            )

            if minimum > settings.break_minutes:
                st.info(t["zero"])
            else:
                st.info(t["zero_queue"])

        with st.expander(t["how"]):
            st.write(
                t["line"].format(
                    walk=result.travel,
                    wait=result.average_wait,
                    buy=settings.buy_minutes,
                    eat=settings.eat_minutes,
                    full=result.average_total,
                )
            )

            st.write(
                t["rate_formula"].format(
                    s=result.success_count,
                    n=result.sample_count,
                    p=percent,
                )
            )


# Chart 1: Compare buffet floors
st.divider()

chart_left, chart_right = st.columns(2, gap="large")

with chart_left:
    with st.container(border=True):
        st.markdown(
            f'<div class="paneltitle">{t["compare"]}</div>',
            unsafe_allow_html=True,
        )

        st.caption(t["compare_sub"])

        probabilities = [
            result_item.probability * 100
            for result_item in all_results
        ]

        fig = go.Figure(
            go.Bar(
                x=[str(floor) for floor in range(1, 6)],
                y=probabilities,
                marker_color=[
                    "#2556C3"
                    if floor == settings.buffet
                    else "#89AAE6"
                    for floor in range(1, 6)
                ],
                text=[
                    f"{value:.0f}%"
                    for value in probabilities
                ],
                textposition="outside",
            )
        )

        fig.update_layout(
            template="plotly_white",
            height=280,
            showlegend=False,
            margin=dict(l=10, r=10, t=28, b=28),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                title=t["floor"],
                showgrid=False,
            ),
            yaxis=dict(
                title="%",
                range=[0, 112],
                gridcolor="#E6ECF3",
            ),
            font=dict(color="#263B59"),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False},
        )


# Chart 2: Waiting-time distribution
with chart_right:
    with st.container(border=True):
        st.markdown(
            f'<div class="paneltitle">{t["frequency"]}</div>',
            unsafe_allow_html=True,
        )

        st.caption(t["frequency_sub"])

        waits = result.observed_waits
        step = 2 if max(waits) <= 20 else 5

        maximum = max(waits)
        bins = list(
            range(
                0,
                int(maximum // step) * step + 1,
                step,
            )
        )

        counts = [
            sum(
                low <= value < low + step
                for value in waits
            )
            for low in bins
        ]

        used = [
            (low, count)
            for low, count in zip(bins, counts)
            if count > 0
        ]

        total_cases = len(waits)

        percentages = [
            100 * count / total_cases
            for _, count in used
        ]

        frequency_chart = go.Figure(
            go.Bar(
                x=[
                    f"{low}–{low + step}"
                    for low, _ in used
                ],
                y=percentages,
                marker_color="#1E9A91",
                text=[
                    f"{value:.1f}%"
                    for value in percentages
                ],
                textposition="outside",
                customdata=[
                    count for _, count in used
                ],
                hovertemplate=(
                    f"%{{x}} {t['min_label']}: "
                    f"%{{y:.1f}}%"
                    f"<br>%{{customdata}} / "
                    f"{total_cases}<extra></extra>"
                ),
            )
        )

        frequency_chart.update_layout(
            template="plotly_white",
            height=280,
            showlegend=False,
            margin=dict(l=10, r=10, t=28, b=28),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                title=t["min_label"],
                showgrid=False,
            ),
            yaxis=dict(
                title=t["freq_label"],
                range=[0, 110],
                dtick=20,
                ticksuffix="%",
                gridcolor="#E6ECF3",
            ),
            font=dict(color="#263B59"),
        )

        st.plotly_chart(
            frequency_chart,
            use_container_width=True,
            config={"displayModeBar": False},
        )


# Mathematical formulas: Weeks 1–5
with st.expander(t["math"]):
    st.markdown(
        f'**{t["m1"]}** · `N = 5 × 5 × 5 = 125`'
    )
    st.caption(t["m1d"])

    st.markdown(
        f'**{t["m2"]}** · `P(A) = n(A) / N`'
    )
    st.caption(t["m2d"])

    st.write(
        f"{result.success_count} / "
        f"{result.sample_count} = {percent:.1f}%"
    )

    st.markdown(
        f'**{t["m3"]}** · '
        '`P(A|B) = P(A∩B) / P(B)`'
    )
    st.caption(t["m3d"])

    st.markdown(
        f'**{t["m3b"]}** · '
        '`P(A) = Σ P(A|Bᵢ) × P(Bᵢ)`'
    )
    st.caption(t["m3bd"])

    overall = law_of_total_probability(
        all_results,
        CHOICE_WEIGHTS["equal"],
    )

    st.write(
        f'{t["examples"]}: {overall * 100:.1f}%'
    )

    st.markdown(
        f'**{t["m4"]}** · '
        '`P(A∩B) = P(A) × P(B)`'
    )
    st.caption(t["m4d"])

    p_a, p_b, joint, product = independence_check(
        all_results,
        CHOICE_WEIGHTS["equal"],
    )

    sign = "=" if abs(joint - product) < 1e-12 else "≠"

    st.write(
        f"{joint:.4f} {sign} {product:.4f} — "
        + (t["ind"] if sign == "=" else t["not_ind"])
    )

    st.markdown(
        f'**{t["m5"]}** · `fᵢ = nᵢ / n`'
    )
    st.caption(t["m5d"])
    st.caption(t["small_note"])

"""TEMIKBEK · Narxoz Buffet Rush — single-page, bilingual classroom app.

Run with `streamlit run app.py`. All starter queue cases are illustrative;
percentages are the share of those cases satisfying the selected route.
"""
from __future__ import annotations

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
    independence_check,
    law_of_total_probability,
)

st.set_page_config(page_title="TEMIKBEK | Narxoz Buffet Rush", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
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
label[data-testid="stWidgetLabel"] {font-weight:700}
hr{border-color:#DEE6F1!important}
[data-testid="stExpander"]{background:white;border:1px solid #D9E1ED;border-radius:12px}
[data-testid="stExpander"] summary{background:#F2F6FD!important;color:#1B365D!important;border-radius:10px}
[data-testid="stExpander"] summary p{color:#1B365D!important}
small.mininote{color:#64778D}
@media(max-width:650px){.hero{padding:21px}.hero h1{font-size:29px}.block-container{padding:10px 13px 27px}}
</style>
""",
    unsafe_allow_html=True,
)

I18N = {
    "ru": {
        "header": "Успеешь на следующую пару?",
        "lead": "Выбери три этажа и настрой очередь. Результат обновится сразу.",
        "route": "1. Выбери маршрут",
        "origin": "На каком этаже закончилась пара?",
        "buffet": "На каком этаже купишь еду?",
        "dest": "На каком этаже следующая пара?",
        "quick": "Готовые варианты",
        "same": "Остаться на 3-м",
        "cross": "С 5-го на 3-й",
        "safe": "Выбрать лучший буфет",
        "settings": "2. Сколько времени у тебя есть?",
        "queue": "Сколько обычно ждёшь в этом буфете?",
        "eat": "Сколько минут хочешь поесть?",
        "more": "Дополнительные настройки",
        "break": "Длительность перемены, мин",
        "buy": "Время покупки и оплаты, мин",
        "pace": "Скорость ходьбы",
        "fast": "Быстрая",
        "normal": "Обычная",
        "slow": "Медленная",
        "result": "Твой прогноз",
        "enough": "Успеваешь на пару",
        "short": "Можешь опоздать",
        "left": "После очереди и покупки на еду остаётся",
        "need": "Для желаемого времени на еду не хватает",
        "time": "мин",
        "walk": "На переходы",
        "avg_wait": "Очередь",
        "buying": "Покупка",
        "full": "На всё вместе (с едой)",
        "rate_title": "Шанс успеть на пару вовремя",
        "rate_text": "Успеваешь в {s} из {n} вариантов очереди",
        "zero": "Даже без очереди времени не хватит. Попробуй ближайший буфет.",
        "zero_queue": "При текущей очереди не укладываешься. Уменьши ожидание или выбери другой этаж.",
        "how": "Как получен результат",
        "line": "Дорога {walk:.1f} + очередь {wait:.1f} + покупка {buy:.1f} + еда {eat:.1f} = {full:.1f} мин",
        "rate_formula": "Успели в {s} из {n} вариантов времени ожидания: {s}/{n} = {p:.0f}%.",
        "compare": "3. Сравни буфеты",
        "compare_sub": "Как меняется результат, если пойти за едой на другой этаж?",
        "chart_rate": "Успеешь на пару, % вариантов",
        "frequency": "4. Вероятность ожидания",
        "frequency_sub": "Какой процент вариантов попадает в каждый интервал ожидания",
        "min_label": "минуты ожидания",
        "freq_label": "доля вариантов, %",
        "math": "Какие формулы используются (Week 1–5)",
        "m1": "Week 1 · Варианты маршрута",
        "m1d": "5 этажей для начала, буфета и следующей пары: 125 вариантов.",
        "m2": "Week 2 · Вероятность",
        "m2d": "Доля успешных вариантов среди всех вариантов ожидания.",
        "m3": "Week 3 · Условная вероятность",
        "m3d": "Успеешь, если выберешь конкретный этаж буфета.",
        "m3b": "Week 3 · Полная вероятность",
        "m3bd": "Учитываем, с какой частотой выбирают каждый буфет.",
        "m4": "Week 4 · Независимость",
        "m4d": "Проверяем, влияет ли выбор третьего этажа на успех.",
        "m5": "Week 5 · Частоты",
        "m5d": "Подсчитываем, сколько раз встречается каждый интервал ожидания.",
        "examples": "Пример с равным выбором пяти буфетов",
        "ind": "События независимы в выбранной модели.",
        "not_ind": "События зависимы в выбранной модели.",
        "small_note": "Проценты рассчитаны по задаваемым вариантам ожидания, а не по статистике посещений Narxoz.",
        "floor": "этаж",
    },
    "en": {
        "header": "Can you make it to class on time?",
        "lead": "Choose three floors and adjust the queue. Results update automatically.",
        "route": "1. Choose your route",
        "origin": "Where was your previous class?",
        "buffet": "Which floor is your buffet on?",
        "dest": "Where is your next class?",
        "quick": "Quick examples",
        "same": "Stay on floor 3",
        "cross": "From floor 5 to 3",
        "safe": "Choose the best buffet",
        "settings": "2. How much time do you have?",
        "queue": "How long do you usually wait here?",
        "eat": "How many minutes do you want to eat?",
        "more": "Other settings",
        "break": "Break length (min)",
        "buy": "Buying and paying (min)",
        "pace": "Walking speed",
        "fast": "Fast",
        "normal": "Normal",
        "slow": "Slow",
        "result": "Your forecast",
        "enough": "You can make it to class",
        "short": "You may arrive late",
        "left": "Time left to eat after queueing and paying",
        "need": "Extra time needed for your planned meal",
        "time": "min",
        "walk": "Walking",
        "avg_wait": "Queue",
        "buying": "Buying",
        "full": "Total (including eating)",
        "rate_title": "Chance of arriving to class on time",
        "rate_text": "On time in {s} out of {n} queue cases",
        "zero": "Even without a queue, there isn't enough time. Try a closer buffet.",
        "zero_queue": "This queue takes too long. Reduce the wait or choose another floor.",
        "how": "How it was calculated",
        "line": "Walking {walk:.1f} + waiting {wait:.1f} + buying {buy:.1f} + eating {eat:.1f} = {full:.1f} min",
        "rate_formula": "On time in {s} of {n} wait-time cases: {s}/{n} = {p:.0f}%.",
        "compare": "3. Compare buffets",
        "compare_sub": "What happens if you choose another buffet floor?",
        "chart_rate": "On-time share, % of cases",
        "frequency": "4. Waiting-time percentages",
        "frequency_sub": "Percentage of cases in each waiting-time interval",
        "min_label": "waiting time (min)",
        "freq_label": "share of cases, %",
        "math": "Formulas used (Weeks 1–5)",
        "m1": "Week 1 · Route combinations",
        "m1d": "Five choices for each of three floors: 125 possible routes.",
        "m2": "Week 2 · Probability",
        "m2d": "Share of on-time outcomes across all wait-time cases.",
        "m3": "Week 3 · Conditional probability",
        "m3d": "On-time probability given a specific buffet floor.",
        "m3b": "Week 3 · Total probability",
        "m3bd": "Combine all floors weighted by how often they're chosen.",
        "m4": "Week 4 · Independence",
        "m4d": "Check whether floor 3 choice is related to being on time.",
        "m5": "Week 5 · Frequencies",
        "m5d": "Count how many wait times belong to each interval.",
        "examples": "Example assuming equal buffet-choice rates",
        "ind": "Events are independent in the selected model.",
        "not_ind": "Events are dependent in the selected model.",
        "small_note": "Percentages are based on adjustable queue cases, not measured Narxoz visitor statistics.",
        "floor": "floor",
    },
}

# Keep all stored values separate from localized widget labels.
DEFAULTS = {
    "lang": "ru", "origin": 3, "buffet": 3, "destination": 3,
    "break_minutes": 15, "eat_minutes": 5.0, "buy_minutes": 1.0,
    "pace": "normal",
}
for k, value in DEFAULTS.items():
    if k not in st.session_state or (k == "pace" and st.session_state.get(k) not in ("fast", "normal", "slow")):
        st.session_state[k] = value

# Each buffet has its own understandable queue length; no CSV or raw table in the main UI.
QUEUE_GROUPS = tuple(DEFAULT_OBSERVATIONS)
BASE_MEANS = {key: mean(DEFAULT_OBSERVATIONS[key]) for key in QUEUE_GROUPS}
for group in QUEUE_GROUPS:
    k = f"waiting_{group}"
    if k not in st.session_state or not isinstance(st.session_state.get(k), (int, float)):
        st.session_state[k] = round(BASE_MEANS[group] * 2) / 2

# Stable values, stable key: switching languages does not alter the widgets' stored values.
st.radio("Language", ("ru", "en"), key="lang", horizontal=True,
         format_func=lambda v: "RU" if v == "ru" else "EN", label_visibility="collapsed")
t = I18N[st.session_state.get("lang", "ru")]

st.markdown(f"<div class='hero'><div class='sub'>T / TEMIKBEK · PROJECT ONE · NARXOZ</div>"
            f"<h1>{t['header']}</h1><p class='lead'>{t['lead']}</p></div>",
            unsafe_allow_html=True)


def group_for_ui(buffet_floor: int, start_floor: int) -> str:
    return "3_same" if buffet_floor == 3 and start_floor == 3 else "3_other" if buffet_floor == 3 else str(buffet_floor)


def adjusted_data() -> dict[str, list[float]]:
    updated = {}
    for group, cases in DEFAULT_OBSERVATIONS.items():
        target = float(st.session_state.get(f"waiting_{group}", BASE_MEANS[group]))
        offset = target - BASE_MEANS[group]
        updated[group] = [max(0.0, round(v + offset, 2)) for v in cases]
    return updated


def settings_now() -> Settings:
    vals = st.session_state
    return Settings(
        origin=int(vals.get("origin", 3)), buffet=int(vals.get("buffet", 3)),
        destination=int(vals.get("destination", 3)),
        break_minutes=float(vals.get("break_minutes", 15)),
        buy_minutes=float(vals.get("buy_minutes", 1.0)),
        eat_minutes=float(vals.get("eat_minutes", 5.0)),
        pace_factor={"fast": .85, "normal": 1.0, "slow": 1.2}.get(vals.get("pace"), 1.0),
    )


def set_route(origin: int, buffet: int, destination: int, restore_time: bool = False) -> None:
    st.session_state.update(origin=origin, buffet=buffet, destination=destination)
    if restore_time:
        st.session_state.update(break_minutes=15, buy_minutes=1.0, eat_minutes=5.0, pace="normal")


def pick_floor(title: str, slot: str) -> None:
    st.markdown(f"**{title}**")
    cols = st.columns(5, gap="small")
    for floor, col in enumerate(cols, 1):
        with col:
            st.button(str(floor), key=f"floor_{slot}_{floor}", use_container_width=True,
                      type="primary" if st.session_state[slot] == floor else "secondary",
                      on_click=set_floor, args=(slot, floor))


def set_floor(slot: str, floor: int) -> None:
    st.session_state[slot] = floor


def choose_best() -> None:
    st.session_state.buffet = best_buffet(settings_now(), adjusted_data())


left, right = st.columns([1.02, .98], gap="large", vertical_alignment="top")
with left:
    with st.container(border=True):
        st.markdown(f"<div class='paneltitle'>{t['route']}</div>", unsafe_allow_html=True)
        pick_floor(t["origin"], "origin")
        pick_floor(t["buffet"], "buffet")
        pick_floor(t["dest"], "destination")
        st.markdown(f"**{t['quick']}**")
        bc = st.columns(3, gap="small")
        with bc[0]:
            st.button(t["same"], key="scenario_same", use_container_width=True,
                      on_click=set_route, args=(3, 3, 3, True))
        with bc[1]:
            st.button(t["cross"], key="scenario_cross", use_container_width=True,
                      on_click=set_route, args=(5, 3, 5, True))
        with bc[2]:
            st.button(t["safe"], key="scenario_best", use_container_width=True,
                      on_click=choose_best)

    with st.container(border=True):
        st.markdown(f"<div class='paneltitle'>{t['settings']}</div>", unsafe_allow_html=True)
        current_group = group_for_ui(st.session_state.buffet, st.session_state.origin)
        current_wait_key = f"waiting_{current_group}"
        # Queue slider matches whichever buffet and arrival group the student selects.
        st.markdown(f"**{t['queue']}**")
        st.slider("Queue waiting time", min_value=0.0, max_value=25.0, step=0.5,
                  key=current_wait_key, label_visibility="collapsed")
        st.markdown(f"**{t['eat']}**")
        st.slider("Desired eating time", min_value=0.0, max_value=15.0, step=0.5,
                  key="eat_minutes", label_visibility="collapsed")
        with st.expander(t["more"]):
            st.markdown(f"**{t['break']}**")
            st.slider("Break duration", min_value=5, max_value=30, step=1,
                      key="break_minutes", label_visibility="collapsed")
            st.markdown(f"**{t['buy']}**")
            st.slider("Buying time", min_value=0.5, max_value=4.0, step=0.5,
                      key="buy_minutes", label_visibility="collapsed")
            st.markdown(f"**{t['pace']}**")
            st.radio("Pace", ("fast", "normal", "slow"), key="pace", horizontal=True,
                     format_func=lambda x: t[x], label_visibility="collapsed")

settings = settings_now()
observations = adjusted_data()
result = evaluate(settings, observations)
all_results = all_buffets(settings, observations)
percent = 100.0 * result.probability

with right:
    with st.container(border=True):
        st.markdown(f"<div class='paneltitle'>{t['result']}</div>", unsafe_allow_html=True)
        food_window = result.average_eating_window
        if result.average_margin >= 0:
            big = f"{max(0.0, food_window):.1f} {t['time']}"
            desc = t["enough"]
            caption = t["left"]
        else:
            big = f"{abs(result.average_margin):.1f} {t['time']}"
            desc = t["short"]
            caption = t["need"]
        st.markdown(
            f"<div class='resultbox'><small>{t['rate_title']}</small>"
            f"<strong>{percent:.1f}%</strong>"
            f"<span>{t['rate_text'].format(s=result.success_count, n=result.sample_count, p=percent)}</span>"
            f"</div>", unsafe_allow_html=True,
        )
        st.progress(float(result.probability))
        st.markdown(
            f"<div class='scorebox'><strong>{big}</strong>"
            f"<p>{caption} · {desc}</p></div>",
            unsafe_allow_html=True,
        )
        x1, x2 = st.columns(2)
        x3, x4 = st.columns(2)
        x1.metric(t["walk"], f"{result.travel:.1f} {t['time']}")
        x2.metric(t["avg_wait"], f"{result.average_wait:.1f} {t['time']}")
        x3.metric(t["buying"], f"{settings.buy_minutes:.1f} {t['time']}")
        x4.metric(t["full"], f"{result.average_total:.1f} {t['time']}")
        if percent == 0:
            must = result.travel + settings.buy_minutes + settings.eat_minutes
            st.info(t["zero"] if must > settings.break_minutes else t["zero_queue"])
        with st.expander(t["how"]):
            st.write(t["line"].format(walk=result.travel, wait=result.average_wait,
                                       buy=settings.buy_minutes, eat=settings.eat_minutes,
                                       full=result.average_total))
            st.write(t["rate_formula"].format(s=result.success_count, n=result.sample_count, p=percent))

st.divider()
chart_a, chart_b = st.columns(2, gap="large")
with chart_a:
    with st.container(border=True):
        st.markdown(f"<div class='paneltitle'>{t['compare']}</div>", unsafe_allow_html=True)
        st.caption(t["compare_sub"])
        bars = [r.probability * 100 for r in all_results]
        fig = go.Figure(go.Bar(
            x=[str(v) for v in range(1, 6)], y=bars,
            marker_color=["#2556C3" if f == settings.buffet else "#89AAE6" for f in range(1, 6)],
            text=[f"{v:.0f}%" for v in bars], textposition="outside",
        ))
        fig.update_layout(
            template="plotly_white", height=280, showlegend=False,
            margin=dict(l=10, r=10, t=28, b=28),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title=t["floor"], showgrid=False),
            yaxis=dict(title="%", range=[0, 112], gridcolor="#E6ECF3"),
            font=dict(color="#263B59"),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
with chart_b:
    with st.container(border=True):
        st.markdown(f"<div class='paneltitle'>{t['frequency']}</div>", unsafe_allow_html=True)
        st.caption(t["frequency_sub"])
        step = 2 if max(result.observed_waits) <= 20 else 5
        maximum = max(result.observed_waits)
        bins = list(range(0, int(maximum // step) * step + 1, step))
        counts = [sum(left <= value < left + step for value in result.observed_waits) for left in bins]
        used = [(left, count) for left, count in zip(bins, counts) if count]
        total_cases = len(result.observed_waits)
        percentages = [100.0 * count / total_cases for _, count in used]
        freq = go.Figure(go.Bar(
            x=[f"{l}–{l+step}" for l, _ in used], y=percentages,
            marker_color="#1E9A91",
            text=[f"{p:.1f}%" for p in percentages], textposition="outside",
            customdata=[count for _, count in used],
            hovertemplate=(f"%{{x}} {t['min_label']}: %{{y:.1f}}%"
                           f"<br>%{{customdata}} / {total_cases}<extra></extra>"),
        ))
        freq.update_layout(
            template="plotly_white", height=280, showlegend=False,
            margin=dict(l=10, r=10, t=28, b=28),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title=t["min_label"], showgrid=False),
            yaxis=dict(title=t["freq_label"], range=[0, 110], dtick=20,
                       ticksuffix="%", gridcolor="#E6ECF3"),
            font=dict(color="#263B59"),
        )
        st.plotly_chart(freq, use_container_width=True, config={"displayModeBar": False})

with st.expander(t["math"]):
    st.markdown(f"**{t['m1']}** · `N = 5 × 5 × 5 = 125`  ")
    st.caption(t["m1d"])
    st.markdown(f"**{t['m2']}** · `P(A) = n(A) / N`  ")
    st.caption(t["m2d"])
    st.markdown(f"`{result.success_count} / {result.sample_count} = {percent:.1f}%`")
    st.markdown(f"**{t['m3']}** · `P(A|B) = P(A∩B) / P(B)`  ")
    st.caption(t["m3d"])
    st.markdown(f"**{t['m3b']}** · `P(A) = Σ P(A|Bᵢ) × P(Bᵢ)`  ")
    st.caption(t["m3bd"])
    p_all = law_of_total_probability(all_results, CHOICE_WEIGHTS["equal"])
    st.markdown(f"**{t['examples']}**: `{p_all * 100:.1f}%`")
    st.markdown(f"**{t['m4']}** · `P(A∩B) = P(A) × P(B)`  ")
    st.caption(t["m4d"])
    p_a, p_b, p_joint, p_product = independence_check(all_results, CHOICE_WEIGHTS["equal"])
    st.markdown(f"`{p_joint:.4f} {'=' if abs(p_joint-p_product)<1e-12 else '≠'} {p_product:.4f}` — "
                + (t["ind"] if abs(p_joint-p_product)<1e-12 else t["not_ind"]))
    st.markdown(f"**{t['m5']}** · `fᵢ = nᵢ / n`  ")
    st.caption(t["m5d"])
    st.caption(t["small_note"])

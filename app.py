"""TEMIKBEK Project One — single-page Streamlit campus buffet probability lab.
Run: streamlit run app.py
"""
from __future__ import annotations

import copy
import csv
import io
from math import floor

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from model import (
    CHOICE_WEIGHTS, DEFAULT_OBSERVATIONS, Settings, all_buffets,
    best_buffet, evaluate, independence_check, parse_waits,
)

st.set_page_config(
    page_title="TEMIKBEK — Narxoz Buffet Rush",
    page_icon="🍱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700;800&display=swap');
html, body, [data-testid="stAppViewContainer"] {font-family:'DM Sans',system-ui,sans-serif;}
[data-testid="stAppViewContainer"] {background:radial-gradient(ellipse 65% 28% at 55% 1%,#1e443d 0%,#0d1a1b 78%,#0b1618 100%) fixed;}
[data-testid="stHeader"] {background:transparent;}
.block-container {max-width:1190px;padding-top:1.7rem;padding-bottom:4rem;}
[data-testid="stAppViewContainer"] h1, [data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3, [data-testid="stAppViewContainer"] h4,
[data-testid="stAppViewContainer"] p, [data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] {color:#e8f5ef;}
[data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"] p {color:#b9cfc2;}
h1,h2,h3 {font-family:'Space Grotesk',system-ui,sans-serif;letter-spacing:-.04em;}
.hero{padding:12px 0 24px;}
.headbar{display:flex;align-items:center;gap:12px;margin-bottom:29px;}
.logo{background:#c9fa89;color:#122719;width:50px;height:50px;display:flex;align-items:center;justify-content:center;border-radius:15px;font:800 31px 'Space Grotesk';transform:rotate(-5deg);box-shadow:0 6px 30px #a8fa8f28;}
.brand{font:800 16px 'Space Grotesk';letter-spacing:.13em;color:#effff3;line-height:1.55;}
.brand small{display:block;font:600 10px 'DM Sans';color:#a0b9ad;letter-spacing:.2em;}
.eyebrow{color:#b8f98e;letter-spacing:.21em;font-size:12px;font-weight:800;margin-bottom:12px;}
.hero h1{font-family:'Space Grotesk';font-size:clamp(36px,5vw,64px);line-height:1.09;margin:0 0 14px;font-weight:800;letter-spacing:-.055em;color:#f2fff2;}
.hero h1 span{color:#c9fa89;}
.hero p{font-size:16px;color:#b6c9bd;max-width:700px;line-height:1.7;margin:0 0 8px;}
.pill{display:inline-block;border:1px solid #4b755d;color:#c9fa89;border-radius:40px;font-size:11px;font-weight:800;letter-spacing:.07em;padding:6px 12px;margin-top:12px;}
.note{font-size:13px;line-height:1.65;color:#a9bdaf;}
.promo{border:1px solid #3b6250;padding:14px 18px;border-radius:16px;background:linear-gradient(110deg,#1b4134,#16312e);color:#e4ffe2;margin:9px 0 15px;font-size:14px;line-height:1.7;}
.section-kicker{color:#b7fa87;font-size:11px;letter-spacing:.13em;font-weight:800;margin:8px 0;}
.result{padding:18px 20px;background:linear-gradient(130deg,#224237,#18332e);border-radius:17px;border:1px solid #43654b;margin:6px 0 16px;}
.result strong{font-family:'Space Grotesk';font-size:clamp(43px,5vw,66px);line-height:1.25;color:#d4ffab;letter-spacing:-.055em;display:block;}
.result span{font-size:13px;color:#c2d8c7;}
.mathcard{min-height:170px;border:1px solid #355348;background:#192e2c;border-radius:16px;padding:17px;margin-bottom:12px;}
.mathcard .week{font-size:11px;color:#bff58a;font-weight:900;letter-spacing:.1em;}
.mathcard .t{font-size:16px;font-weight:800;color:#f2fff0;margin:8px 0;}
.mathcard .f{font-size:14px;font-weight:700;color:#fff0d0;margin-bottom:8px;overflow-wrap:anywhere;}
.mathcard .d{color:#b7c9bf;font-size:12px;line-height:1.65;}
[data-testid="stVerticalBlockBorderWrapper"] > div{border-color:#2f4d45 !important;border-radius:18px !important;}
.stButton > button[kind="primary"] {background:#c9fa89;color:#102318;border:1px solid #c9fa89;font-weight:800;border-radius:11px;}
.stButton > button[kind="secondary"] {background:#203632;border-color:#416056;color:#f1fff0;border-radius:11px;font-weight:700;}
.stButton > button {min-height:42px;}
[data-testid="stMetric"] {background:#1b3530;border-radius:14px;padding:12px 15px;border:1px solid #34584c;}
[data-testid="stMetricLabel"]{font-size:13px;}
[data-testid="stMetricValue"]{font-family:'Space Grotesk';}
hr {border-color:#34564b;}
@media (max-width:660px){.block-container{padding-left:14px;padding-right:14px;padding-top:10px}.hero h1{font-size:39px}.mathcard{min-height:auto}.headbar{margin-bottom:20px}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

TEXT = {
    "ru": {
        "title": "Еда или <span>пара вовремя?</span>",
        "intro": "У тебя 15 минут на перемене. Выбери этажи, купи еду и проверь, успеешь ли на следующую пару.",
        "tag": "ПРОЕКТ ПО ВЕРОЯТНОСТИ · НЕДЕЛИ 1–5",
        "route": "🧭 Твой маршрут",
        "origin": "01 · Где закончилась пара?",
        "buffet": "02 · В какой буфет идёшь?",
        "destination": "03 · Где следующая пара?",
        "quick": "Быстрые сценарии",
        "same3": "🍱 С 3-го на 3-й",
        "popular": "🔥 Буфет 3-го этажа",
        "cross": "🏃 С 5-го на 3-й",
        "safe": "🎓 Хочу успеть",
        "crowd": "Очередь в буфете",
        "pace": "Скорость ходьбы",
        "quiet": "Мало людей",
        "normal": "Обычно",
        "busy": "Большая очередь",
        "fast": "Быстро",
        "slow": "Не спеша",
        "break": "Перемена, минут",
        "buy": "Покупка и оплата, минут",
        "eat": "Сколько минут хочешь поесть?",
        "result": "ТВОЙ ПРОГНОЗ",
        "chance": "Шанс успеть до начала пары",
        "success": "УСПЕВАЕШЬ В УЧЕБНОЙ МОДЕЛИ",
        "uncertain": "РЕЗУЛЬТАТ ЗАВИСИТ ОТ ОЧЕРЕДИ",
        "late": "ВЫСОКИЙ РИСК ОПОЗДАТЬ",
        "travel": "Переход между этажами",
        "wait": "Средняя очередь",
        "total": "Общее время (включая еду)",
        "eatwindow": "Осталось минут на еду",
        "margin": "Запас до начала пары",
        "note": "Проценты — доля подходящих примеров времени ожидания. Это не официальные измерения Narxoz; при других очередях результат может отличаться.",
        "route_warning": "Даже если очереди нет, на этот маршрут, покупку и еду нужно {mins:.1f} мин при перемене {breaks:.0f} мин. Поэтому 0% — ограничение времени, а не ошибка графика.",
        "queue_warning": "В данном наборе ожиданий нет ни одного случая, который помещается в перемену. Попробуй сократить время на еду или выбрать более близкий буфет.",
        "perfect_sample": "Все {count} примеров помещаются в перемену. 100% относится к учебной таблице, а не означает гарантию в реальности.",
        "compare_route": "Для маршрута {start} → буфет → {end}; еда {eat:g} мин. Далёкие буфеты могут дать 0% просто из-за переходов.",
        "third_same": "Важное уточнение: если предыдущая и следующая пары на 3-м этаже, а ты идёшь в буфет 3-го, после очереди и оплаты обычно остаётся 8–10 минут на еду при стандартных настройках этого примера.",
        "third_other": "Если идти на 3-й из другого этажа, ты попадёшь в очередь позже. Мы считаем время перехода и отдельную очередь, не добавляя дорогу дважды.",
        "generic": "Поменяй этаж или длительность еды: процент сразу пересчитается по тем же наблюдениям — без случайных скачков.",
        "successes": "успешных случаев из",
        "detail": "🧮 Откуда получился процент?",
        "detail_text": "В каждом наблюдении: переходы + очередь + покупка + еда. Успех, если общее время не превышает длительность перемены.",
        "compare": "📊 Сравни 5 буфетов",
        "compare_note": "Вероятность успеть при тех же начальном и конечном этажах, но с другим этажом буфета.",
        "freq": "📉 Частоты времени ожидания",
        "freq_note": "Сколько раз встречалось конкретное время ожидания в выбранном буфете.",
        "choice": "Предположение о выборе буфета",
        "equal": "Каждый этаж одинаково вероятен (20%)",
        "hot": "Популярный 3-й этаж (50%)",
        "choice_note": "Доли выбора условные. Они используются только в формуле полной вероятности и проверке независимости.",
        "data": "📝 Наблюдения: можно изменить",
        "data_help": "Это не измеренная статистика, а настраиваемые примеры. На 3-м этаже ожидание 4–6 мин, если ты уже на 3-м, и обычно больше для тех, кто пришёл с другого этажа. Переход между этажами учитывается отдельно. Введи реальные замеры через запятую (минуты), чтобы улучшить оценку.",
        "data_groups": "Группа",
        "data_values": "Очередь, минуты (через запятую)",
        "save": "✅ Применить данные",
        "reset": "↩️ Вернуть примеры",
        "download": "⬇️ Скачать CSV",
        "saved": "Данные применены. Графики и расчёты обновлены.",
        "reset_done": "Учебный набор восстановлен.",
        "data_error": "Проверь таблицу: для каждой строки нужно хотя бы одно число от 0 до 120 минут (через запятую).",
        "math": "📚 Математика курса: Week 1–5",
        "math_desc": "Каждая тема связана с одной задачей: успеть купить еду и вернуться на пару.",
        "w1": "События и комбинаторика",
        "w1f": "N = 5 × 5 × 5 = 125",
        "w1d": "Есть 125 маршрутов (старт → буфет → аудитория), если все три этажа можно выбирать свободно. A — успеть; B — выбрать буфет 3-го этажа.",
        "w2": "Пространство вероятностей",
        "w2f": "P(A) = n(A) / N",
        "w2d": "Для равновероятных исходов. Для примеров разного ожидания считаем относительную частоту успехов: m / n.",
        "w3": "Условная вероятность",
        "w3f": "P(A | B) = P(A ∩ B) / P(B)",
        "w3d": "Шанс прийти вовремя при условии конкретного этажа буфета. Смотрим только подходящие наблюдения.",
        "w3b": "Полная вероятность",
        "w3bf": "P(A) = Σ P(A | Bᵢ)P(Bᵢ)",
        "w3bd": "Общий шанс успеть складывается из вероятностей пяти буфетов с учётом частоты их выбора.",
        "w4": "Независимость событий",
        "w4f": "P(A ∩ B) = P(A) · P(B)",
        "w4d": "Проверяем, связано ли событие «выбрал 3-й этаж» с событием «успел». Это тест внутри принятой модели.",
        "w5": "Частоты и графики",
        "w5f": "fᵢ = nᵢ / n",
        "w5d": "Группируем времена ожидания, считаем абсолютные и относительные частоты, строим график.",
        "math_details": "Показать числовую подстановку для Weeks 2–4",
        "total_formula": "Полная вероятность — все пять буфетов",
        "independent_formula": "Сравнение для независимости",
        "independent_yes": "В рамках заданной модели равенство выполняется.",
        "independent_no": "В рамках заданной модели равенство не выполняется.",
        "footer": "TEMIKBEK · PROJECT ONE · NARXOZ BUFFET RUSH · PYTHON / STREAMLIT",
        "not_official": "Учебные данные можно заменить результатами собственных анонимных наблюдений.",
        "floor": "этаж",
        "minutes": "мин",
        "frequency": "наблюдений",
        "sample": "Использованный набор",
    },
    "en": {
        "title": "Food or <span>class on time?</span>",
        "intro": "You have a 15-minute break. Choose your floors, grab food, and check whether you can return to class on time.",
        "tag": "PROBABILITY PROJECT · WEEKS 1–5",
        "route": "🧭 Your route",
        "origin": "01 · Where was your previous class?",
        "buffet": "02 · Which buffet will you visit?",
        "destination": "03 · Where is your next class?",
        "quick": "Quick scenarios",
        "same3": "🍱 Floor 3 → Floor 3",
        "popular": "🔥 Buffet on floor 3",
        "cross": "🏃 From floor 5 to 3",
        "safe": "🎓 Help me arrive on time",
        "crowd": "Queue level",
        "pace": "Walking speed",
        "quiet": "Quiet",
        "normal": "Normal",
        "busy": "Busy",
        "fast": "Fast",
        "slow": "Slow",
        "break": "Break duration (minutes)",
        "buy": "Buying and paying (minutes)",
        "eat": "How many minutes do you want to eat?",
        "result": "YOUR FORECAST",
        "chance": "Chance of arriving on time",
        "success": "ON TIME IN THE EXAMPLE MODEL",
        "uncertain": "DEPENDS ON THE QUEUE",
        "late": "HIGH CHANCE OF BEING LATE",
        "travel": "Walking time",
        "wait": "Average waiting time",
        "total": "Total (including eating)",
        "eatwindow": "Minutes available to eat",
        "margin": "Time left before class",
        "note": "Percentages are proportions of example waiting times that fit this trip. These are not official Narxoz measurements.",
        "route_warning": "Even with no queue, walking, buying, and eating require {mins:.1f} min, but the break is {breaks:.0f} min. The 0% result comes from the route, not a chart error.",
        "queue_warning": "None of the example waits fit within the break. Try less eating time or a closer buffet.",
        "perfect_sample": "All {count} example waits fit within the break. 100% describes this example dataset, not a real-world guarantee.",
        "compare_route": "For {start} → buffet → {end}; eating {eat:g} min. Distant floors may score 0% because of travel alone.",
        "third_same": "Important: if both your previous and next classes are on floor 3 and you visit the floor 3 buffet, the normal example leaves around 8–10 minutes to eat after waiting and paying.",
        "third_other": "Arriving from another floor means joining the queue later. Walking time and waiting time are modeled separately, without double-counting the trip.",
        "generic": "Change a floor or eating duration. The percentage will update from the same observations without random jumps.",
        "successes": "successful cases out of",
        "detail": "🧮 How is this percentage calculated?",
        "detail_text": "For every observation: walking + queue + purchase + eating. Success means the total is no longer than the break.",
        "compare": "📊 Compare all 5 buffets",
        "compare_note": "Chance of arriving on time with the same previous and next class floors, changing only the buffet.",
        "freq": "📉 Waiting-time frequencies",
        "freq_note": "How many observations fall within each waiting-time interval for the selected buffet.",
        "choice": "Assumption about buffet choice",
        "equal": "All floors equally likely (20% each)",
        "hot": "Floor 3 is popular (50%)",
        "choice_note": "These selection shares are hypothetical and only affect the total-probability and independence examples.",
        "data": "📝 Edit observations",
        "data_help": "These are editable examples, not measured statistics. Floor 3 assumes 4–6 min waits for students already there, and longer waits for arrivals from other floors. Walking is counted separately. Replace these values with actual timed waits (comma-separated minutes).",
        "data_groups": "Group",
        "data_values": "Waiting times (comma-separated minutes)",
        "save": "✅ Apply data",
        "reset": "↩️ Reset examples",
        "download": "⬇️ Download CSV",
        "saved": "New observations applied. The results and charts have been recalculated.",
        "reset_done": "Example dataset restored.",
        "data_error": "Check data: each row needs at least one number from 0 to 120 minutes, comma-separated.",
        "math": "📚 Course math: Weeks 1–5",
        "math_desc": "Every concept is tied to one problem: buying food and getting to class on time.",
        "w1": "Events and combinatorics",
        "w1f": "N = 5 × 5 × 5 = 125",
        "w1d": "125 possible routes (start → buffet → class) if all three floors may be freely chosen. A = on time; B = choose buffet on floor 3.",
        "w2": "Probability space",
        "w2f": "P(A) = n(A) / N",
        "w2d": "For equally likely outcomes. For different observed waits, use relative frequency: successes / total observations.",
        "w3": "Conditional probability",
        "w3f": "P(A | B) = P(A ∩ B) / P(B)",
        "w3d": "Probability of being on time given a specific buffet floor. We look at the matching observations.",
        "w3b": "Law of total probability",
        "w3bf": "P(A) = Σ P(A | Bᵢ)P(Bᵢ)",
        "w3bd": "The overall chance of being on time combines five buffet-specific rates weighted by how often each buffet is chosen.",
        "w4": "Independent events",
        "w4f": "P(A ∩ B) = P(A) · P(B)",
        "w4d": "Check whether choosing floor 3 and being on time are independent within the stated model.",
        "w5": "Frequencies and charts",
        "w5f": "fᵢ = nᵢ / n",
        "w5d": "Group waiting times into intervals, count absolute and relative frequencies, and plot them.",
        "math_details": "Show numeric calculations for Weeks 2–4",
        "total_formula": "Total probability — all five buffets",
        "independent_formula": "Independence comparison",
        "independent_yes": "The equality holds within the stated model.",
        "independent_no": "The equality does not hold within the stated model.",
        "footer": "TEMIKBEK · PROJECT ONE · NARXOZ BUFFET RUSH · PYTHON / STREAMLIT",
        "not_official": "Replace the sample data with your own anonymous observations whenever available.",
        "floor": "floor",
        "minutes": "min",
        "frequency": "observations",
        "sample": "Dataset used",
    },
}

for key, val in {
    "lang": "ru", "origin": 3, "buffet": 3, "destination": 3,
    "crowd": "normal", "pace": "normal", "break_minutes": 15,
    "buy_minutes": 1.0, "eat_minutes": 5.0,
    "choice_weight": "equal", "editor_version": 0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val
if "observations" not in st.session_state:
    st.session_state.observations = copy.deepcopy(DEFAULT_OBSERVATIONS)

lang = st.radio("Language / Язык", options=["ru", "en"],
                horizontal=True, format_func=lambda s: "🇷🇺 RU" if s == "ru" else "🇬🇧 EN",
                key="lang", label_visibility="collapsed")
t = TEXT[lang]

st.markdown(f"""
<div class="hero">
  <div class="headbar"><div class="logo">T</div><div class="brand">TEMIKBEK<small>PROJECT ONE · NARXOZ</small></div></div>
  <div class="eyebrow">{t['tag']}</div>
  <h1>{t['title']}</h1>
  <p>{t['intro']}</p>
  <div class="pill">🍱 NARXOZ BUFFET RUSH · PYTHON / STREAMLIT</div>
</div>
""", unsafe_allow_html=True)


def choose_floor(title: str, key: str):
    st.markdown(f"**{title}**")
    cols = st.columns(5, gap="small")
    for val, col in enumerate(cols, 1):
        with col:
            lab = f"🔥 {val}" if key == "buffet" and val == 3 else str(val)
            if st.button(lab, key=f"{key}_{val}", use_container_width=True,
                         type="primary" if st.session_state[key] == val else "secondary"):
                st.session_state[key] = val
                st.rerun()


def use_scenario(name):
    if name == "same":
        st.session_state.origin, st.session_state.buffet, st.session_state.destination = 3, 3, 3
        st.session_state.crowd, st.session_state.pace = "normal", "normal"
        st.session_state.break_minutes = 15
        st.session_state.buy_minutes, st.session_state.eat_minutes = 1.0, 8.0
    elif name == "popular":
        st.session_state.buffet = 3
    elif name == "cross":
        st.session_state.origin, st.session_state.buffet, st.session_state.destination = 5, 3, 5
    elif name == "safe":
        st.session_state.buffet = best_buffet(current_settings(), st.session_state.observations)



def current_settings():
    return Settings(
        origin=st.session_state.origin,
        buffet=st.session_state.buffet,
        destination=st.session_state.destination,
        break_minutes=st.session_state.break_minutes,
        buy_minutes=st.session_state.buy_minutes,
        eat_minutes=st.session_state.eat_minutes,
        crowd_factor={"quiet": .8, "normal": 1, "busy": 1.3}[st.session_state.crowd],
        pace_factor={"fast": .85, "normal": 1, "slow": 1.2}[st.session_state.pace],
    )

left, right = st.columns([1.05, .95], gap="large", vertical_alignment="top")
with left:
    with st.container(border=True):
        st.subheader(t["route"])
        choose_floor(t["origin"], "origin")
        choose_floor(t["buffet"], "buffet")
        choose_floor(t["destination"], "destination")
        st.markdown(f"**{t['quick']}**")
        quick_cols = st.columns(2)
        with quick_cols[0]:
            st.button(t["same3"], key="scenario_same", on_click=use_scenario,
                      args=("same",), use_container_width=True)
            st.button(t["cross"], key="scenario_cross", on_click=use_scenario,
                      args=("cross",), use_container_width=True)
        with quick_cols[1]:
            st.button(t["popular"], key="scenario_popular", on_click=use_scenario,
                      args=("popular",), use_container_width=True)
            st.button(t["safe"], key="scenario_safe", on_click=use_scenario,
                      args=("safe",), use_container_width=True)
        st.divider()
        select_a, select_b = st.columns(2)
        with select_a:
            st.selectbox(t["crowd"], options=["quiet", "normal", "busy"],
                         format_func=lambda opt: t[opt], key="crowd")
        with select_b:
            st.selectbox(t["pace"], options=["fast", "normal", "slow"],
                         format_func=lambda opt: t[opt], key="pace")
        slider_a, slider_b = st.columns(2)
        with slider_a:
            st.slider(t["break"], 5, 30, key="break_minutes")
            st.slider(t["buy"], .5, 4., step=.5, key="buy_minutes")
        with slider_b:
            st.slider(t["eat"], 0., 15., step=.5, key="eat_minutes")
            st.caption(f"↓ 1.5 {t['minutes']} / ↑ 2.25 {t['minutes']} — "
                       + ("на каждый этаж" if lang == "ru" else "per floor"))

settings = current_settings()
result = evaluate(settings, st.session_state.observations)
compared = all_buffets(settings, st.session_state.observations)
prob_pct = 100 * result.probability
status = t["success"] if prob_pct >= 80 else t["uncertain"] if prob_pct >= 40 else t["late"]

with right:
    with st.container(border=True):
        st.markdown(f"<div class='section-kicker'>{t['result']}</div>", unsafe_allow_html=True)
        st.markdown(f"""<div class='result'><span>{t['chance']}</span>
                     <strong>{prob_pct:.1f}%</strong><span>{status}</span></div>""", unsafe_allow_html=True)
        st.progress(float(result.probability))
        st.caption(f"{result.success_count} {t['successes']} {result.sample_count} · {t['sample']}: {result.group}")
        m1, m2 = st.columns(2)
        m3, m4 = st.columns(2)
        m1.metric(t["travel"], f"{result.travel:.1f} {t['minutes']}")
        m2.metric(t["wait"], f"{result.average_wait:.1f} {t['minutes']}")
        m3.metric(t["total"], f"{result.average_total:.1f} {t['minutes']}")
        m4.metric(t["eatwindow"], f"{result.average_eating_window:.1f} {t['minutes']}")
        if settings.origin == settings.buffet == settings.destination == 3:
            st.markdown(f"<div class='promo'>🍽️ {t['third_same']}<br><b>"
                        f"{result.min_eating_window:.1f}–{result.max_eating_window:.1f} {t['minutes']}"
                        f"</b></div>", unsafe_allow_html=True)
        elif settings.buffet == 3 and settings.origin != 3:
            st.markdown(f"<div class='promo'>🔥 {t['third_other']}</div>", unsafe_allow_html=True)
        else:
            st.info(t["generic"], icon="💡")
        minimum_required = result.travel + settings.buy_minutes + settings.eat_minutes
        if minimum_required > settings.break_minutes + 1e-9:
            st.warning(t["route_warning"].format(mins=minimum_required, breaks=settings.break_minutes))
        elif result.probability == 0:
            st.warning(t["queue_warning"])
        elif result.probability == 1:
            st.caption(t["perfect_sample"].format(count=result.sample_count))
        st.caption(t["note"])
        with st.expander(t["detail"]):
            st.write(t["detail_text"])
            st.code(
                f"Walk = {result.travel:.2f} min\n"
                f"Mean wait = {result.average_wait:.2f} min\n"
                f"Buy = {settings.buy_minutes:.2f} min\n"
                f"Eat = {settings.eat_minutes:.2f} min\n"
                f"Total = {result.travel:.2f} + {result.average_wait:.2f} + "
                f"{settings.buy_minutes:.2f} + {settings.eat_minutes:.2f}"
                f" = {result.average_total:.2f} min\n"
                f"P(on time | chosen route) ≈ {result.success_count}/{result.sample_count}"
                f" = {prob_pct:.1f}%",
                language="text",
            )

st.divider()
plot_left, plot_right = st.columns(2, gap="large")
with plot_left:
    with st.container(border=True):
        st.subheader(t["compare"])
        st.caption(t["compare_note"])
        st.caption(t["compare_route"].format(start=settings.origin, end=settings.destination, eat=settings.eat_minutes))
        colors = ["#f2ae75" if r.floor == settings.buffet else "#b9f68b" for r in compared]
        fig = go.Figure(go.Bar(
            x=[r.probability * 100 for r in compared],
            y=[f"{r.floor} {t['floor']}" for r in compared],
            orientation="h", marker_color=colors,
            text=[f"{r.probability*100:.0f}%" for r in compared],
            textposition="outside", cliponaxis=False,
            hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
        ))
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=8, b=20, l=10, r=45),
            height=290, xaxis=dict(range=[0, 112], title="%", showgrid=True, gridcolor="#2d4b42"),
            yaxis=dict(autorange="reversed", showgrid=False), showlegend=False,
            font=dict(color="#def5e5"),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
with plot_right:
    with st.container(border=True):
        st.subheader(t["freq"])
        st.caption(t["freq_note"])
        step = 2 if max(result.observed_waits) <= 25 else 5
        lows = list(range(0, int(max(result.observed_waits)) + step, step))
        counts = [sum(low <= v < low + step for v in result.observed_waits) for low in lows]
        # Include the endpoint of the final bin when samples hit a multiple of step.
        bins = [(f"{low}–{low+step}", count) for low, count in zip(lows, counts) if count > 0]
        figh = go.Figure(go.Bar(
            x=[b[0] for b in bins], y=[b[1] for b in bins], marker_color="#b9f68b",
            text=[b[1] for b in bins], textposition="outside",
        ))
        figh.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=8, b=20, l=10, r=12),
            height=290, xaxis=dict(title=t["minutes"], showgrid=False),
            yaxis=dict(title=t["frequency"], dtick=1, showgrid=True, gridcolor="#2d4b42"),
            showlegend=False, font=dict(color="#def5e5"),
        )
        st.plotly_chart(figh, use_container_width=True, config={"displayModeBar": False})

with st.expander(t["data"]):
    st.write(t["data_help"])
    group_labels = {
        "1": "1", "2": "2", "3_same": "3 · same / с 3-го",
        "3_other": "3 · other / с других", "4": "4", "5": "5",
    }
    rows = [{"Group": key, "Display": group_labels[key],
             "Waits": ", ".join(f"{v:g}" for v in st.session_state.observations[key])}
            for key in DEFAULT_OBSERVATIONS]
    editor = st.data_editor(
        pd.DataFrame(rows), hide_index=True, use_container_width=True,
        column_config={
            "Group": None,
            "Display": st.column_config.TextColumn(t["data_groups"], disabled=True),
            "Waits": st.column_config.TextColumn(t["data_values"], width="large"),
        },
        disabled=["Group", "Display"], num_rows="fixed",
        key=f"observations_editor_{st.session_state.editor_version}",
    )
    ca, cb, cc = st.columns(3)
    with ca:
        if st.button(t["save"], use_container_width=True):
            try:
                new_observations = {row["Group"]: parse_waits(str(row["Waits"]))
                                    for _, row in editor.iterrows()}
                if set(new_observations) != set(DEFAULT_OBSERVATIONS):
                    raise ValueError("Missing group")
            except (ValueError, TypeError):
                st.error(t["data_error"])
            else:
                st.session_state.observations = new_observations
                st.session_state.editor_version += 1
                st.success(t["saved"])
                st.rerun()
    with cb:
        if st.button(t["reset"], use_container_width=True):
            st.session_state.observations = copy.deepcopy(DEFAULT_OBSERVATIONS)
            st.session_state.editor_version += 1
            st.rerun()
    with cc:
        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow(["buffet_floor", "arrival_group", "wait_minutes"])
        for group, waits in st.session_state.observations.items():
            for wait in waits:
                writer.writerow(["3" if group.startswith("3") else group,
                                 "same_floor" if group == "3_same" else "other_floor" if group == "3_other" else "all",
                                 wait])
        st.download_button(t["download"], data=out.getvalue().encode("utf-8-sig"),
                           file_name="narxoz_buffet_observations.csv", mime="text/csv",
                           use_container_width=True)
    st.caption(t["not_official"])

st.divider()
st.subheader(t["math"])
st.caption(t["math_desc"])
MATH = [
    ("WEEK 1", "w1", "w1f", "w1d"),
    ("WEEK 2", "w2", "w2f", "w2d"),
    ("WEEK 3", "w3", "w3f", "w3d"),
    ("WEEK 3", "w3b", "w3bf", "w3bd"),
    ("WEEK 4", "w4", "w4f", "w4d"),
    ("WEEK 5", "w5", "w5f", "w5d"),
]
for begin in (0, 3):
    columns = st.columns(3, gap="medium")
    for col, (week, title, formula, desc) in zip(columns, MATH[begin:begin + 3]):
        with col:
            st.markdown(f"""<div class='mathcard'>
              <div class='week'>{week}</div>
              <div class='t'>{t[title]}</div>
              <div class='f'>{t[formula]}</div>
              <div class='d'>{t[desc]}</div>
            </div>""", unsafe_allow_html=True)

st.markdown(f"**{t['choice']}**")
choice = st.radio("weights", ["equal", "popular_third"],
                  format_func=lambda val: t["equal"] if val == "equal" else t["hot"],
                  key="choice_weight", label_visibility="collapsed", horizontal=True)
st.caption(t["choice_note"])
weights = CHOICE_WEIGHTS[choice]
p_a, p_b, joint, product = independence_check(compared, weights)
with st.expander(t["math_details"]):
    st.markdown(f"**WEEK 2–3 — {t['detail']}**")
    st.latex(rf"\widehat P(A\mid B) = \frac{{{result.success_count}}}{{{result.sample_count}}} = {result.probability:.3f}")
    st.markdown(f"**WEEK 3 — {t['total_formula']}**")
    terms = " + ".join(f"{w:.2f} × {r.probability:.2f}" for w,r in zip(weights,compared))
    st.code(f"P(A) = {terms} = {p_a:.3f} = {p_a*100:.1f}%", language="text")
    st.markdown(f"**WEEK 4 — {t['independent_formula']}**")
    st.code(f"P(B) = {p_b:.2f}\nP(A∩B) = P(A|B)×P(B) = {compared[2].probability:.3f}×{p_b:.2f} = {joint:.3f}\n"
            f"P(A)×P(B) = {p_a:.3f}×{p_b:.2f} = {product:.3f}", language="text")
    st.write(t["independent_yes"] if abs(joint-product) < 1e-10 else t["independent_no"])
    st.caption(t["choice_note"])

st.markdown(f"<div style='color:#8ea99b;text-align:center;font-size:12px;padding:28px 0 10px'>"
            f"{t['footer']}</div>", unsafe_allow_html=True)

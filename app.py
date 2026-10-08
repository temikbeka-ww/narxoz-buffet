"""TEMIKBEK Project One — classroom-first, bilingual Streamlit buffet calculator.

All probabilities below are relative frequencies over editable illustrative waiting
cases, not measured predictions for Narxoz University.

Start: streamlit run app.py
"""
from __future__ import annotations

import copy
import csv
import io

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from model import (CHOICE_WEIGHTS, DEFAULT_OBSERVATIONS, Settings,
                   all_buffets, best_buffet, evaluate, independence_check,
                   parse_waits)

st.set_page_config(page_title="TEMIKBEK | Narxoz Buffet Rush", page_icon="🥪",
                   layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
html,body,[data-testid="stAppViewContainer"]{font-family:'DM Sans',system-ui,sans-serif;background:#F6F8FC;color:#1B2940}
[data-testid="stHeader"]{background:transparent}
.block-container{max-width:1160px;padding-top:1.1rem;padding-bottom:3.5rem}
.stApp h1,.stApp h2,.stApp h3,.stApp p,.stApp label{color:#1B2940}
.hero{background:linear-gradient(110deg,#152C62,#233C7E 55%,#194F69);padding:24px 30px 26px;border-radius:22px;color:white;margin:4px 0 20px;box-shadow:0 16px 38px #233c7e22}
.brand{color:#BFE7FC;font-weight:800;letter-spacing:.15em;font-size:11px}
.hero h1{font-size:clamp(30px,4vw,49px);line-height:1.13;color:white!important;letter-spacing:-.035em;margin:13px 0 8px}
.hero h1 em{font-style:normal;color:#B9FAAB}
.hero p{color:#ECF4FF!important;font-size:15px;margin-bottom:0;max-width:700px}
.eyebrow{font-size:11px;letter-spacing:.12em;color:#3A5CD1;font-weight:800;margin-bottom:3px}
.card-title{font-size:20px;font-weight:800;color:#162B54;margin-bottom:5px}
[data-testid="stVerticalBlockBorderWrapper"]{border:1px solid #DFE6F0!important;border-radius:18px!important;background:white!important;box-shadow:0 7px 24px #1c32600b}
[data-testid="stVerticalBlockBorderWrapper"] > div{background:transparent!important}
.stButton>button{border-radius:11px!important;min-height:43px!important;font-weight:800!important;border:1px solid #CED8E7!important;box-shadow:none!important}
.stButton>button[kind="primary"]{background:#2555C7!important;border-color:#2555C7!important;color:white!important}
.stButton>button[kind="secondary"]{background:#F5F7FD!important;color:#21365B!important}
.stButton>button:hover{border-color:#2555C7!important}
.stRadio [role="radiogroup"]{gap:11px}
[data-testid="stMetric"]{background:#F2F6FF;border:1px solid #E0E8F9;border-radius:14px;padding:11px 14px}
[data-testid="stMetricValue"]{color:#173C8B}
.result-panel{background:#EAF4F5;border:1px solid #C9E5E2;border-radius:17px;padding:15px 20px;margin:5px 0 15px}
.result-panel strong{font-size:clamp(36px,4.2vw,51px);font-weight:800;color:#123B72;display:block;line-height:1.15;margin:5px 0}
.result-panel span{color:#376177;font-weight:700;font-size:12px}
.highlight{background:#F0F5FF;border-left:4px solid #2555C7;border-radius:12px;padding:12px 15px;color:#1E3B72;font-size:13px;line-height:1.55;margin:8px 0 15px}
.tiny{color:#64768D;font-size:12px;line-height:1.5}
.mathitem{padding:12px;border-radius:12px;background:#F2F5FC;margin:6px 0}
.mathitem b{color:#173C8B}.mathitem code{color:#1C479F}
hr{border-color:#E0E8F2}
@media(max-width:650px){.hero{padding:21px}.hero h1{font-size:32px}.block-container{padding:1rem 13px 2rem}}
</style>
""",unsafe_allow_html=True)

LANG = {
"ru":{
"hero":"Успеешь поесть <em>до пары?</em>","subtitle":"Одна перемена — 15 минут. Выбирай этажи, сравнивай очереди и проверяй свой маршрут.",
"route":"01 · Твой маршрут","origin":"Где закончилась пара?","buffet":"Где покупаешь еду?","dest":"Где следующая пара?",
"quick":"Попробуй готовый сценарий","three":"🍟 На третьем","cross":"🏃 С пятого на третий","safe":"✅ Лучший буфет",
"settings":"Настроить условия","duration":"Длина перемены, минут","eat":"Сколько минут хочешь есть?","buy":"Оплата и покупка, минут",
"crowd":"Очередь","crowd_quiet":"Небольшая","crowd_normal":"Обычная","crowd_busy":"Большая","pace":"Скорость","pace_fast":"Быстро","pace_normal":"Обычно","pace_slow":"Медленно",
"result":"02 · Твой результат","remain":"Время на еду до начала пары","on_time":"При выбранных условиях успеваешь","late":"Времени не хватает","travel":"Дорога","wait":"Очередь (средняя)","total":"Путь + очередь + покупка + еда","margin":"Запас до пары","chance":"Оценка успеть с желаемым временем на еду","from":"из","cases":"примеров",
"third_info":"На 3-м этаже: если предыдущая и следующая пары там же, после очереди и оплаты остаётся примерно 8–10 минут для еды.",
"explain_zero_time":"Даже без очереди путь, оплата и желаемое время на еду не помещаются в перемену.",
"explain_zero_queue":"По заданным примерам очередей свободного времени не хватает. Попробуй меньше минут на еду или другой буфет.",
"explain_prob":"Процент — доля подходящих учебных примеров очереди, а не точное обещание, что ты успеешь.",
"chart":"03 · Сравни этажи","chart_hint":"Тот же старт и следующая пара; меняется только этаж буфета.","freq":"04 · Очередь на выбранном этаже","freq_hint":"Распределение времени ожидания по интервалам.",
"data":"✏️ Откуда данные? Изменить примеры","data_help":"Время ожидания в минутах. Эти значения придуманы для объяснения формул, а не измерены в Narxoz. После наблюдений можно заменить их своими.",
"group":"Сценарий","values":"Минуты ожидания через запятую","apply":"Сохранить","reset":"Вернуть примеры","download":"Скачать CSV","saved":"Данные сохранены для этой сессии.","invalid":"Проверь значения: в каждой строке нужны числа от 0 до 120 через запятую.",
"math":"📚 Формулы из Week 1–5","math_help":"Один проект — пять тем. Нажми, чтобы посмотреть формулы и подставленные значения.",
"step":"Как получен мой процент?","total_prob":"Полная вероятность при выборе буфета","weights":"Как студенты выбирают этажи?","equal":"Все этажи поровну — по 20%","popular":"Третий этаж выбирают чаще — 50%", "independent":"Проверка независимости","notind":"В этой модели события не независимы.","ind":"В этой модели равенство соблюдается.",
"disclaimer":"Статистика в демо — иллюстративная. Для реального прогноза нужны наблюдения в буфетах.",
"floor":"этаж","minutes":"мин","count":"наблюдений","none":"Нет подходящих наблюдений",
"math1":"Week 1 · События и комбинаторика","math2":"Week 2 · Вероятность","math3":"Week 3 · Условная вероятность и полная вероятность","math4":"Week 4 · Независимые события","math5":"Week 5 · Частоты и графики",
},
"en":{
"hero":"Food or <em>class on time?</em>","subtitle":"One break — 15 minutes. Choose floors, compare queues, and plan your route.",
"route":"01 · Your route","origin":"Where was your last class?","buffet":"Which buffet?","dest":"Where is your next class?",
"quick":"Try a quick scenario","three":"🍟 Stay on floor 3","cross":"🏃 From floor 5 to 3","safe":"✅ Best buffet",
"settings":"Adjust conditions","duration":"Break duration, minutes","eat":"How long do you want to eat?","buy":"Buying and paying, minutes",
"crowd":"Queue size","crowd_quiet":"Short","crowd_normal":"Normal","crowd_busy":"Long","pace":"Walking speed","pace_fast":"Fast","pace_normal":"Normal","pace_slow":"Slow",
"result":"02 · Your result","remain":"Minutes available to eat before class","on_time":"Enough time with these settings","late":"Not enough time","travel":"Walking","wait":"Average queue","total":"Walking + waiting + buying + eating","margin":"Time left before class","chance":"Observed-style rate of reaching class on time","from":"out of","cases":"example cases",
"third_info":"On floor 3: if your previous and next classes are also there, around 8–10 minutes remain for eating after queuing and paying.",
"explain_zero_time":"Even without a queue, walking, paying and your desired eating time exceed the break.",
"explain_zero_queue":"None of the sample queues fit. Try a shorter meal or another buffet.",
"explain_prob":"This percentage is a frequency across example queues, not a guarantee of arrival.",
"chart":"03 · Compare five buffets","chart_hint":"Same start and next-class floors; only the buffet floor changes.","freq":"04 · Waiting times","freq_hint":"Frequency distribution of waiting-time intervals.",
"data":"✏️ Edit the example waiting data","data_help":"Waiting times in minutes. These are learning examples, not Narxoz measurements. Replace them with real observations later.",
"group":"Scenario","values":"Waits, comma-separated (min)","apply":"Save","reset":"Reset examples","download":"Download CSV","saved":"Data saved for this session.","invalid":"Check values: each row must contain comma-separated numbers between 0 and 120.",
"math":"📚 Math covered in Weeks 1–5","math_help":"One project, five concepts. Open to see formulas using your current inputs.",
"step":"How was my percentage calculated?","total_prob":"Total probability across buffet choices","weights":"How do students select floors?","equal":"Equal choices — 20% per floor","popular":"Floor 3 is popular — 50%", "independent":"Independence check","notind":"The events are not independent in this model.","ind":"The equation holds in this model.",
"disclaimer":"Demo observations are illustrative. Real campus predictions need collected data.",
"floor":"floor","minutes":"min","count":"observations","none":"No matching observations",
"math1":"Week 1 · Events and combinations","math2":"Week 2 · Probability","math3":"Week 3 · Conditional and total probability","math4":"Week 4 · Independent events","math5":"Week 5 · Frequencies and charts",
}}

if "language" not in st.session_state or st.session_state.language not in ("ru", "en"):
    st.session_state.language = "ru"
if "observations" not in st.session_state:
    st.session_state.observations = copy.deepcopy(DEFAULT_OBSERVATIONS)
for key, val in {"origin":3,"buffet":3,"destination":3,"break_minutes":15,
                 "buy_minutes":1.0,"eat_minutes":5.0,"crowd_choice":"normal",
                 "pace_choice":"normal","weight_choice":"equal","editor_count":0}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Streamlit widget keys can be transient after a language toggle. Revalidate them.
for key, choices in ("crowd_choice",("quiet","normal","busy")), ("pace_choice",("fast","normal","slow")), ("weight_choice",("equal","popular_third")):
    if st.session_state.get(key) not in choices:
        st.session_state[key] = choices[1] if key != "weight_choice" else "equal"

st.radio("Language / Язык", ["ru", "en"], key="language", horizontal=True,
         format_func=lambda v: "🇷🇺 Русский" if v == "ru" else "🇬🇧 English",
         label_visibility="collapsed")
t = LANG[st.session_state.language]
st.markdown(f"""<div class='hero'><div class='brand'>T / TEMIKBEK · PROJECT ONE · NARXOZ</div>
<h1>{t['hero']}</h1><p>{t['subtitle']}</p></div>""", unsafe_allow_html=True)


def select_floor(name: str, title: str):
    st.markdown(f"**{title}**")
    cols = st.columns(5, gap="small")
    for idx, col in enumerate(cols, start=1):
        with col:
            st.button(("🔥 " if name == "buffet" and idx == 3 else "")+str(idx),
                      type="primary" if st.session_state[name] == idx else "secondary",
                      key=f"floor_{name}_{idx}", use_container_width=True,
                      on_click=st.session_state.update, args=({name:idx},))


def set_scenario(which: str):
    if which == "three":
        st.session_state.update(origin=3,buffet=3,destination=3,break_minutes=15,
                                buy_minutes=1.0,eat_minutes=5.0,crowd_choice="normal",pace_choice="normal")
    elif which == "cross":
        st.session_state.update(origin=5,buffet=3,destination=5,break_minutes=15,
                                buy_minutes=1.0,eat_minutes=5.0,crowd_choice="normal",pace_choice="normal")
    elif which == "safe":
        st.session_state.buffet = best_buffet(make_settings(),st.session_state.observations)


def make_settings() -> Settings:
    c = st.session_state
    return Settings(origin=c.origin,buffet=c.buffet,destination=c.destination,
      break_minutes=c.break_minutes,buy_minutes=c.buy_minutes,eat_minutes=c.eat_minutes,
      crowd_factor={"quiet":.8,"normal":1.,"busy":1.25}.get(c.crowd_choice,1.),
      pace_factor={"fast":.85,"normal":1.,"slow":1.2}.get(c.pace_choice,1.))

left,right=st.columns([1.1,.9],gap="large",vertical_alignment="top")
with left:
    with st.container(border=True):
        st.markdown(f"<div class='card-title'>🧭 {t['route']}</div>",unsafe_allow_html=True)
        select_floor("origin",t["origin"])
        select_floor("buffet",t["buffet"])
        select_floor("destination",t["dest"])
        st.markdown(f"**{t['quick']}**")
        buttons=st.columns(3,gap="small")
        for col, name, key in zip(buttons,[t['three'],t['cross'],t['safe']],['three','cross','safe']):
            with col: st.button(name,key=f"q_{key}",on_click=set_scenario,args=(key,),use_container_width=True)
        with st.expander("⚙️ "+t["settings"]):
            c1,c2=st.columns(2)
            with c1:
                st.slider(t["duration"],5,30,key="break_minutes")
                st.slider(t["buy"],.5,4.,step=.5,key="buy_minutes")
                st.selectbox(t["crowd"],("quiet","normal","busy"),key="crowd_choice",
                             format_func=lambda x:t[f"crowd_{x}"])
            with c2:
                st.slider(t["eat"],0.,15.,step=.5,key="eat_minutes")
                st.selectbox(t["pace"],("fast","normal","slow"),key="pace_choice",
                             format_func=lambda x:t[f"pace_{x}"])
                st.caption("↓ 1.5 min/floor · ↑ 2.25 min/floor")

settings=make_settings()
result=evaluate(settings,st.session_state.observations)
results=all_buffets(settings,st.session_state.observations)
prob_pct=100*result.probability

with right:
    with st.container(border=True):
        st.markdown(f"<div class='card-title'>🎯 {t['result']}</div>",unsafe_allow_html=True)
        avg_available=result.average_eating_window
        msg=t['on_time'] if result.average_margin>=0 else t['late']
        st.markdown(f"<div class='result-panel'><span>{t['remain']}</span>"
                    f"<strong>{avg_available:+.1f} {t['minutes']}</strong><span>{msg}</span></div>",
                    unsafe_allow_html=True)
        if settings.origin==settings.buffet==settings.destination==3 and settings.crowd_factor==1 and settings.buy_minutes==1:
            st.markdown(f"<div class='highlight'>🍟 {t['third_info']}</div>",unsafe_allow_html=True)
        m1,m2=st.columns(2)
        m1.metric(t["travel"],f"{result.travel:.1f} {t['minutes']}")
        m2.metric(t["wait"],f"{result.average_wait:.1f} {t['minutes']}")
        m3,m4=st.columns(2)
        m3.metric(t["total"],f"{result.average_total:.1f} {t['minutes']}")
        m4.metric(t["margin"],f"{result.average_margin:+.1f} {t['minutes']}")
        st.markdown(f"**{t['chance']}**")
        st.progress(result.probability)
        st.markdown(f"**{prob_pct:.1f}%** · {result.success_count} {t['from']} {result.sample_count} {t['cases']}")
        if prob_pct == 0:
            necessary=result.travel+settings.buy_minutes+settings.eat_minutes
            st.warning(t["explain_zero_time"] if necessary>settings.break_minutes else t["explain_zero_queue"])
        st.caption(t["explain_prob"])
        with st.expander("🧮 "+t["step"]):
            st.code(f"Travel = {result.travel:.1f} min\n"
                    f"Mean queue = {result.average_wait:.1f} min\n"
                    f"Buying = {settings.buy_minutes:.1f} min\n"
                    f"Eating = {settings.eat_minutes:.1f} min\n"
                    f"Total = {result.average_total:.1f} min\n"
                    f"P(on time | route) ≈ {result.success_count}/{result.sample_count} = {prob_pct:.1f}%",language="text")

st.divider()
chart_a,chart_b=st.columns(2,gap="large")
with chart_a:
    with st.container(border=True):
        st.markdown(f"<div class='card-title'>📊 {t['chart']}</div>",unsafe_allow_html=True)
        st.caption(t["chart_hint"])
        vals=[r.probability*100 for r in results]
        fig=go.Figure(go.Bar(x=[f"{i} {t['floor']}" for i in range(1,6)],y=vals,
          marker_color=["#2555C7" if i==settings.buffet else "#88ADEB" for i in range(1,6)],
          text=[f"{v:.0f}%" for v in vals],textposition="outside"))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
          height=290,showlegend=False,margin=dict(l=5,r=4,t=18,b=18),
          yaxis=dict(range=[0,110],title="%",gridcolor="#E5EBF2"),
          xaxis=dict(title="",showgrid=False),font=dict(color="#263B59"))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
with chart_b:
    with st.container(border=True):
        st.markdown(f"<div class='card-title'>📈 {t['freq']}</div>",unsafe_allow_html=True)
        st.caption(t["freq_hint"])
        step=2 if max(result.observed_waits)<=20 else 5
        end=int(max(result.observed_waits)//step)*step
        bins=list(range(0,end+step,step))
        counts=[sum(low<=x<low+step for x in result.observed_waits) for low in bins]
        shown=[(low,cnt) for low,cnt in zip(bins,counts) if cnt]
        fig2=go.Figure(go.Bar(x=[f"{b}–{b+step}" for b,c in shown],
          y=[c for _,c in shown],marker_color="#2A9D8F",
          text=[str(c) for _,c in shown],textposition="outside"))
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
          height=290,showlegend=False,margin=dict(l=5,r=4,t=18,b=18),
          xaxis=dict(title=t['minutes']),yaxis=dict(dtick=1,gridcolor="#E5EBF2",title=t['count']),
          font=dict(color="#263B59"))
        st.plotly_chart(fig2,use_container_width=True,config={"displayModeBar":False})

with st.expander(t["data"]):
    st.caption(t["data_help"])
    names={"1":"1","2":"2","3_same":"3 · same","3_other":"3 · other","4":"4","5":"5"}
    with st.form("obs_form"):
        entered={}
        ca,cb=st.columns(2)
        for i,k in enumerate(DEFAULT_OBSERVATIONS):
            with (ca if i%2==0 else cb):
                entered[k]=st.text_input(names[k],value=", ".join(f"{x:g}" for x in st.session_state.observations[k]),key=f"obs_{k}")
        submitted=st.form_submit_button(t["apply"],type="primary")
    if submitted:
        try:
            changed={k:parse_waits(v) for k,v in entered.items()}
        except ValueError: st.error(t["invalid"])
        else:
            st.session_state.observations=changed
            st.success(t["saved"])
            st.rerun()
    if st.button(t["reset"],key="reset_examples"):
        st.session_state.observations=copy.deepcopy(DEFAULT_OBSERVATIONS)
        for k in DEFAULT_OBSERVATIONS:
            st.session_state.pop(f"obs_{k}",None)
        st.rerun()
    stream=io.StringIO()
    writer=csv.writer(stream)
    writer.writerow(("scenario","wait_minutes","source"))
    for k,observations in st.session_state.observations.items():
        for v in observations: writer.writerow((k,v,"illustrative_or_user_entered"))
    st.download_button(t["download"],stream.getvalue().encode('utf-8-sig'),
                       file_name="buffet_waiting_times.csv",mime="text/csv")

st.divider()
with st.expander(t["math"],expanded=False):
    st.caption(t["math_help"])
    st.markdown(f"**{t['math1']}**")
    st.latex(r"N=5\cdot5\cdot5=125")
    st.write("A = on time; B = choose buffet on floor 3; Ω = all routes (start, buffet, class).")
    st.markdown(f"**{t['math2']}**")
    st.latex(r"P(A)=\frac{n(A)}{N}")
    st.write(f"Sample estimate for this route: {result.success_count} / {result.sample_count} = {prob_pct:.1f}% (equally weighted examples).")
    st.markdown(f"**{t['math3']}**")
    st.latex(r"P(A\mid B)=\frac{P(A\cap B)}{P(B)}")
    st.write(f"P(on time | buffet floor {settings.buffet}, given route) ≈ {result.success_count}/{result.sample_count} = {prob_pct:.1f}%")
    st.latex(r"P(A)=\sum_{i=1}^{5}P(A\mid B_i)P(B_i)")
    weight=st.radio(t["weights"],("equal","popular_third"),key="weight_choice",horizontal=True,
                    format_func=lambda v:t['equal'] if v=="equal" else t['popular'])
    p_a,p_b,p_joint,p_product=independence_check(results,CHOICE_WEIGHTS[weight])
    st.write(f"P(A) = {' + '.join(f'{r.probability:.2f}×{w:.2f}' for r,w in zip(results,CHOICE_WEIGHTS[weight]))} = {p_a:.3f} ({100*p_a:.1f}%)")
    st.markdown(f"**{t['math4']}**")
    st.latex(r"P(A\cap B)\stackrel{?}{=}P(A)\,P(B)")
    st.write(f"P(A∩B) = {p_joint:.4f}; P(A)×P(B) = {p_a:.4f}×{p_b:.2f} = {p_product:.4f}. "
             +(t['ind'] if abs(p_joint-p_product)<1e-12 else t['notind']))
    st.markdown(f"**{t['math5']}**")
    st.latex(r"f_i=\frac{n_i}{n}")
    st.write(f"n = {result.sample_count}; chart above groups observed waiting times into intervals and counts their frequencies.")

st.caption(t["disclaimer"])

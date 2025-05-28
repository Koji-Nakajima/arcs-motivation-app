import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import io

# --- フォント設定（日本語は避けて英字） ---
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'sans-serif']

st.set_page_config(page_title="ARCS モチベーション診断", layout="centered")
st.title("🎓 学習モチベーション診断")
st.write("以下の質問に1〜100で答えて、この科目・課題に対する今のあなたの「やる気」を分析してみましょう。")

# セッション履歴保持
if 'records' not in st.session_state:
    st.session_state.records = []

# 入力フォーム
with st.form("arcs_form"):
    name = st.text_input("お名前（ニックネーム可）")
    user_id = st.text_input("学籍番号またはID")
    attention = st.slider("1. 学習にワクワク感がありますか？", 1, 100, 50)
    relevance = st.slider("2. 学びは自分に関係があると感じますか？", 1, 100, 50)
    confidence = st.slider("3. この課題をやりきれる自信はありますか？", 1, 100, 50)
    satisfaction = st.slider("4. 自分の学びに満足していますか？", 1, 100, 50)
    submitted = st.form_submit_button("診断する")

if submitted:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.subheader("🔍 診断結果")
    st.markdown("自己分析で30点未満を選んだ項目についてのアドバイス")
    st.markdown("このレポートは印刷するか、PDF等で保存しておきましょう。")
    st.markdown(f"### 【スコア】\n注意: {attention}｜関連性: {relevance}｜自信: {confidence}｜満足感: {satisfaction}")
    st.markdown("---")

    advice_blocks = []
    summary = []

    if attention < 30:
        advice_blocks.append(("学習にワクワク感がありますか？", attention,
                              "最近の学習が退屈に感じるなら、色を使ってノートを整理したり、生成AIでクイズを作ってみるのがおすすめです。"))
    if relevance < 30:
        advice_blocks.append(("学びは自分に関係があると感じますか_

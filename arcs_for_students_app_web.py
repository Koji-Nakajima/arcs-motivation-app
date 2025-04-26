# arcs_for_students_web.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import streamlit.components.v1 as components

# --- matplotlibの英字フォント設定（環境依存なし） ---
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'sans-serif']

# --- ページ設定 ---
st.set_page_config(page_title="ARCS モチベーション診断", layout="centered")

st.title("🎓 学習モチベーション診断")
st.write("以下の質問に1〜100で答えて、この科目・課題に対する今のあなたの「やる気」を分析してみましょう。")

# --- 入力フォーム ---
with st.form("arcs_form"):
    name = st.text_input("お名前（ニックネーム可）")
    user_id = st.text_input("学籍番号またはID")
    attention = st.slider("1. （指定された科目・課題について）学習にワクワク感がありますか？", 1, 100, 50)
    relevance = st.slider("2. ここでの学びは自分に関係があると感じますか？", 1, 100, 50)
    confidence = st.slider("3. この科目・課題をやりきれる自信はありますか？", 1, 100, 50)
    satisfaction = st.slider("4. ここまでの自分の学びに満足していますか？", 1, 100, 50)
    submitted = st.form_submit_button("診断する")

if submitted:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- アドバイス構築 ---
    st.subheader("🔍 診断結果")
    st.markdown("自己分析で30点未満を選んだ項目についてのアドバイス")
    st.markdown("---")

    advice_blocks = []

    if attention < 30:
        advice_blocks.append({
            "question": "（指定された科目・課題について）学習にワクワク感がありますか？",
            "score": attention,
            "advice": "最近の学習が退屈に感じるなら、「色を使ってノートを整理してみる」「生成AIを使って、学習内容をクイズ形式にしてみる」といった工夫を試してみましょう。",
            "evaluation": "次の学習時に「内容を思い出しやすかったか」「次に学ぶことにワクワクできたか」を振り返って○△×で記録してみましょう。"
        })

    if relevance < 30:
        advice_blocks.append({
            "question": "ここでの学びは自分に関係があると感じますか？",
            "score": relevance,
            "advice": "学んでいることが自分に関係ないと感じたら、「ここで学ぶ知識やスキルが将来どんなことに役立つか」を検索して、具体例を書き出してみましょう。",
            "evaluation": "例を探したあとの気持ちを書き出して、「自分との関連性を、自分なりに納得できたか」をメモに残しておきましょう。"
        })

    if confidence < 30:
        advice_blocks.append({
            "question": "この科目・課題をやりきれる自信はありますか？",
            "score": confidence,
            "advice": "難しそうだと感じたら、「一番簡単そうなところだけやってみる」「5分だけタイマーをセットして取りかかる」など、細切れにしてできるところから順番に進める方法を始めてみましょう。",
            "evaluation": "細切れにしてみた後、「やってみたら案外できたか？」を思い出して、○×△で記録しておきましょう。"
        })

    if satisfaction < 30:
        advice_blocks.append({
            "question": "ここまでの自分の学びに満足していますか？",
            "score": satisfaction,
            "advice": "ここまでに学んだことを「一言で説明する」「友達や家族に話す」「SNSや日記に書く」など、言葉にしてアウトプットすることで達成感を得やすくなります。",
            "evaluation": "その行動の後、「気分が少しでもよくなったかどうか」「振り返って意味を感じられたか」をチェックしてみましょう。"
        })

    if not advice_blocks:
        advice_blocks.append({
            "question": "全体の状態",
            "score": "-",
            "advice": "現在のモチベーションは良好のようです。この調子で継続して学習を進めましょう！",
            "evaluation": "定期的に記録して、状態の変化を確認するのがおすすめです。"
        })

    # --- レポート生成（ファイル保存なし） ---
    html_blocks = f"""
    <div style="font-family: Arial, sans-serif; border:1px solid #ccc; padding:20px;">
    <p><strong>氏名：</strong>{name}　　<strong>日時：</strong>{now}</p>
    <p style="margin-top: 1em; color: #444;">このレポートは印刷するか、PDF等で保存しておきましょう。</p>
    <p style="margin-top: 1.5em;"><strong style="font-size: 20px;">【スコア】</strong><br>
    <span style="font-size: 22px;">注意: {attention}｜関連性: {relevance}｜自信: {confidence}｜満足感: {satisfaction}</span></p>
    <hr>
    """
    for block in advice_blocks:
        html_blocks += f"""
        <h4>■ 質問：{block['question']}</h4>
        <p><strong>▶ アドバイス：</strong>{block['advice']}</p>
        <p><strong>▶ 自己評価方法：</strong>{block['evaluation']}</p>
        <hr>
        """
    html_blocks += "</div>"
    components.html(html_blocks, height=800, scrolling=True)

    # --- 推移グラフ（診断結果のみを可視化） ---
    st.markdown("---")
    st.subheader("📊 「やる気」の要因別 推移グラフ")

    # 1回の診断結果だけを使ってグラフ
    df_result = pd.DataFrame({
        '項目': ['Attention', 'Relevance', 'Confidence', 'Satisfaction'],
        'スコア': [attention, relevance, confidence, satisfaction]
    })

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(df_result['項目'], df_result['スコア'])
    ax.set_ylim(0, 100)
    ax.set_ylabel("Score (1–100)")
    ax.set_title(f"{name}'s Current Motivation")
    ax.grid(axis='y')
    st.pyplot(fig)

    st.markdown("""
    📝 **凡例の意味：**
    - Attention = 注意（学習に関心が向いているかどうか）
    - Relevance = 関連性（学習内容や方法が、自分に関連性がある、意味があると感じられているかどうか）
    - Confidence = 自信（学習を最後までやりきれるという見通しが経っているかどうか）
    - Satisfaction = 満足感（学習した結果に対する達成感や納得感があるかどうか）
    """)

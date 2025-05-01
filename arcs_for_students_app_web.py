import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import io

# --- フォント設定（日本語は避けて英字） ---
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'sans-serif']

st.set_page_config(page_title="ARCS モチベーション診断", layout="centered")
st.title("🎓 学習モチベーション診断（Web版）")
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
    st.markdown(f"### 【スコア】  \n注意: {attention}｜関連性: {relevance}｜自信: {confidence}｜満足感: {satisfaction}")
    st.markdown("---")

    advice_blocks = []
    summary = []

    if attention < 30:
        advice_blocks.append(("（指定された課題について）学習にワクワク感がありますか？", attention,
                              "最近の学習が退屈に感じるなら、「色を使ってノートを整理」「生成AIでクイズ化」など工夫を。"))
    if relevance < 30:
        advice_blocks.append(("ここでの学びは自分に関係があると感じますか？", relevance,
                              "学びの意味を見失っているかもしれません。将来どう活かせるか具体例を探してみましょう。"))
    if confidence < 30:
        advice_blocks.append(("この課題をやりきれる自信はありますか？", confidence,
                              "ハードルが高く感じるなら、「5分だけやってみる」「簡単な所から始める」が効果的です。"))
    if satisfaction < 30:
        advice_blocks.append(("自分の学びに満足していますか？", satisfaction,
                              "アウトプット（話す・書く・描く）することで、達成感を得やすくなります。"))

    if not advice_blocks:
        st.success("現在のモチベーションは良好のようです。この調子で継続して学びましょう！")
    else:
        for q, s, a in advice_blocks:
            st.info(f"■ 質問：{q}\n\n▶ スコア：{s}点\n\n▶ アドバイス：{a}")

    if satisfaction < 40 and relevance < 40:
        summary.append("満足感が低く、学びの関連性も感じにくいようです。まずは「なぜ学ぶのか」を見直すことで、手応えも得られるようになるかもしれません。")
    if attention > 60 and relevance < 40:
        summary.append("興味はあるのに意味がわからない、という状態かもしれません。学習の目的やゴールを再確認するとよいでしょう。")
    if confidence > 70 and satisfaction < 40:
        summary.append("やりきれる見通しがあるのに満足できていないようです。学習成果をアウトプットして、達成感を得る工夫をしてみましょう。")
    if relevance > 60 and confidence < 40:
        summary.append("自分にとって重要とは思っていても、やりきれる自信がないようです。計画を細かく分けて、小さな成功体験を積みましょう。")
    if attention < 40 and confidence > 60:
        summary.append("自信はあるのに興味がわかないようです。実生活や他分野との接点を見つけると、意義を再発見できるかもしれません。")

    if summary:
        st.markdown("### 🧠 アドバイスのまとめ（要因間の関連から）")
        for line in summary:
            st.warning(f"📌 {line}")
    summary_text = " / ".join(summary) if summary else ""

    # 診断履歴をセッションに保存
    st.session_state.records.append({
        "Date": now,
        "Attention": attention,
        "Relevance": relevance,
        "Confidence": confidence,
        "Satisfaction": satisfaction
    })

    # ダウンロードボタン（1件分）
    new_data = pd.DataFrame([{
        "Name": name,
        "ID": user_id,
        "Date": now,
        "Attention": attention,
        "Relevance": relevance,
        "Confidence": confidence,
        "Satisfaction": satisfaction,
        "Summary": summary_text
    }])
    csv_buffer = io.StringIO()
    new_data.to_csv(csv_buffer, index=False, encoding="utf-8")
    st.download_button(
        label="📥 この診断結果をCSVで保存",
        data=csv_buffer.getvalue(),
        file_name="my_motivation_result.csv",
        mime="text/csv"
    )

    # 推移グラフ（セッション内のみ）
    st.markdown("---")
    st.subheader("📈 モチベーション推移グラフ（このセッション内）")

    df_history = pd.DataFrame(st.session_state.records)
    if len(df_history) >= 2:
        df_history["Date"] = pd.to_datetime(df_history["Date"])
        df_history = df_history.sort_values("Date")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df_history["Date"], df_history["Attention"], label="Attention")
        ax.plot(df_history["Date"], df_history["Relevance"], label="Relevance")
        ax.plot(df_history["Date"], df_history["Confidence"], label="Confidence")
        ax.plot(df_history["Date"], df_history["Satisfaction"], label="Satisfaction")
        ax.set_ylabel("Score (1–100)")
        ax.set_xlabel("Date")
        ax.set_title(f"{name}'s Motivation Over Time")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)
    else:
        st.info("記録がまだ1件のため、推移グラフは表示されません。")

    # 常時表示：ARCS凡例
    st.markdown("""
    ---
    📝 **凡例の意味：**
    - Attention = 注意（学習に関心が向いているかどうか）  
    - Relevance = 関連性（学習内容や方法が、自分に関連性がある、意味があると感じられているかどうか）  
    - Confidence = 自信（学習を最後までやりきれるという見通しが経っているかどうか）  
    - Satisfaction = 満足感（学習した結果に対する達成感や納得感があるかどうか）
    """)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import io

# --- フォント設定（日本語を避けて英字） ---
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'sans-serif']

st.set_page_config(page_title="ARCS モチベーション診断", layout="centered")
st.title("🎓 学習モチベーション診断")
st.write("以下の質問に1〜100で答えて、この科目・課題に対する今のあなたの『やる気』をチェックしてみよう！")

if 'records' not in st.session_state:
    st.session_state.records = []

# 入力フォーム
with st.form("arcs_form"):
    name = st.text_input("お名前（ニックネームでもOK）")
    user_id = st.text_input("学籍番号やID（任意）")
    attention = st.slider("1. この勉強、なんかワクワクする？", 1, 100, 50)
    relevance = st.slider("2. これって、自分に関係あると思う？", 1, 100, 50)
    confidence = st.slider("3. やりきれそうな自信、ある？", 1, 100, 50)
    satisfaction = st.slider("4. 今までの勉強に、まあまあ満足してる？", 1, 100, 50)
    submitted = st.form_submit_button("診断する")

if submitted:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.subheader("🔍 診断結果")
    st.markdown("自己分析で30点未満を選んだ項目についてのアドバイス")
    st.markdown("このレポートは印刷するか、PDFなどで保存しておこう！")
    st.markdown(f"### 【スコア】  \\
注意: {attention}｜関連性: {relevance}｜自信: {confidence}｜満足感: {satisfaction}")
    st.markdown("---")

    advice_blocks = []
    summary = []

    if attention < 30:
        advice_blocks.append(("この勉強、なんかワクワクする？", attention,
                              "最近つまらないな〜って感じてるなら、ノートに色を使ったり、内容をクイズにしてみるとちょっと楽しくなるかも！"))
    if relevance < 30:
        advice_blocks.append(("これって、自分に関係あると思う？", relevance,
                              "『これ、将来どんなときに使うの？』って考えてみて。意外と身近なところで使えるヒントが見つかるかも！"))
    if confidence < 30:
        advice_blocks.append(("やりきれそうな自信、ある？", confidence,
                              "ハードル高いなって感じたら、『まずは5分だけやってみよう！』ってスタートすると意外と進められるよ。"))
    if satisfaction < 30:
        advice_blocks.append(("今までの勉強に、まあまあ満足してる？", satisfaction,
                              "やったことを誰かに話したり、日記やSNSに書いてみると『けっこう頑張ってるじゃん』って気づけるかも！"))

    if not advice_blocks:
        st.success("今のやる気はいい感じ！その調子で続けてみよう！")
    else:
        for q, s, a in advice_blocks:
            st.info(f"■ 質問：{q}\n\n▶ スコア：{s}点\n\n▶ アドバイス：{a}")

    # 要因間の傾向アドバイス
    if satisfaction < 40 and relevance < 40:
        summary.append("『なんで勉強してるんだっけ？』って気持ちになってるかも。学ぶ理由を見つけられると、もっと手応え出てくるよ！")
    if attention > 60 and relevance < 40:
        summary.append("おもしろそうなのに、意味が見えない…？そんなときはゴールをもう一度確認してみよう！")
    if confidence > 70 and satisfaction < 40:
        summary.append("やれそうなのに、いまいち達成感がない？学んだことを誰かに見せたり話すと、もっと満足できるかも！")
    if relevance > 60 and confidence < 40:
        summary.append("大事だとは思ってるけど、自信がない感じ？ちょっとずつ進めて、小さい成功を重ねていこう！")
    if attention < 40 and confidence > 60:
        summary.append("できそうだけど、おもしろくない…？身近な例と結びつけて考えると、意外と興味がわくかも！")

    if summary:
        st.markdown("### 🧠 アドバイスのまとめ（要因の組み合わせから）")
        for line in summary:
            st.warning(f"📌 {line}")
    summary_text = " / ".join(summary) if summary else ""

    # セッションに記録保存
    st.session_state.records.append({
        "Date": now,
        "Attention": attention,
        "Relevance": relevance,
        "Confidence": confidence,
        "Satisfaction": satisfaction
    })

    # CSV保存（1件）
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

    # 推移グラフ（セッション内）
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

    # ARCSモデル凡例
    st.markdown("""
    ---
    📝 **凡例の意味：**
    - Attention = 注意（学習に関心が向いているかどうか）  
    - Relevance = 関連性（学習内容や方法が、自分に関連性がある、意味があると感じられているかどうか）  
    - Confidence = 自信（学習を最後までやりきれるという見通しが経っているかどうか）  
    - Satisfaction = 満足感（学習した結果に対する達成感や納得感があるかどうか）
    """)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import tempfile
from datetime import datetime
from fpdf import FPDF

DATA_FILE = "arcs_data.csv"

# --------------------
# アドバイス生成
# --------------------
def generate_advice(row, previous_df=None):
    advice = []
    if row["attention"] <= 4:
        advice.append("【Attention】教材に問いや驚きを含め、好奇心を刺激しましょう。")
    if row["relevance"] <= 4:
        advice.append("【Relevance】学習が自分の目標とつながっているか意識しましょう。")
    if row["confidence"] <= 4:
        advice.append("【Confidence】成功体験を積む工夫をして自信を高めましょう。")
    if row["satisfaction"] <= 4:
        advice.append("【Satisfaction】成果を振り返る機会をつくり、達成感を感じましょう。")

    if previous_df is not None and len(previous_df) >= 1:
        last = previous_df.iloc[-1]
        diffs = {
            "attention": row["attention"] - last["attention"],
            "relevance": row["relevance"] - last["relevance"],
            "confidence": row["confidence"] - last["confidence"],
            "satisfaction": row["satisfaction"] - last["satisfaction"],
        }
        for key, diff in diffs.items():
            if diff < 0:
                advice.append(f"【{key.capitalize()}】前回より下がっています。要因を振り返ってみましょう。")
            elif diff > 0:
                advice.append(f"【{key.capitalize()}】前回より上昇しています。この調子を維持しましょう。")

    return advice

# --------------------
# 相関に基づくまとめアドバイス
# --------------------
def generate_summary_advice(user_df):
    if len(user_df) < 5:
        return "まだ十分なデータがないため、傾向分析はできません。"

    corr = user_df[["attention", "relevance", "confidence", "satisfaction"]].corr()
    summary = []
    if corr.loc["confidence", "satisfaction"] > 0.6:
        summary.append("💡Confidence（自信）が高まるとSatisfaction（満足感）も高まりやすい傾向があります。")
    if corr.loc["attention", "confidence"] > 0.6:
        summary.append("💡Attention（注意）が高まるとConfidence（自信）も上がる傾向があります。")
    if corr.loc["relevance", "confidence"] > 0.6:
        summary.append("💡Relevance（関連性）を感じるとConfidence（自信）も高まるようです。")

    return "\n".join(summary) if summary else "強い相関は見られませんが、継続して記録しましょう。"

# --------------------
# PDF生成（グラフ画像含む）
# --------------------
def generate_pdf_report(name, latest, advice_list, summary_text, graph_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="ARCS Motivation Report", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {latest['timestamp']}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", size=11)
    pdf.cell(200, 10, txt="Scores:", ln=True)
    for key in ["attention", "relevance", "confidence", "satisfaction"]:
        pdf.cell(200, 10, txt=f"{key.capitalize()}: {latest[key]}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Advice", ln=True)
    pdf.set_font("Arial", size=11)
    for a in advice_list:
        pdf.multi_cell(0, 10, txt="- " + a)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Summary Advice", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, txt=summary_text)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Motivation Trend Graph", ln=True)
    pdf.image(graph_path, w=180)

    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_pdf.name)
    return temp_pdf.name

# --------------------
# グラフ保存
# --------------------
def save_trend_graph(user_df):
    user_df["timestamp"] = pd.to_datetime(user_df["timestamp"])
    user_df = user_df.sort_values("timestamp")

    fig, ax = plt.subplots()
    for factor in ["attention", "relevance", "confidence", "satisfaction"]:
        ax.plot(user_df["timestamp"], user_df[factor], marker="o", label=factor)
    ax.set_xlabel("Date")
    ax.set_ylabel("Score")
    ax.legend()
    plt.xticks(rotation=30)

    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    fig.savefig(tmpfile.name, bbox_inches='tight')
    plt.close(fig)
    return tmpfile.name

# --------------------
# Streamlit UI
# --------------------
st.title("ARCS Motivation Self-Check")
name = st.text_input("Your Name")
attention = st.slider("Attention", 1, 7, 4)
relevance = st.slider("Relevance", 1, 7, 4)
confidence = st.slider("Confidence", 1, 7, 4)
satisfaction = st.slider("Satisfaction", 1, 7, 4)

if st.button("Submit"):
    if name.strip() == "":
        st.warning("Please enter your name.")
    else:
        new_entry = {
            "timestamp": datetime.now().isoformat(),
            "name": name,
            "attention": attention,
            "relevance": relevance,
            "confidence": confidence,
            "satisfaction": satisfaction,
        }
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        else:
            df = pd.DataFrame([new_entry])
        df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
        st.success("Saved!")

# --------------------
# 傾向・アドバイス・PDF
# --------------------
if name.strip() != "" and os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    user_df = df[df["name"] == name]
    if not user_df.empty:
        st.subheader(f"{name}'s Motivation Trend")
        graph_path = save_trend_graph(user_df)
        st.image(graph_path)

        latest = user_df.iloc[-1]
        previous = user_df.iloc[:-1] if len(user_df) > 1 else None
        advice = generate_advice(latest, previous)
        summary = generate_summary_advice(user_df)

        st.subheader("📌 Advice")
        for a in advice:
            st.write("- " + a)

        st.subheader("📊 Summary Advice")
        st.write(summary)

        if st.button("Generate PDF Report"):
            pdf_path = generate_pdf_report(name, latest, advice, summary, graph_path)
            with open(pdf_path, "rb") as f:
                st.download_button("Download PDF", f, file_name=f"ARCS_Report_{name}.pdf", mime="application/pdf")

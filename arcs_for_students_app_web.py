import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import tempfile
from datetime import datetime
from fpdf import FPDF

DATA_FILE = "arcs_data.csv"

# --- アドバイス生成 ---
def generate_advice(row, previous_df=None):
    advice = []
    if row["attention"] < 50:
        advice.append("【Attention】問いや驚きで好奇心を刺激しましょう。")
    if row["relevance"] < 50:
        advice.append("【Relevance】自分の目標との関係を考えましょう。")
    if row["confidence"] < 50:
        advice.append("【Confidence】できた経験を積みましょう。")
    if row["satisfaction"] < 50:
        advice.append("【Satisfaction】成果を振り返りましょう。")
    if previous_df is not None and len(previous_df) >= 1:
        last = previous_df.iloc[-1]
        for key in ["attention", "relevance", "confidence", "satisfaction"]:
            diff = row[key] - last[key]
            if diff < 0:
                advice.append(f"【{key.capitalize()}】前回より下がっています。")
            elif diff > 0:
                advice.append(f"【{key.capitalize()}】前回より向上しています。")
    return advice

# --- 相関ベースのまとめアドバイス ---
def generate_summary_advice(user_df):
    if len(user_df) < 5:
        return "十分なデータがないため、傾向分析はまだ行えません。"
    corr = user_df[["attention", "relevance", "confidence", "satisfaction"]].corr()
    summary = []
    if corr.loc["confidence", "satisfaction"] > 0.6:
        summary.append("💡Confidence（自信）が上がるとSatisfactionも上がりやすい傾向があります。")
    if corr.loc["attention", "confidence"] > 0.6:
        summary.append("💡Attention（注意）を高めるとConfidenceも向上しやすい傾向があります。")
    if corr.loc["relevance", "confidence"] > 0.6:
        summary.append("💡Relevance（関連性）を感じるとConfidenceが上がる傾向があります。")
    return "\n".join(summary) if summary else "強い傾向は見られませんでしたが、継続して記録しましょう。"

# --- グラフ保存 ---
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

# --- PDF出力 ---
def generate_pdf_report(name, student_id, latest, advice_list, summary_text, graph_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="ARCS Motivation Report", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Student ID: {student_id}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {latest['timestamp']}", ln=True)
    pdf.ln(5)
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
    pdf.cell(200, 10, txt="Motivation Trend Graph", ln=True)
    pdf.image(graph_path, w=180)
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_pdf.name)
    return temp_pdf.name

# --- UI表示 ---
st.title("ARCS Motivation Self-Check")

student_id = st.text_input("Student ID")
name = st.text_input("Your Name")

attention = st.slider("Attention", 1, 100, 50)
relevance = st.slider("Relevance", 1, 100, 50)
confidence = st.slider("Confidence", 1, 100, 50)
satisfaction = st.slider("Satisfaction", 1, 100, 50)

if st.button("Submit"):
    if student_id.strip() == "" or name.strip() == "":
        st.warning("Student IDとNameの両方を入力してください。")
    else:
        new_entry = {
            "timestamp": datetime.now().isoformat(),
            "student_id": student_id,
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
        st.success("保存しました。")

        # 保存後すぐに傾向とアドバイス表示
        user_df = df[df["student_id"] == student_id]
        if not user_df.empty:
            st.subheader(f"{name} さんのモチベーション傾向")
            graph_path = save_trend_graph(user_df)
            st.image(graph_path)

            latest = user_df.iloc[-1]
            previous = user_df.iloc[:-1] if len(user_df) > 1 else None
            advice = generate_advice(latest, previous)
            summary = generate_summary_advice(user_df)

            st.subheader("📌 アドバイス")
            for a in advice:
                st.write("- " + a)

            st.subheader("📊 まとめアドバイス")
            st.write(summary)

            if st.button("PDFで出力する"):
                pdf_path = generate_pdf_report(name, student_id, latest, advice, summary, graph_path)
                with open(pdf_path, "rb") as f:
                    st.download_button("Download PDF", f, file_name=f"ARCS_Report_{student_id}.pdf", mime="application/pdf")

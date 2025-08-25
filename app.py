import streamlit as st
import json
import os
import pandas as pd
import io
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(page_title="📋 Ghi nhận công việc", page_icon="✅", layout="wide")
st.title("📋 Ghi nhận công việc")
st.markdown("Ứng dụng ghi nhận và báo cáo công việc chuyên nghiệp dành cho nhóm hoặc cá nhân.")

DATA_FILE = "tasks.json"
tasks = []

# Đọc dữ liệu
if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            tasks = json.load(f)
    except json.JSONDecodeError:
        st.warning("⚠️ File dữ liệu bị lỗi. Đang khởi tạo lại danh sách trống.")
        tasks = []

# --- Biểu mẫu ghi nhận ---
with st.form("task_form"):
    st.markdown("### 👤 Thông tin người thực hiện")
    name = st.text_input("Tên người thực hiện")
    department = st.text_input("Phòng ban")

    st.markdown("### 📁 Thông tin công việc")
    project = st.selectbox("Dự án", options=["Dự án 43DTM", "Dự án VVIP", "Dự án GALERY"])
    category = st.selectbox("Hạng mục", options=["Thiết kế", "Mua sắm", "Gia công", "Vận chuyển", "Lắp dựng"])
    task = st.text_area("Nội dung công việc")
    note = st.text_area("Ghi chú")

    st.markdown("### ⏰ Thời gian thực hiện")
    date = st.date_input("Ngày thực hiện", value=datetime.today())
    time = st.time_input("Thời gian bắt đầu", value=datetime.now().time())
    repeat = st.number_input("Số lần thực hiện", min_value=1, step=1, value=1)

    st.markdown("### ☑️ Trạng thái công việc")
    status = st.radio("Trạng thái", options=["Hoàn thành", "Đang thực hiện", "Chờ duyệt", "Ngưng chờ", "Bỏ"])

    submitted = st.form_submit_button("✅ Ghi nhận")
    if submitted:
        new_task = {
            "name": name.strip(),
            "department": department.strip(),
            "project": project,
            "category": category,
            "task": task.strip(),
            "note": note.strip(),
            "date": str(date),
            "time": time.strftime("%H:%M"),
            "repeat": repeat,
            "status": status
        }
        tasks.append(new_task)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        st.success("🎉 Công việc đã được ghi nhận!")
        st.experimental_rerun()



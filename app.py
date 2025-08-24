import streamlit as st
import json
import os
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="Ghi nhận công việc", page_icon="📝")

st.title("📝 Ghi nhận công việc")
st.markdown("Nhập thông tin công việc bạn đã hoàn thành để lưu lại và thống kê.")

# File lưu dữ liệu
DATA_FILE = "tasks.json"
tasks = []

# Đọc dữ liệu từ file JSON, xử lý lỗi nếu có
if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            tasks = json.load(f)
    except json.JSONDecodeError:
        st.warning("⚠️ File dữ liệu bị lỗi. Đang khởi tạo lại danh sách trống.")
        tasks = []

# Form nhập công việc
with st.form("task_form"):
    name = st.text_input("👤 Tên người thực hiện")
    task = st.text_area("📌 Nội dung công việc")
    date = st.date_input("📅 Ngày thực hiện", value=datetime.today())
    time = st.time_input("⏰ Thời gian thực hiện", value=datetime.now().time())
    repeat = st.number_input("🔁 Lần thực hiện", min_value=1, step=1, value=1)
    submitted = st.form_submit_button("✅ Ghi nhận")

    if submitted:
        new_task = {
            "name": name,
            "task": task,
            "date": str(date),
            "time": time.strftime("%H:%M"),
            "repeat": repeat
        }
        tasks.append(new_task)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        st.success("🎉 Đã ghi nhận công việc!")

# Hiển thị thống kê nếu có dữ liệu
if tasks:
    st.subheader("📊 Danh sách công việc đã ghi nhận")
    df = pd.DataFrame(tasks)
    st.dataframe(df)

    # Thống kê theo ngày
    st.subheader("📅 Số lượng công việc theo ngày")
    count_by_date = df["date"].value_counts().sort_index()
    st.bar_chart(count_by_date)

    # Tải xuống file Excel
    st.subheader("📥 Tải danh sách công việc")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Tasks")
    st.download_button(
        label="📂 Tải xuống Excel",
        data=output.getvalue(),
        file_name="danh_sach_cong_viec.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Chưa có công việc nào được ghi nhận.")



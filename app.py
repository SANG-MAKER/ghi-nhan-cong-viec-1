import streamlit as st
import json
import os
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="Ghi nhận công việc", page_icon="📝")

st.title("📝 Ghi nhận công việc")
st.markdown("Hệ thống ghi nhận công việc chuyên nghiệp dành cho nhóm hoặc cá nhân.")

# File dữ liệu
DATA_FILE = "tasks.json"
tasks = []

# Đọc dữ liệu từ file JSON
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
    department = st.text_input("Phòng ban (nếu có)")

    st.markdown("### 📁 Thông tin công việc")
    project = st.selectbox("Dự án", options=["43 DTM", "GALLERY", "VVIP"])
    category = st.selectbox("Hạng mục", options=["Thiết kế", "Mua sắm ", "Gia công", "Vận chuyển", "Lắp dựng"])
    task = st.text_area("Nội dung công việc")
    note = st.text_area("Ghi chú bổ sung")

    st.markdown("### ⏰ Thời gian thực hiện")
    date = st.date_input("Ngày thực hiện", value=datetime.today())
    time = st.time_input("Thời gian bắt đầu", value=datetime.now().time())
    repeat = st.number_input("Số lần thực hiện", min_value=1, step=1, value=1)

    st.markdown("### ☑️ Trạng thái công việc")
    status_done = st.checkbox("Hoàn thành")
    status_pending = st.checkbox("Đang thực hiện")
    status_review = st.checkbox("Chờ duyệt")

    submitted = st.form_submit_button("✅ Ghi nhận")

    if submitted:
        status_list = []
        if status_done: status_list.append("Hoàn thành")
        if status_pending: status_list.append("Đang thực hiện")
        if status_review: status_list.append("Chờ duyệt")

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
            "status": ", ".join(status_list)
        }
        tasks.append(new_task)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        st.success("🎉 Đã ghi nhận công việc!")

# --- Hiển thị dữ liệu ---
if tasks:
    st.subheader("📊 Danh sách công việc đã ghi nhận")
    df = pd.DataFrame(tasks)
    st.dataframe(df)

    # Bộ lọc theo hạng mục
    st.subheader("📂 Xuất báo cáo theo hạng mục")
    unique_categories = df["category"].dropna().unique()
    selected_category = st.selectbox("🧩 Chọn hạng mục để xuất báo cáo", options=unique_categories)

    filtered_df = df[df["category"] == selected_category]
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        filtered_df.to_excel(writer, index=False, sheet_name="Hạng mục")
    st.download_button(
        label=f"📥 Tải báo cáo hạng mục '{selected_category}'",
        data=output.getvalue(),
        file_name=f"bao_cao_{selected_category}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Tải toàn bộ danh sách
    st.subheader("📥 Tải toàn bộ danh sách công việc")
    full_output = io.BytesIO()
    with pd.ExcelWriter(full_output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Tất cả công việc")
    st.download_button(
        label="📂 Tải toàn bộ Excel",
        data=full_output.getvalue(),
        file_name="danh_sach_cong_viec.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Chưa có công việc nào được ghi nhận.")




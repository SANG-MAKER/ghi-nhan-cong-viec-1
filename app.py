import streamlit as st
import json
import os
import pandas as pd
import io
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="📋 Ghi nhận công việc", page_icon="✅", layout="wide")
st.title("📋 Ghi nhận công việc")
DATA_FILE = "tasks.json"

# Load dữ liệu
if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            tasks = json.load(f)
    except:
        tasks = []
else:
    tasks = []

# --- Biểu mẫu ghi nhận ---
with st.form("task_form"):
    st.subheader("📝 Ghi nhận công việc mới")
    name = st.text_input("👤 Tên người thực hiện")
    department = st.text_input("🏢 Phòng ban")
    project = st.selectbox("📁 Dự án", ["Dự án 43 DTM", "Dự án GALERY", "Dự án VVIP"])
    category = st.selectbox("📂 Hạng mục", ["Thiết kế", "Mua sắm", "Gia công", "Vận chuyển", "Lắp dựng"])
    task = st.text_area("📌 Nội dung công việc")
    note = st.text_area("🗒 Ghi chú")
    date = st.date_input("📅 Ngày thực hiện", value=datetime.today())
    time = st.time_input("⏰ Thời gian bắt đầu", value=datetime.now().time())
    repeat = st.number_input("🔁 Số lần thực hiện", min_value=1, step=1, value=1)
    status = st.radio("📍 Trạng thái", ["Hoàn thành", "Đang thực hiện", "Chờ duyệt"])
    progress = st.slider("📈 % Hoàn thành", 0, 100, value=100 if status == "Hoàn thành" else 0)
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
            "status": status,
            "progress": progress
        }
        tasks.append(new_task)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        st.success("🎉 Công việc đã được ghi nhận!")

# --- Hiển thị bảng lịch sử ---
if tasks:
    df = pd.DataFrame(tasks)
    df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"])
    df.sort_values("datetime", inplace=True)

    st.subheader("📋 Bảng lịch sử công việc")

    # Bộ lọc
    with st.expander("🔍 Bộ lọc"):
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_person = st.multiselect("👤 Người thực hiện", options=df["name"].unique())
        with col2:
            selected_project = st.multiselect("📁 Dự án", options=df["project"].unique())
        with col3:
            selected_status = st.multiselect("📍 Trạng thái", options=df["status"].unique())

        filtered_df = df.copy()
        if selected_person:
            filtered_df = filtered_df[filtered_df["name"].isin(selected_person)]
        if selected_project:
            filtered_df = filtered_df[filtered_df["project"].isin(selected_project)]
        if selected_status:
            filtered_df = filtered_df[filtered_df["status"].isin(selected_status)]

    # Màu sắc trạng thái
    def color_status(row):
        if row["status"] == "Hoàn thành":
            return "background-color: #d4edda"
        elif row["status"] == "Đang thực hiện":
            return "background-color: #fff3cd"
        else:
            return "background-color: #f8d7da"

    styled_df = filtered_df.style.applymap(
        lambda val: "color: black", subset=["status"]
    ).applymap(
        lambda val: "font-weight: bold", subset=["status"]
    ).apply(
        lambda row: [color_status(row)] * len(row), axis=1
    )

    st.dataframe(styled_df, use_container_width=True)

    # Chỉnh sửa từng dòng
    st.subheader("✏️ Chỉnh sửa công việc")
    for i, row in filtered_df.iterrows():
        with st.expander(f"{row['date']} - {row['name']} - {row['task']}"):
            new_task = st.text_area("📌 Nội dung", value=row["task"], key=f"task_{i}")
            new_note = st.text_area("🗒 Ghi chú", value=row["note"], key=f"note_{i}")
            new_status = st.selectbox("📍 Trạng thái", ["Hoàn thành", "Đang thực hiện", "Chờ duyệt"], index=["Hoàn thành", "Đang thực hiện", "Chờ duyệt"].index(row["status"]), key=f"status_{i}")
            new_progress = st.slider("📈 % Hoàn thành", 0, 100, value=int(row["progress"]), key=f"progress_{i}")
            if st.button("💾 Lưu", key=f"save_{i}"):
                df.at[i, "task"] = new_task
                df.at[i, "note"] = new_note
                df.at[i, "status"] = new_status
                df.at[i, "progress"] = new_progress
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(df.drop(columns=["datetime"]).to_dict(orient="records"), f, ensure_ascii=False, indent=2)
                st.success("✅ Đã lưu thay đổi!")

    # Xuất Excel
    st.subheader("📥 Tải danh sách công việc")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.drop(columns=["datetime"]).to_excel(writer, index=False, sheet_name="Tasks")
    st.download_button(
        label="📂 Tải xuống Excel",
        data=output.getvalue(),
        file_name="danh_sach_cong_viec.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("📭 Chưa có công việc nào được ghi nhận.")





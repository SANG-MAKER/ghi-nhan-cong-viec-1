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

# --- Hiển thị & chỉnh sửa lịch sử ---
if tasks:
    df = pd.DataFrame(tasks)
    df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"])
    df.sort_values("datetime", inplace=True)

    st.subheader("📄 Lịch sử ghi nhận công việc")

    grouped = df.groupby(["project", "category"])
    for (proj, cat), group in grouped:
        with st.expander(f"📁 {proj} - 📂 {cat} ({len(group)} công việc)"):
            for i, row in group.iterrows():
                with st.container():
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"**📌 {row['task']}**  \n🗓 {row['date']} - 👤 {row['name']} ({row['department']})")
                        new_task = st.text_area("📌 Nội dung", value=row["task"], key=f"task_{i}")
                        new_note = st.text_area("🗒 Ghi chú", value=row["note"], key=f"note_{i}")
                    with col2:
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

    # --- Dashboard ---
    st.subheader("📊 Thống kê tổng quan")
    total = len(df)
    done = len(df[df["status"] == "Hoàn thành"])
    percent_done = round((done / total) * 100, 1) if total > 0 else 0
    col1, col2, col3 = st.columns(3)
    col1.metric("✅ % Hoàn thành", f"{percent_done}%")
    col2.metric("📌 Tổng công việc", total)
    col3.metric("⏳ Đang thực hiện", len(df[df["status"] == "Đang thực hiện"]))

    fig_status = px.pie(df, names="status", title="Tỷ lệ trạng thái công việc")
    st.plotly_chart(fig_status, use_container_width=True)

    fig_cat = px.bar(df["category"].value_counts(), orientation="h", title="Số lượng công việc theo hạng mục")
    st.plotly_chart(fig_cat, use_container_width=True)

    # --- Xuất Excel ---
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





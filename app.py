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
    project = st.selectbox("Dự án", options=["Dự án 43 DTM", "Dự án GALERY", "Dự án VVIP"])
    category = st.selectbox("Hạng mục", options=["Thiết kế", "Mua sắm", "Gia công", "Vận chuyển", "Lắp dựng"])
    task = st.text_area("Nội dung công việc")
    note = st.text_area("Ghi chú")

    st.markdown("### ⏰ Thời gian thực hiện")
    date = st.date_input("Ngày thực hiện", value=datetime.today())
    time = st.time_input("Thời gian bắt đầu", value=datetime.now().time())
    repeat = st.number_input("Số lần thực hiện", min_value=1, step=1, value=1)

    st.markdown("### ☑️ Trạng thái công việc")
    status = st.radio("Trạng thái", options=["Hoàn thành", "Đang thực hiện", "Chờ duyệt"])
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
        st.markdown("### 📄 Công việc vừa ghi nhận")
        st.dataframe(pd.DataFrame([new_task]), use_container_width=True)

# --- Dashboard & Báo cáo ---
if tasks:
    df = pd.DataFrame(tasks)
    st.markdown("## 📊 Dashboard báo cáo công việc")

    col1, col2, col3 = st.columns(3)
    total = len(df)
    done = len(df[df["status"] == "Hoàn thành"])
    percent_done = round((done / total) * 100, 1) if total > 0 else 0
    col1.metric("✅ % Hoàn thành", f"{percent_done}%")
    col2.metric("📌 Tổng công việc", total)
    col3.metric("⏳ Đang thực hiện", len(df[df["status"] == "Đang thực hiện"]))

    # Biểu đồ trạng thái
    status_count = df["status"].value_counts()
    fig_status = px.pie(names=status_count.index, values=status_count.values, title="Tỷ lệ trạng thái công việc")
    st.plotly_chart(fig_status, use_container_width=True)

    # Biểu đồ theo ngày
    fig_date = px.bar(df["date"].value_counts().sort_index(), title="Số lượng công việc theo ngày")
    st.plotly_chart(fig_date, use_container_width=True)

    # Biểu đồ theo hạng mục
    fig_cat = px.bar(df["category"].value_counts(), orientation="h", title="Số lượng công việc theo hạng mục")
    st.plotly_chart(fig_cat, use_container_width=True)

    # Nhắc nhở công việc chờ duyệt quá 3 ngày
    st.markdown("### 🔔 Nhắc nhở công việc chờ duyệt")
    df["date_obj"] = pd.to_datetime(df["date"])
    overdue = df[(df["status"] == "Chờ duyệt") & (df["date_obj"] < datetime.today() - timedelta(days=3))]
    if not overdue.empty:
        st.warning(f"⚠️ Có {len(overdue)} công việc chờ duyệt quá 3 ngày!")
        st.dataframe(overdue.drop(columns=["date_obj"]))
    else:
        st.success("✅ Không có công việc chờ duyệt quá hạn.")

    # Cập nhật trạng thái bằng checkbox
    st.markdown("### ☑️ Cập nhật trạng thái công việc")
    for i, row in df.iterrows():
        col1, col2 = st.columns([5, 1])
        with col1:
            st.write(f"📌 {row['task']} ({row['date']}) - {row['name']}")
        with col2:
            if st.checkbox("✅ Hoàn thành", key=f"done_{i}"):
                df.at[i, "status"] = "Hoàn thành"
                df.at[i, "progress"] = 100
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(df.drop(columns=["date_obj"]).to_dict(orient="records"), f, ensure_ascii=False, indent=2)
                st.success(f"🎯 Đã cập nhật: {row['task']}")

    # Tải toàn bộ danh sách
    st.markdown("### 📥 Tải danh sách công việc")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.drop(columns=["date_obj"]).to_excel(writer, index=False, sheet_name="Tasks")
    st.download_button(
        label="📂 Tải xuống Excel",
        data=output.getvalue(),
        file_name="danh_sach_cong_viec.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("📭 Chưa có công việc nào được ghi nhận.")





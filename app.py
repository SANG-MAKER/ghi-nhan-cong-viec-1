import streamlit as st
import json
import os
import pandas as pd
import io
from datetime import datetime
import plotly.express as px

# --- Cấu hình giao diện ---
st.set_page_config(page_title="📋 Ghi nhận công việc", page_icon="✅", layout="wide")
st.title("📋 Ghi nhận công việc")
st.markdown("Ứng dụng ghi nhận và báo cáo công việc chuyên nghiệp dành cho nhóm hoặc cá nhân.")

# --- Đường dẫn file dữ liệu ---
DATA_FILE = "tasks.json"

# --- Hàm xử lý dữ liệu ---
def load_tasks(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.warning("⚠️ File dữ liệu bị lỗi. Đang khởi tạo lại danh sách trống.")
    return []

def save_tasks(file_path, tasks):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Tasks')
    return output.getvalue()

# --- Đọc dữ liệu ---
tasks = load_tasks(DATA_FILE)

# --- Biểu mẫu ghi nhận công việc ---
with st.form("task_form"):
    st.markdown("### 📝 Ghi nhận công việc")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("👤 Tên người thực hiện")
        project = st.selectbox("📁 Dự án", ["Dự án 43DTM", "Dự án VVIP", "Dự án GALERY"])
        task = st.text_area("🛠️ Nội dung công việc")
        date = st.date_input("📅 Ngày thực hiện", value=datetime.today())
    with col2:
        department = st.text_input("🏢 Phòng ban")
        category = st.selectbox("📂 Hạng mục", ["Thiết kế", "Mua sắm", "Gia công", "Vận chuyển", "Lắp dựng"])
        note = st.text_area("🗒️ Ghi chú")
        time = st.time_input("⏰ Thời gian bắt đầu", value=datetime.now().time())

    col3, col4 = st.columns([1, 2])
    with col3:
        repeat = st.number_input("🔁 Số lần thực hiện", min_value=1, step=1, value=1)
    with col4:
        status = st.radio("📌 Trạng thái công việc", ["Hoàn thành", "Đang thực hiện", "Chờ duyệt", "Ngưng chờ", "Bỏ"])

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
        save_tasks(DATA_FILE, tasks)
        st.success("🎉 Công việc đã được ghi nhận!")
        st.rerun()

# --- Hiển thị dữ liệu và biểu đồ ---
if tasks:
    df = pd.DataFrame(tasks)
    st.markdown("### 📊 Danh sách công việc đã ghi nhận")
    st.dataframe(df, use_container_width=True)

    # --- Biểu đồ trạng thái công việc ---
    st.markdown("### 📈 Thống kê trạng thái công việc")
    status_chart = df["status"].value_counts().reset_index()
    status_chart.columns = ["Trạng thái", "Số lượng"]
    fig = px.pie(status_chart, names="Trạng thái", values="Số lượng", title="Tỷ lệ trạng thái công việc", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

    # --- Nút tải Excel ---
    excel_data = to_excel(df)
    st.download_button(
        label="📥 Tải xuống danh sách công việc (Excel)",
        data=excel_data,
        file_name="tasks.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("📭 Chưa có công việc nào được ghi nhận.")




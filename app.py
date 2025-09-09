import streamlit as st
import json
import os
import pandas as pd
import io
from datetime import datetime, date
import plotly.express as px
import calendar

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

# --- Phân quyền người dùng ---
role = st.sidebar.selectbox("🔐 Vai trò người dùng", ["Nhân viên", "Quản lý"])
st.sidebar.markdown(f"**Bạn đang đăng nhập với vai trò:** `{role}`")

# --- Đọc dữ liệu ---
tasks = load_tasks(DATA_FILE)

# --- Biểu mẫu ghi nhận công việc ---
with st.expander("📝 Ghi nhận công việc mới", expanded=(role == "Nhân viên")):
    with st.form("task_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("👤 Tên người thực hiện")
            department = st.text_input("🏢 Phòng ban")
            project = st.selectbox("📁 Dự án", ["Dự án 43DTM", "Dự án VVIP", "Dự án GALERY"])
        with col2:
            category = st.selectbox("📂 Hạng mục", ["Thiết kế", "Mua sắm", "Gia công", "Vận chuyển", "Lắp dựng"])
            date_work = st.date_input("📅 Ngày thực hiện", value=datetime.today())
            time = st.time_input("⏰ Thời gian bắt đầu", value=datetime.now().time())

        task = st.text_area("🛠️ Nội dung công việc")
        note = st.text_area("🗒️ Ghi chú")
        deadline = st.date_input("📅 Ngày tới hạn")
        feedback = st.text_area("💬 Phản hồi")
        feedback_date = st.date_input("📅 Ngày phản hồi", value=None)

        col3, col4 = st.columns([1, 2])
        with col3:
            repeat = st.number_input("🔁 Số lần thực hiện", min_value=1, step=1, value=1)
        with col4:
            status = st.radio("📌 Trạng thái công việc", ["Hoàn thành", "Đang thực hiện", "Chờ duyệt", "Ngưng chờ", "Bỏ"])

        next_plan = ""
        if status != "Hoàn thành":
            next_plan = st.date_input("📆 Ngày dự kiến hoàn thành tiếp theo", value=None)

        submitted = st.form_submit_button("✅ Ghi nhận")
        if submitted:
            new_task = {
                "name": name.strip(),
                "department": department.strip(),
                "project": project,
                "category": category,
                "task": task.strip(),
                "note": note.strip(),
                "date": str(date_work),
                "time": time.strftime("%H:%M"),
                "repeat": repeat,
                "status": status,
                "deadline": str(deadline),
                "feedback": feedback.strip(),
                "feedback_date": str(feedback_date) if feedback_date else "",
                "next_plan": str(next_plan) if next_plan else ""
            }
            tasks.append(new_task)
            save_tasks(DATA_FILE, tasks)
            st.success("🎉 Công việc đã được ghi nhận!")
            st.rerun()

# --- Hiển thị dữ liệu và biểu đồ ---
if tasks:
    df = pd.DataFrame(tasks)

    # Bộ lọc dữ liệu
    with st.sidebar.expander("🔎 Bộ lọc dữ liệu"):
        selected_project = st.selectbox("📁 Lọc theo dự án", ["Tất cả"] + df["project"].unique().tolist())
        selected_status = st.selectbox("📌 Lọc theo trạng thái", ["Tất cả"] + df["status"].unique().tolist())
        selected_department = st.selectbox("🏢 Lọc theo phòng ban", ["Tất cả"] + df["department"].unique().tolist())
        selected_name = st.selectbox("👤 Lọc theo người thực hiện", ["Tất cả"] + df["name"].unique().tolist())

    # Áp dụng bộ lọc
    if selected_project != "Tất cả":
        df = df[df["project"] == selected_project]
    if selected_status != "Tất cả":
        df = df[df["status"] == selected_status]
    if selected_department != "Tất cả":
        df = df[df["department"] == selected_department]
    if selected_name != "Tất cả":
        df = df[df["name"] == selected_name]

    # Thêm cột nhắc việc
    df["🔔 Nhắc việc"] = df["status"].apply(lambda s: "Cần nhắc" if s != "Hoàn thành" else "")

    # Cảnh báo tới hạn
    def check_overdue(row):
        if row["status"] != "Hoàn thành":
            try:
                deadline_date = datetime.strptime(row["deadline"], "%Y-%m-%d").date()
                if deadline_date < date.today():
                    return "🔴 Đã quá hạn!"
            except:
                return ""
        return ""

    df["⚠️ Cảnh báo"] = df.apply(check_overdue, axis=1)

    # Dashboard tổng quan
    with st.expander("📊 Dashboard tổng quan", expanded=(role == "Quản lý")):
        col1, col2, col3 = st.columns(3)
        col1.metric("📌 Tổng công việc", len(df))
        col2.metric("✅ Hoàn thành", df[df["status"] == "Hoàn thành"].shape[0])
        col3.metric("🔔 Cần nhắc", df[df["🔔 Nhắc việc"] == "Cần nhắc"].shape[0])

    with st.expander("📅 Lịch công việc"):
        df["Ngày"] = pd.to_datetime(df["date"])
        calendar_df = df.groupby(df["Ngày"].dt.date)["task"].count().reset_index()
        calendar_df.columns = ["Ngày", "Số lượng"]
        fig_cal = px.bar(calendar_df, x="Ngày", y="Số lượng", title="Lịch công việc theo ngày", color="Số lượng")
        st.plotly_chart(fig_cal, use_container_width=True)

    with st.expander("📊 Danh sách công việc đã ghi nhận", expanded=True):
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        if st.button("💾 Lưu thay đổi"):
            tasks = edited_df.to_dict(orient="records")
            save_tasks(DATA_FILE, tasks)
            st.success("✅ Dữ liệu đã được cập nhật!")
            st.rerun()

    with st.expander("📈 Thống kê công việc theo trạng thái"):
        status_chart = df["status"].value_counts().reset_index()
        status_chart.columns = ["Trạng thái", "Số lượng"]
        fig = px.pie(status_chart, names="Trạng thái", values="Số lượng", title="Tỷ lệ trạng thái công việc", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("📈 Công việc cần nhắc"):
        reminder_chart = df["🔔 Nhắc việc"].value_counts().reset_index()
        reminder_chart.columns = ["Nhắc việc", "Số lượng"]
        fig2 = px.bar(reminder_chart, x="Nhắc việc", y="Số lượng", title="Số lượng công việc cần nhắc", color="Nhắc việc")
        st.plotly_chart(fig2, use_container_width=True)



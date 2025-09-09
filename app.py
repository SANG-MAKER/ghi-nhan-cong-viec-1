import streamlit as st
import json
import os
import pandas as pd
import io
from datetime import datetime, date
import plotly.express as px

# --- Cấu hình giao diện ---
st.set_page_config(page_title="📋 TRACKING", page_icon="✅", layout="wide")
st.title("📋 TRACKING")
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
            task_type = st.selectbox("🧱 Công việc", ["Thiết kế", "Mua sắm", "Gia công", "Vận chuyển", "Lắp dựng"])
            task_group = st.text_input("📂 Hạng mục (nhập thủ công)")
            date_work = st.date_input("📅 Ngày thực hiện", value=datetime.today())
            time = st.time_input("⏰ Thời gian bắt đầu", value=datetime.now().time())

        task = st.text_area("🛠️ Nội dung công việc")
        note = st.text_area("🗒️ Ghi chú")
        feedback = st.text_area("💬 Phản hồi")
        feedback_date = st.date_input("📅 Ngày phản hồi", value=None)
        deadline = st.date_input("📅 Ngày tới hạn")

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
                "task_type": task_type,
                "task_group": task_group.strip(),
                "task": task.strip(),
                "note": note.strip(),
                "feedback": feedback.strip(),
                "feedback_date": str(feedback_date) if feedback_date else "",
                "date": str(date_work),
                "time": time.strftime("%H:%M"),
                "repeat": repeat,
                "status": status,
                "deadline": str(deadline),
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

    if selected_project != "Tất cả":
        df = df[df["project"] == selected_project]
    if selected_status != "Tất cả":
        df = df[df["status"] == selected_status]
    if selected_department != "Tất cả":
        df = df[df["department"] == selected_department]
    if selected_name != "Tất cả":
        df = df[df["name"] == selected_name]

    df["🔔 Nhắc việc"] = df["status"].apply(lambda s: "Cần nhắc" if s != "Hoàn thành" else "")

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
        fig_status = px.pie(status_chart, names="Trạng thái", values="Số lượng", title="Tỷ lệ trạng thái công việc", hole=0.4)
        st.plotly_chart(fig_status, use_container_width=True)

    with st.expander("📊 Thống kê công việc theo Hạng mục và Dự án"):
        stacked_df = df.groupby(["project", "task_group"]).size().reset_index(name="Số lượng")
        fig_stacked = px.bar(
            stacked_df,
            x="project",
            y="Số lượng",
            color="task_group",
            title="Số lượng công việc theo Hạng mục trong từng Dự án",
            barmode="stack"
        )
        st.plotly_chart(fig_stacked, use_container_width=True)

    with st.expander("📊 Thống kê theo loại Công việc"):
        type_chart = df["task_type"].value_counts().reset_index()
        type_chart.columns = ["Công việc", "Số lượng"]
        fig_type = px.bar(type_chart, x="Công việc", y="Số lượng", title="Số lượng công việc theo loại", color="Công việc")
        st.plotly_chart(fig_type, use_container_width=True)

    with st.expander("📊 KPI theo nhân sự"):
        kpi_df = df.groupby("name")["status"].value_counts().unstack(fill_value=0)
        kpi_df["Tổng công việc"] = kpi_df.sum(axis=1)
        kpi_df = kpi_df.sort_values("Tổng công việc", ascending=False)
        st.dataframe(kpi_df, use_container_width=True)

    with st.expander("📅 Lịch công việc theo ngày"):
        df["Ngày thực hiện"] = pd.to_datetime(df["date"], errors="coerce")
        calendar_df = df.groupby(df["Ngày thực hiện"].dt.date)["task"].count().reset_index()
        calendar_df.columns = ["Ngày", "Số lượng công việc"]
        fig_calendar = px.bar(
            calendar_df,
            x="Ngày",
            y="Số lượng công việc",
            title="Lịch công việc theo ngày",
            color="Số lượng công việc"
        )
        st.plotly_chart(fig_calendar, use_container_width=True)

    with st.expander("📥 Tải xuống dữ liệu"):
        excel_data = to_excel(df)
        st.download_button


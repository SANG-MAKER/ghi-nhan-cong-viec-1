import streamlit as st
import json
import os
import pandas as pd
import io
from datetime import datetime, date
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
with st.expander("📝 Ghi nhận công việc mới", expanded=True):
    with st.form("task_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("👤 Tên người thực hiện")
            department = st.text_input("🏢 Phòng ban")
            project = st.selectbox("📁 Dự án", ["Dự án 43DTM", "Dự án VVIP", "Dự án GALERY"])
        with col2:
            task_type = st.selectbox("🧱 Công việc", ["Thiết kế", "Mua sắm", "Gia công", "Vận chuyển", "Lắp dựng"])
            task_group = st.selectbox("📂 Hạng mục", ["Hạng mục A", "Hạng mục B", "Hạng mục C"])
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
                "task_group": task_group,
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

    with st.expander("📊 Danh sách công việc đã ghi nhận", expanded=True):
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        if st.button("💾 Lưu thay đổi"):
            tasks = edited_df.to_dict(orient="records")
            save_tasks(DATA_FILE, tasks)
            st.success("✅ Dữ liệu đã được cập nhật!")
            st.rerun()

    # Biểu đồ trạng thái
    with st.expander("📈 Thống kê công việc theo trạng thái"):
        status_chart = df["status"].value_counts().reset_index()
        status_chart.columns = ["Trạng thái", "Số lượng"]
        fig = px.pie(status_chart, names="Trạng thái", values="Số lượng", title="Tỷ lệ trạng thái công việc", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    # Biểu đồ công việc (task_type)
    with st.expander("📈 Thống kê theo loại công việc"):
        type_chart = df["task_type"].value_counts().reset_index()
        type_chart.columns = ["Công việc", "Số lượng"]
        fig_type = px.pie(type_chart, names="Công việc", values="Số lượng", title="Tỷ lệ loại công việc", hole=0.3)
        st.plotly_chart(fig_type, use_container_width=True)

    # Biểu đồ hạng mục (task_group)
    with st.expander("📈 Thống kê theo hạng mục"):
        group_chart = df["task_group"].value_counts().reset_index()
        group_chart.columns = ["Hạng mục", "Số lượng"]
        fig_group = px.pie(group_chart, names="Hạng mục", values="Số lượng", title="Tỷ lệ hạng mục công việc", hole=0.3)
        st.plotly_chart(fig_group, use_container_width=True)

    # Biểu đồ công việc theo từng dự án
    with st.expander("📈 Biểu đồ công việc theo từng dự án"):
        for proj in df["project"].unique():
            proj_df = df[df["project"] == proj]
            if not proj_df.empty:
                chart = proj_df["task_type"].value_counts().reset_index()
                chart.columns = ["Công việc", "Số lượng"]
                fig_proj = px.pie(chart, names="Công việc", values="Số lượng", title=f"{proj}", hole=0.3)
                st.plotly_chart(fig_proj, use_container_width=True)

    # Tải xuống dữ liệu
    with st.expander("📥 Tải xuống dữ liệu"):
        excel_data = to_excel(df)
        st.download_button(
            label="📥 Tải xuống danh sách công việc (Excel)",
            data=excel_data,
            file_name="tasks.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("📭 Chưa có công việc nào được ghi nhận.")



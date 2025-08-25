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

    status_count = df["status"].value_counts()
    fig_status = px.pie(names=status_count.index, values=status_count.values, title="Tỷ lệ trạng thái công việc")
    st.plotly_chart(fig_status, use_container_width=True)

    fig_date = px.bar(df["date"].value_counts().sort_index(), title="Số lượng công việc theo ngày")
    st.plotly_chart(fig_date, use_container_width=True)

    fig_cat = px.bar(df["category"].value_counts(), orientation="h", title="Số lượng công việc theo hạng mục")
    st.plotly_chart(fig_cat, use_container_width=True)

    st.markdown("### 🔔 Nhắc nhở công việc chờ duyệt")
    df["date_obj"] = pd.to_datetime(df["date"])
    overdue = df[(df["status"] == "Chờ duyệt") & (df["date_obj"] < datetime.today() - timedelta(days=3))]
    if not overdue.empty:
        st.warning(f"⚠️ Có {len(overdue)} công việc chờ duyệt quá 3 ngày!")
        st.dataframe(overdue.drop(columns=["date_obj"]))
    else:
        st.success("✅ Không có công việc chờ duyệt quá hạn.")

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

    # --- Quản lý công việc ---
    st.markdown("## 🗂️ Quản lý công việc")

    for i, task in enumerate(tasks):
        task_display = f"{task['date']} - {task['name']} - {task['task'][:40]}"
        if task["status"].lower() in ["ngưng chờ", "bỏ"]:
            task_display = f"~~{task_display}~~"

        with st.expander(task_display):
            st.write(f"**Phòng ban:** {task['department']}")
            st.write(f"**Dự án:** {task['project']}")
            st.write(f"**Hạng mục:** {task['category']}")
            st.write(f"**Nội dung:** {task['task']}")
            st.write(f"**Ghi chú:** {task['note']}")
            st.write(f"**Thời gian:** {task['date']} {task['time']} | Lặp: {task['repeat']} lần")
            st.write(f"**Trạng thái:** {task['status']}")

            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button(f"❌ Xóa", key=f"delete_{i}"):
                    tasks.pop(i)
                    with open(DATA_FILE, "w", encoding="utf-8") as f:
                        json.dump(tasks, f, ensure_ascii=False, indent=2)
                    st.success("🗑️ Công việc đã được xóa. Vui lòng tải lại trang.")
                    st.experimental_rerun()
            with col2:
                if st.button(f"✏️ Sửa", key=f"edit_{i}"):
                    st.session_state["edit_index"] = i

    # --- Chỉnh sửa công việc ---
    if "edit_index" in st.session_state:
        edit_index = st.session_state["edit_index"]
        selected_task = tasks[edit_index]

        st.markdown("### ✏️ Cập nhật công việc đã chọn")
        with st.form("edit_task_inline"):
            name_edit = st.text_input("Tên người thực hiện", value=selected_task["name"])
            department_edit = st.text_input("Phòng ban", value=selected_task["department"])
            project_edit = st.selectbox("Dự án", options=["Dự án 43DTM", "Dự án VVIP", "Dự án GALERY"], index=["Dự án 43DTM", "Dự án VVIP", "Dự án GALERY"].index(selected_task["project"]))
            category_edit = st.selectbox("Hạng mục", options=["Thiết kế", "Mua sắm", "Gia công", "Vận chuyển", "Lắp dựng"], index=["Thiết kế", "Mua sắm", "Gia công", "Vận chuyển", "Lắp dựng"].index(selected_task["category"]))
            task_edit = st.text_area("Nội dung công việc", value=selected_task["task"])
            note_edit = st.text_area("Ghi chú", value=selected_task["note"])
            date_edit = st.date_input("Ngày thực hiện", value=datetime.strptime(selected_task["date"], "%Y-%m-%d"))
            time_edit = st.time_input("Thời gian bắt đầu", value=datetime.strptime(selected_task["time"], "%H:%M").time())
            repeat_edit = st.number_input("Số lần thực hiện", min_value=1, step=1, value=selected_task["repeat"])

            status_options = ["Hoàn thành", "Đang thực hiện", "Chờ duyệt", "Ngưng chờ", "Bỏ"]
            status_index = status_options.index(selected_task["status"]) if selected_task["status"] in

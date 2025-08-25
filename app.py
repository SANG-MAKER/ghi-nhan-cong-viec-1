import streamlit as st
import json
from datetime import datetime

DATA_FILE = "tasks.json"

# --- Load dữ liệu ---
def load_tasks():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

tasks = load_tasks()

# --- Giao diện chính ---
st.set_page_config(page_title="📋 Ghi nhận công việc", layout="wide")
st.title("📋 Ghi nhận công việc")

# --- Thêm công việc mới ---
st.markdown("### ➕ Thêm công việc mới")
with st.form("add_task"):
    name = st.text_input("Tên người thực hiện")
    department = st.text_input("Phòng ban")
    project = st.selectbox("Dự án", ["Dự án 43DTM", "Dự án VVIP", "Dự án GALERY"])
    category = st.selectbox("Hạng mục", ["Thiết kế", "Mua sắm", "Gia công", "Vận chuyển", "Lắp dựng"])
    task = st.text_area("Nội dung công việc")
    note = st.text_area("Ghi chú")
    date = st.date_input("Ngày thực hiện", value=datetime.today())
    time = st.time_input("Thời gian bắt đầu", value=datetime.now().time())
    repeat = st.number_input("Số lần thực hiện", min_value=1, step=1, value=1)
    status = st.radio("Trạng thái", ["Hoàn thành", "Đang thực hiện", "Chờ duyệt", "Ngưng chờ", "Bỏ"])
    submit_btn = st.form_submit_button("✅ Ghi nhận")

    if submit_btn:
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
        st.success("✅ Công việc đã được ghi nhận!")

# --- Hiển thị danh sách công việc ---
st.markdown("### 📑 Danh sách công việc")
for i, t in enumerate(tasks):
    with st.expander(f"{t['date']} - {t['name']} ({t['project']})"):
        st.write(f"**Phòng ban:** {t['department']}")
        st.write(f"**Hạng mục:** {t['category']}")
        st.write(f"**Nội dung:** {t['task']}")
        st.write(f"**Ghi chú:** {t['note']}")
        st.write(f"**Thời gian:** {t['time']}")
        st.write(f"**Số lần thực hiện:** {t['repeat']}")
        st.write(f"**Trạng thái:** {t['status']}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ Sửa", key=f"edit_{i}"):
                st.session_state["edit_index"] = i
                st.experimental_rerun()
        with col2:
            if st.button("🗑️ Xóa", key=f"delete_{i}"):
                tasks.pop(i)
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(tasks, f, ensure_ascii=False, indent=2)
                st.success("🗑️ Đã xóa công việc.")
                st.experimental_rerun()

# --- Chỉnh sửa công việc ---
if "edit_index" in st.session_state:
    edit_index = st.session_state["edit_index"]
    selected_task = tasks[edit_index]

    st.markdown("### ✏️ Cập nhật công việc đã chọn")
    with st.form("edit_task_inline"):
        name_edit = st.text_input("Tên người thực hiện", value=selected_task["name"])
        department_edit = st.text_input("Phòng ban", value=selected_task["department"])
        project_edit = st.selectbox("Dự án", ["Dự án 43DTM", "Dự án VVIP", "Dự án GALERY"],
                                    index=["Dự án 43DTM", "Dự án VVIP", "Dự án GALERY"].index(selected_task["project"]))
        category_edit = st.selectbox("Hạng mục", ["Thiết kế", "Mua sắm", "Gia công", "Vận chuyển", "Lắp dựng"],
                                     index=["Thiết kế", "Mua sắm", "Gia công", "Vận chuyển", "Lắp dựng"].index(selected_task["category"]))
        task_edit = st.text_area("Nội dung công việc", value=selected_task["task"])
        note_edit = st.text_area("Ghi chú", value=selected_task["note"])
        date_edit = st.date_input("Ngày thực hiện", value=datetime.strptime(selected_task["date"], "%Y-%m-%d"))
        time_edit = st.time_input("Thời gian bắt đầu", value=datetime.strptime(selected_task["time"], "%H:%M").time())
        repeat_edit = st.number_input("Số lần thực hiện", min_value=1, step=1, value=selected_task["repeat"])
        status_options = ["Hoàn thành", "Đang thực hiện", "Chờ duyệt", "Ngưng chờ", "Bỏ"]
        status_index = status_options.index(selected_task["status"]) if selected_task["status"] in status_options else 0
        status_edit = st.radio("Trạng thái", options=status_options, index=status_index)

        update_btn = st.form_submit_button("💾 Cập nhật")

        if update_btn:
            tasks[edit_index] = {
                "name": name_edit.strip(),
                "department": department_edit.strip(),
                "project": project_edit,
                "category": category_edit,
                "task": task_edit.strip(),
                "note": note_edit.strip(),
                "date": str(date_edit),
                "time": time_edit.strftime("%H:%M"),
                "repeat": repeat_edit,
                "status": status_edit
            }
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(tasks, f, ensure_ascii=False, indent=2)
            st.success("✅ Công việc đã được cập nhật!")
            del st.session_state["edit_index"]
            st.experimental_rerun()


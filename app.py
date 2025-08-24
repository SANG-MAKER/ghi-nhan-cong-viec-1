import streamlit as st
import json
import os

# Cấu hình giao diện
st.set_page_config(page_title="Ghi nhận công việc", layout="centered")

st.title("📋 Ghi nhận công việc")
st.write("Nhập thông tin công việc bạn đã hoàn thành:")

# Tạo file nếu chưa tồn tại
if not os.path.exists("tasks.json"):
    with open("tasks.json", "w", encoding="utf-8") as f:
        json.dump([], f)

# Đọc dữ liệu từ file
try:
    with open("tasks.json", "r", encoding="utf-8") as f:
        tasks = json.load(f)
    if not isinstance(tasks, list):
        tasks = []
except Exception as e:
    st.error(f"Lỗi khi đọc file dữ liệu: {e}")
    tasks = []

# Form nhập dữ liệu
with st.form("task_form"):
    task_name = st.text_input("Tên công việc")
    task_date = st.date_input("Ngày thực hiện")
    task_note = st.text_area("Ghi chú")
    submitted = st.form_submit_button("Lưu")

# Xử lý khi nhấn nút Lưu
if submitted:
    if not task_name.strip():
        st.warning("⚠️ Vui lòng nhập tên công việc.")
    else:
        new_task = {
            "name": task_name.strip(),
            "date": str(task_date),
            "note": task_note.strip()
        }

        tasks.append(new_task)

        try:
            with open("tasks.json", "w", encoding="utf-8") as f:
                json.dump(tasks, f, ensure_ascii=False, indent=2)
            st.success("✅ Công việc đã được lưu!")
        except Exception as e:
            st.error(f"Lỗi khi lưu dữ liệu: {e}")

# Hiển thị danh sách công việc
if tasks:
    st.subheader("📌 Danh sách công việc đã ghi nhận")
    for i, task in enumerate(tasks[::-1], 1):
        st.markdown(f"**{i}. {task['name']}** ({task['date']})  \n*{task['note']}*")
else:
    st.info("📭 Chưa có công việc nào được ghi nhận.")



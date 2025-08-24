import streamlit as st
import json
import os

st.set_page_config(page_title="Ghi nhận công việc", layout="centered")

st.title("📋 Ghi nhận công việc")
st.write("Nhập thông tin công việc bạn đã hoàn thành:")

# Form nhập dữ liệu
with st.form("task_form"):
    task_name = st.text_input("Tên công việc")
    task_date = st.date_input("Ngày thực hiện")
    task_note = st.text_area("Ghi chú")
    submitted = st.form_submit_button("Lưu")

# Lưu dữ liệu vào file JSON
if submitted:
    new_task = {
        "name": task_name,
        "date": str(task_date),
        "note": task_note
    }

    if os.path.exists("tasks.json"):
        with open("tasks.json", "r", encoding="utf-8") as f:
            tasks = json.load(f)
    else:
        tasks = []

    tasks.append(new_task)

    with open("tasks.json", "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

    st.success("✅ Công việc đã được lưu!")

# Hiển thị danh sách công việc
if os.path.exists("tasks.json"):
    st.subheader("📌 Danh sách công việc đã ghi nhận")
    with open("tasks.json", "r", encoding="utf-8") as f:
        tasks = json.load(f)
        for i, task in enumerate(tasks[::-1], 1):
            st.markdown(f"**{i}. {task['name']}** ({task['date']})  \n*{task['note']}*")


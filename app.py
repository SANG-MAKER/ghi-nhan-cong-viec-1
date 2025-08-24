import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import streamlit_authenticator as stauth

# --- Đăng nhập ---
names = ["Sang"]
usernames = ["sang"]
passwords = ["123456"]  # Đổi thành mật khẩu mạnh hơn nếu triển khai thực tế
hashed_pw = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(names, usernames, hashed_pw, "ghi_nhan_app", "abcdef", cookie_expiry_days=30)
name, auth_status, username = authenticator.login("Đăng nhập", "main")

if auth_status == False:
    st.error("Sai thông tin đăng nhập")
elif auth_status == None:
    st.warning("Vui lòng nhập thông tin")
elif auth_status:
    authenticator.logout("Đăng xuất", "sidebar")
    st.sidebar.success(f"Xin chào {name} 👋")

    # --- Load và lưu dữ liệu ---
    DATA_FILE = "tasks.json"

    def load_tasks():
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_tasks(tasks):
        with open(DATA_FILE, "w") as f:
            json.dump(tasks, f, indent=4)

    st.title("📝 Ghi nhận công việc mỗi ngày")

    # --- Ghi nhận công việc ---
    with st.form("task_form"):
        desc = st.text_input("📌 Mô tả công việc")
        category = st.selectbox("📂 Phân loại", ["Công việc", "Cá nhân", "Học tập", "Khác"])
        submitted = st.form_submit_button("✅ Ghi nhận")

        if submitted and desc:
            tasks = load_tasks()
            date = datetime.now().strftime("%Y-%m-%d")
            time = datetime.now().strftime("%H:%M:%S")
            if date not in tasks:
                tasks[date] = []
            tasks[date].append({
                "time": time,
                "description": desc,
                "category": category,
                "user": username
            })
            save_tasks(tasks)
            st.success(f"Đã ghi nhận: {desc} lúc {time}")

    # --- Hiển thị công việc hôm nay ---
    st.subheader("📅 Danh sách công việc hôm nay")
    tasks = load_tasks()
    today = datetime.now().strftime("%Y-%m-%d")
    if today in tasks:
        for i, task in enumerate(tasks[today], 1):
            if task["user"] == username:
                st.markdown(f"- **{i}.** ⏰ *{task['time']}* — {task['description']} _(Loại: {task['category']})_")
    else:
        st.info("Chưa có công việc nào được ghi nhận hôm nay.")

    # --- Báo cáo tuần ---
    st.subheader("📈 Báo cáo tuần")
    week_dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
    report = []

    for date in week_dates:
        if date in tasks:
            for task in tasks[date]:
                if task["user"] == username:
                    report.append({
                        "Ngày": date,
                        "Giờ": task["time"],
                        "Mô tả": task["description"],
                        "Phân loại": task["category"]
                    })

    if report:
        df = pd.DataFrame(report)
        st.dataframe(df)

        # --- Biểu đồ ---
        st.subheader("📊 Biểu đồ số lượng công việc theo ngày")
        count_by_day = df["Ngày"].value_counts().sort_index()
        fig, ax = plt.subplots()
        count_by_day.plot(kind="bar", ax=ax, color="skyblue")
        ax.set_ylabel("Số công việc")
        ax.set_xlabel("Ngày")
        ax.set_title("Thống kê công việc trong tuần")
        st.pyplot(fig)
    else:
        st.info("Không có dữ liệu tuần này.")

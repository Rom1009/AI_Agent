import time
import requests
import streamlit as st


API_URL = "http://localhost:8000/api/ai"

st.set_page_config(page_title="Level 4 Celery Pipeline", page_icon="⚙️")

st.title("⚙️ Level 4 - Celery AI Pipeline")

st.write(
    """
    Flow:
    Streamlit -> FastAPI -> Celery Task -> Redis Broker -> Celery Worker -> Redis Result Backend
    """
)

text = st.text_input("Enter text to process:")

if st.button("Submit Task"):
    if not text.strip():
        st.warning("Please enter some text.")
    else:
        response = requests.post(
            f"{API_URL}/submit",
            json={"text": text},
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            st.session_state["task_id"] = data["task_id"]
            st.success(f"Task submitted: {data['task_id']}")
        else:
            st.error(f"API error: {response.text}")


if "task_id" in st.session_state:
    task_id = st.session_state["task_id"]

    st.divider()
    st.write("Current task ID:")
    st.code(task_id)

    if st.button("Check Result"):
        response = requests.get(
            f"{API_URL}/result/{task_id}",
            timeout=10,
        )

        data = response.json()

        st.write("Status:", data.get("status"))

        if data.get("status") == "SUCCESS":
            st.success(data.get("result"))

        elif data.get("status") == "FAILURE":
            st.error(data.get("error"))

        elif data.get("status") == "RETRY":
            st.warning("Task is retrying...")

        else:
            st.info("Task is still running or waiting...")

    if st.button("Auto Poll Until Finished"):
        placeholder = st.empty()

        while True:
            response = requests.get(
                f"{API_URL}/result/{task_id}",
                timeout=10,
            )

            data = response.json()
            status = data.get("status")

            placeholder.write(f"Status: {status}")

            if status == "SUCCESS":
                st.success(data.get("result"))
                break

            if status == "FAILURE":
                st.error(data.get("error"))
                break

            time.sleep(2)
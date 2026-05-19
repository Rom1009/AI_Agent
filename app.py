import time
import requests
import streamlit as st


API_URL = "http://localhost:8000/api/ai"

st.set_page_config(page_title="Level 5 Reliable Pipeline", page_icon="🛡️")

st.title("🛡️ Level 5 - Reliable Celery AI Pipeline")

st.write(
    """
    Flow:
    Streamlit -> FastAPI -> Celery -> Redis -> Worker -> Result/DLQ/History
    """
)

st.info(
    """
    Try inputs:
    - `hello mlops` -> success
    - `bad` -> permanent failure
    - `unstable` -> transient error with retry
    - `timeout` -> timeout failure
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


st.divider()

col1, col2 = st.columns(2)

with col1:
    if st.button("Show Job History"):
        response = requests.get(f"{API_URL}/history?limit=20", timeout=10)
        data = response.json()
        st.write(data["items"])

with col2:
    if st.button("Show DLQ"):
        response = requests.get(f"{API_URL}/dlq?limit=20", timeout=10)
        data = response.json()
        st.write(data["items"])
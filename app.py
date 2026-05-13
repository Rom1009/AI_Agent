import streamlit as st
import requests
import time


API_URL = "http://localhost:8000/api/ai"

st.set_page_config(page_title="Level 3 Redis Queue", page_icon="🚀")

st.title("Level 3 - Redis Queue AI Pipeline")

st.write(
    """
    Flow:
    Streamlit -> FastAPI -> Redis Queue -> Worker -> Result
    """
)

text = st.text_input("Enter text to process:")

if st.button("Submit Job"):
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
            st.session_state["job_id"] = data["job_id"]
            st.success(f"Job submitted: {data['job_id']}")
        else:
            st.error(f"API error: {response.text}")


if "job_id" in st.session_state:
    job_id = st.session_state["job_id"]

    st.divider()
    st.write("Current job ID:")
    st.code(job_id)

    if st.button("Check Result"):
        response = requests.get(
            f"{API_URL}/result/{job_id}",
            timeout=10,
        )


        data = response.json()

        print(data)
        st.write("Status:", data.get("status"))

        if data.get("status") == "DONE":
            st.success(data.get("result"))
        elif data.get("status") == "FAILED":
            st.error(data.get("error"))
        elif data.get("status") == "NOT_FOUND":
            st.error("Job not found")
        else:
            st.warning("Still processing...")

    if st.button("Auto Poll Until Done"):
        placeholder = st.empty()

        while True:
            response = requests.get(
                f"{API_URL}/result/{job_id}",
                timeout=10,
            )

            data = response.json()
            status = data.get("status")

            placeholder.write(f"Status: {status}")

            if status == "DONE":
                st.success(data.get("result"))
                break

            if status == "FAILED":
                st.error(data.get("error"))
                break

            if status == "NOT_FOUND":
                st.error("Job not found")
                break

            time.sleep(2)


st.divider()

if st.button("Check Queue Size"):
    response = requests.get(f"{API_URL}/queue_size", timeout=10)
    data = response.json()
    st.write("Queue size:", data["size"])
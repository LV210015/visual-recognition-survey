import streamlit as st
import time
import random
import pandas as pd
import requests
from datetime import datetime

WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbxr9VbH4_pjofYGmTNREOsFYo9J6BEXSFAd5-zkdYVFDHAp-ozKaSuTlb5jEbvt-lvJOg/exec"

# Define your 6 text-based conditions for testing (no images)
treatments = [
    {"Color": "Single", "Distortion": "None", "Label": "Single Color, No Distortion"},
    {"Color": "Single", "Distortion": "Simple", "Label": "Single Color, Simple Distortion"},
    {"Color": "Single", "Distortion": "Complex", "Label": "Single Color, Complex Distortion"},
    {"Color": "Mixed", "Distortion": "None", "Label": "Mixed Color, No Distortion"},
    {"Color": "Mixed", "Distortion": "Simple", "Label": "Mixed Color, Simple Distortion"},
    {"Color": "Mixed", "Distortion": "Complex", "Label": "Mixed Color, Complex Distortion"},
]

st.title("🎯 Visual Recognition Experiment (Text Only Test Mode)")

# Create session state to hold timing, trials, and results
if "trial_index" not in st.session_state:
    st.session_state.trial_index = 0
    st.session_state.trials = random.sample(treatments * 2, 12)  # 12 randomized trials
    st.session_state.start_time = None
    st.session_state.results = []

# Run trials
if st.session_state.trial_index < len(st.session_state.trials):
    trial = st.session_state.trials[st.session_state.trial_index]
    st.subheader(f"Trial {st.session_state.trial_index + 1}")
    st.markdown(f"**Condition:** {trial['Label']}")

    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()

    if st.button("I recognized it"):
        st.session_state.response_time = time.time() - st.session_state.start_time
        st.session_state.show_input = True

    if "response_time" in st.session_state and st.session_state.get("show_input"):
        answer = st.text_input("What was the number you saw?")
        if st.button("Submit"):
            if answer.strip() == "4675":
                st.success("Correct! Trial saved.")
                result = {
                    "Trial": st.session_state.trial_index + 1,
                    "Color": trial["Color"],
                    "Distortion": trial["Distortion"],
                    "Time_sec": round(st.session_state.response_time, 3),
                    "Answer": answer,
                    "Timestamp": datetime.now().isoformat()
                }
                st.session_state.results.append(result)

                # Send to Google Sheet
                try:
                    requests.post(WEBHOOK_URL, json=result)
                except Exception as e:
                    st.warning(f"Failed to upload to Google Sheet: {e}")
            else:
                st.error("Incorrect. Trial not saved.")

            # Move to next trial
            st.session_state.trial_index += 1
            st.session_state.start_time = None
            st.session_state.show_input = False
            st.rerun()

else:
    st.header("✅ Experiment Completed")
    df = pd.DataFrame(st.session_state.results)
    st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Results as CSV", csv, "results.csv", "text/csv")
    
    

    
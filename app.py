import streamlit as st
import time
import random
import pandas as pd
import requests
from datetime import datetime
from collections import OrderedDict

WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbx2aIPevVrrqiliUMJCXFXIc4Xaz8o3_0s_2qCZzwvR8fxxqS7MUomqyF40LxarLruBgA/exec"

# Define all image groups (6 per treatment)
image_groups = {
    ("Single", "None"): [f"SCND{i}.jpg" for i in range(1, 7)],
    ("Single", "Simple"): [f"SCSD{i}.jpg" for i in range(1, 7)],
    ("Single", "Complex"): [f"SCCD{i}.jpg" for i in range(1, 7)],
    ("Mixed", "None"): [f"MCND{i}.jpg" for i in range(1, 7)],
    ("Mixed", "Simple"): [f"MCSD{i}.jpg" for i in range(1, 7)],
    ("Mixed", "Complex"): [f"MCCD{i}.jpg" for i in range(1, 7)],
}

instructions = (
    "1. You’ll see 12 images of verification codes — just recognize and type what you see.\n\n"
    "2. For each image, click the 'I Recognized It!' button before entering your answer.\n\n"
    "3. There will NOT be codes like '0' (zero) or 'O' (letter O), so don’t worry about confusing characters.\n\n"
    "4. Just relax, type naturally, and have fun with it — it’s not a test!"
)

st.title("Visual Recognition Experiment")

# --- Start Page ---
if "username" not in st.session_state:
    st.session_state.username = None

if st.session_state.username is None:
    name_input = st.text_input("Enter a nickname to begin:")
    if st.button("Start"):
        if name_input.strip() != "":
            st.session_state.username = name_input.strip()
            st.rerun()
        else:
            st.warning("Please enter a valid nickname.")
    st.stop()

# --- Instructions ---
if "show_instructions" not in st.session_state:
    st.session_state.show_instructions = True

if st.session_state.show_instructions:
    st.subheader("Instructions")
    st.markdown(instructions)
    if st.button("I'm ready! Start the experiment"):
        st.session_state.show_instructions = False
        st.rerun()
    st.stop()

# --- Prepare trials (once only) ---
if "trial_index" not in st.session_state:
    trials = []
    for (color, distortion), images in image_groups.items():
        selected_imgs = random.sample(images, 2)  # pick 2 unique images per group
        for img in selected_imgs:
            trials.append({
                "Color": color,
                "Distortion": distortion,
                "Image": img
            })
    random.shuffle(trials)  # ✅ full random shuffle
    st.session_state.trials = trials
    st.session_state.trial_index = 0
    st.session_state.start_time = None
    st.session_state.results = []

# --- Run trials ---
if st.session_state.trial_index < len(st.session_state.trials):
    trial = st.session_state.trials[st.session_state.trial_index]
    st.subheader(f"Trial {st.session_state.trial_index + 1}")
    st.markdown(f"**Condition:** {trial['Color']} Color + {trial['Distortion']} Distortion")
    st.image(trial["Image"], use_column_width=True)

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
                result = OrderedDict([
                    ("Username", st.session_state.username),
                    ("Trial", st.session_state.trial_index + 1),
                    ("Color", trial["Color"]),
                    ("Distortion", trial["Distortion"]),
                    ("Time_sec", round(st.session_state.response_time, 3)),
                    ("Answer", answer),
                    ("Timestamp", datetime.now().isoformat())
                ])
                st.session_state.results.append(result)

                try:
                    requests.post(WEBHOOK_URL, json=result)
                except Exception as e:
                    st.warning(f"Failed to upload to Google Sheet: {e}")
            else:
                st.error("Incorrect. Trial not saved.")

            st.session_state.trial_index += 1
            st.session_state.start_time = None
            st.session_state.show_input = False
            st.rerun()
else:
    st.header("Experiment Completed")
    df = pd.DataFrame(st.session_state.results)
    st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Results as CSV", csv, "results.csv", "text/csv")

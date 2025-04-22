import streamlit as st
from PIL import Image
import base64
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

if 'history' not in st.session_state:
    st.session_state.history = []

st.title("Wall Issue Detector and Paint Recommendation System")
st.write("Upload or capture up to 3 photos of your wall, and we'll analyze them for issues and suggest treatments.")

st.sidebar.header("Upload History")
if st.session_state.history:
    for idx, (img_bytes_list, result) in enumerate(reversed(st.session_state.history), 1):
        for img_idx, img_bytes in enumerate(img_bytes_list):
            st.sidebar.image(img_bytes, caption=f"Upload #{len(st.session_state.history) - idx + 1}, Image {img_idx + 1}", use_container_width=True)
        with st.sidebar.expander("View Analysis"):
            st.markdown(result)
else:
    st.sidebar.info("No uploads yet.")

input_method = st.radio("Choose input method:", ("Upload Images", "Use Camera (one at a time)"))

uploaded_files = []

if input_method == "Upload Images":
    uploaded_files = st.file_uploader("Upload up to 3 photos of your wall", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    uploaded_files = uploaded_files[:3]  
else:
    camera_img = st.camera_input("Take a photo of your wall")
    if camera_img:
        uploaded_files = [camera_img]  

def encode_image_to_data_url(image_file):
    image_bytes = image_file.read()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    mime_type = Image.open(image_file).get_format_mimetype()
    return f"data:{mime_type};base64,{base64_image}", image_bytes


def analyze_wall_images(image_files):
    prompt = '''
    You are an expert in wall surface inspection for painting. Analyze up to 3 attached images of a wall for visible painting-related surface defects.

Objective:
Deliver an accurate, image-based assessment of visible wall surface defects. Clearly identify any actual defects, provide likely root causes if visibly evident, and recommend appropriate surface preparation and painting products. Your analysis must be strictly grounded in what is observable in the images.

Instructions:

Base your assessment only on what is clearly visible in the images.

Do not speculate or list possible defects, causes, or treatments that are not visibly present.

If a wall image appears to be in good condition with no visible defects, clearly state that no issues are observed.

Only label a surface as “uneven” or cite any other defect if it is visibly clear and unambiguous in the image.

Do not ask follow-up questions or request clarification.

Output Format:

Defect Classification

List and describe only the visible defects (e.g., cracks, peeling, mold, efflorescence, etc.).

If no visible defects are present, state: “No visible painting-related defects observed in the image(s).”

Root Cause Insight

For each visible defect, explain the most likely cause based solely on the image evidence.

If the cause is not visually identifiable, respond with: “Root cause not clearly identifiable from the image.”

Actionable Recommendations

Provide steps for surface preparation only if defects are present.

Recommend appropriate types of products (e.g., primers, putty, waterproofing) relevant to the identified defects.

Suggest paint types suited to the observed surface condition.

If no defects are present, state: “No surface preparation or special products required. Standard paint application is suitable.”

    '''.strip().replace('  ', '')
    contents = [
        {"type": "input_text", "text": prompt}
    ]
    image_bytes_list = []

    for file in image_files:
        data_url, img_bytes = encode_image_to_data_url(file)
        contents.append({"type": "input_image", "image_url": data_url})
        image_bytes_list.append(img_bytes)

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[{"role": "user", "content": contents}]
    )
    return response.output_text, image_bytes_list

if uploaded_files:
    for file in uploaded_files:
        st.image(file, caption="Wall Photo", use_container_width=True)

    with st.spinner("Analyzing the wall images using AI..."):
        analysis_result, image_bytes_list = analyze_wall_images(uploaded_files)

    st.subheader("AI Analysis and Recommendations")
    st.write(analysis_result)

    st.session_state.history.append((image_bytes_list, analysis_result))
else:
    st.info("Please upload or capture up to 3 wall photos to begin analysis.")
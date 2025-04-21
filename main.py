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
    Please analyze the attached up to 3 images of a wall surface for potential painting-related defects.

    Objective:
    To receive a precise, AI-based assessment of visible surface defects, understand possible root causes, and get recommendations for surface preparation and painting products.

    Required Output:

    Defect Classification

    List and describe visible defects (e.g., moisture, cracks, peeling, efflorescence, mold, chalking, surface contamination, uneven surface).

    Root Cause Insight

    Explain the likely underlying cause for each defect.

    Actionable Recommendations

    Steps for surface preparation before painting.

    Suggest relevant product types (e.g., primers, waterproofing, putty, etc.).

    Suggest suitable paint products for the wall surface, considering the identified defects and root causes.

    Dont ask any follow up questions

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
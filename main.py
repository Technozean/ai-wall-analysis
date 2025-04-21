import streamlit as st
from PIL import Image
import base64
import requests
from openai import OpenAI

# Initialize OpenAI client

api_key = "sk-proj-MNRqIY5wF8Hf04YkKhj1T3BlbkFJWYNORdBqRHpZGS2NgZwF"
client = OpenAI(api_key=api_key)

# Initialize session state for history
if 'history' not in st.session_state:
    st.session_state.history = []

# Title
st.title("Wall Issue Detector and Paint Recommendation System")
st.write("Upload a photo of your wall, and we'll analyze it for issues and suggest treatments.")

# Sidebar for history
st.sidebar.header("Upload History")
if st.session_state.history:
    for idx, (img_bytes, result) in enumerate(reversed(st.session_state.history), 1):
        st.sidebar.image(img_bytes, caption=f"Previous Upload #{len(st.session_state.history) - idx + 1}", use_container_width=True)
        with st.sidebar.expander("View Analysis"):
            st.markdown(result)
else:
    st.sidebar.info("No uploads yet.")

# Image upload
uploaded_file = st.file_uploader("Upload a photo of your wall", type=["jpg", "jpeg", "png"])

# Function to convert image to base64 and generate data URL
def encode_image_to_data_url(image_file):
    image_bytes = image_file.read()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    mime_type = Image.open(image_file).get_format_mimetype()
    return f"data:{mime_type};base64,{base64_image}", image_bytes

# Function to analyze image using OpenAI GPT-4 vision model
def analyze_wall_image(data_url):
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Analyze this wall image. Identify visible issues like cracks, dampness, or peeling paint. Provide the possible cause and recommended treatment and paint options."},
                {"type": "input_image", "image_url": data_url}
            ]
        }],
    )
    return response.output_text

# Display the uploaded image and perform analysis
if uploaded_file is not None:
    data_url, raw_image_bytes = encode_image_to_data_url(uploaded_file)

    st.image(raw_image_bytes, caption="Uploaded Wall Photo", use_container_width=True)

    with st.spinner("Analyzing the wall image using AI..."):
        analysis_result = analyze_wall_image(data_url)

    st.subheader("AI Analysis and Recommendations")
    st.write(analysis_result)

    # Save to session state history
    st.session_state.history.append((raw_image_bytes, analysis_result))
else:
    st.info("Please upload a wall photo to begin analysis.")
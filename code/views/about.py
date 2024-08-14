import streamlit as st

# Custom CSS for styling
st.markdown(
    """
    <style>
    .about-container {
        background-color: #f4f4f9;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        font-family: 'Arial', sans-serif;
        max-width: 800px;
        margin: auto;
    }
    .about-title {
        color: #333;
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-align: center;
    }
    .about-description {
        color: #555;
        font-size: 1.1rem;
        line-height: 1.6;
        text-align: justify;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# About Page Content
st.markdown(
    """
    <div class="about-container">
        <div class="about-title">About Our Project</div>
        <div class="about-description">
            Welcome to our Fine-Tuning GenAI Project! This website is dedicated to the art of moodboard creation through the power of generative AI. Here, we explore the intersection of creativity and technology by fine-tuning AI models to generate moodboards based on specific prompts. 
            Whether you're a fashion enthusiast, a designer, or simply someone who appreciates visual storytelling, our platform offers a unique space to discover and explore a wide range of moodboards. 
            Each moodboard is carefully crafted by our AI, reflecting the essence of the prompt it was generated from. Dive in and experience the fusion of innovation and artistry!
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

import streamlit as st
import os
from PIL import Image
import pandas as pd
from sqlalchemy import create_engine, text
from google.cloud import storage
from io import BytesIO
import json
import tempfile

# Title of the page
st.title("Fine-tuning GenAI Project")

# Load GCS credentials from secrets
gcs_credentials = json.loads(st.secrets["database"]["credentials"])

# Save credentials to a temporary file
with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json') as temp_file:
    json.dump(gcs_credentials, temp_file)
    temp_file_path = temp_file.name
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file_path

# Initialize Google Cloud Storage client
client = storage.Client()

# Specify your bucket name and get the bucket
bucket_name = 'open-to-public-rw-sairam'
bucket = client.get_bucket(bucket_name)

# Database connection using SQLAlchemy
engine = create_engine("postgresql://finetune:genai#2024@finetune-ai.postgres.database.azure.com/Fintune")

# Inputs for the range of images to display
start_range = st.number_input("Images FROM:", min_value=1, value=1)
end_range = st.number_input("TO:", min_value=1, value=10)

# Add an "Apply" button
if st.button("Apply"):
    # Folder containing the images
    image_folder = "Prompts/Final images moodboard/"

    # Function to fetch prompts from PostgreSQL based on image number
    def get_prompts(image_number):
        query = f"""
        SELECT serial_nos, sno, image_prompts, prompt_feedback
        FROM prompts
        WHERE sno = {image_number}
        ORDER BY serial_nos;
        """
        prompts_df = pd.read_sql(query, engine)
        return prompts_df

    # Function to update the edited prompt and feedback in the database
    def update_prompt(serial_nos, new_prompt, feedback):
        try:
            serial_nos = int(serial_nos)
            update_query = text("""
            UPDATE prompts
            SET image_prompts = :new_prompt, prompt_feedback = :feedback
            WHERE serial_nos = :serial_nos
            """)
            with engine.connect() as conn:
                conn.execute(update_query, {"new_prompt": new_prompt, "feedback": feedback, "serial_nos": serial_nos})
                conn.commit()
            st.success("Prompt updated successfully!")
        except Exception as e:
            st.error(f"Failed to update prompt: {e}")

    # Function to update the image review in the database
    def update_image_review(image_name, review):
        try:
            update_query = text("""
            UPDATE images
            SET image_feedback = :review
            WHERE image = :image_name
            """)
            with engine.connect() as conn:
                conn.execute(update_query, {"review": review, "image_name": image_name})
                conn.commit()
            st.success("Image review updated successfully!")
        except Exception as e:
            st.error(f"Failed to update image review: {e}")

    # Function to add a new prompt to the database
    def add_new_prompt(image_number, new_prompt):
        try:
            insert_query = text("""
            INSERT INTO prompts (sno, image_prompts, prompt_feedback)
            VALUES (:sno, :new_prompt, 'GOOD')
            """)
            with engine.connect() as conn:
                conn.execute(insert_query, {"sno": image_number, "new_prompt": new_prompt})
                conn.commit()
            st.success("New prompt added successfully!")
        except Exception as e:
            st.error(f"Failed to add new prompt: {e}")

    # Display images and prompts within the specified range
    for i in range(start_range, end_range + 1):
        image_name = f"image{i}.jpg"  # Construct the image filename using the image number
        image_path = os.path.join(image_folder, image_name)

        col1, col2 = st.columns([1, 2])

        with col1:
            # Download and display the image from Google Cloud Storage
            blob = bucket.blob(image_path)
            image_data = blob.download_as_bytes()
            image = Image.open(BytesIO(image_data))
            st.image(image, caption=f"Image {i}")

            # Add review option for the image
            image_review = st.radio(f"Review Image {i}:", ["GOOD", "BAD"], key=f"image_review_{i}")
            if st.button(f"Save Image Review {i}"):
                update_image_review(image_name, image_review)

        with col2:
            prompts_df = get_prompts(i)
            if not prompts_df.empty:
                # Create a selectbox to choose between the prompts
                prompt_options = prompts_df['image_prompts'].tolist()
                selected_prompt_index = st.selectbox(f"Select Prompt for Image {i}", range(len(prompt_options)), format_func=lambda x: f"Prompt {x+1}")
                selected_prompt = prompt_options[selected_prompt_index]
                serial_nos = prompts_df.iloc[selected_prompt_index]['serial_nos']

                st.write(f"Prompt {selected_prompt_index + 1}:")
                # Editable text area for the selected prompt
                new_prompt = st.text_area(f"Edit Prompt {selected_prompt_index + 1}", value=selected_prompt, key=f"prompt_{serial_nos}")

                # Review option for the selected prompt
                prompt_review = st.radio(f"Review Prompt {selected_prompt_index + 1}", ["GOOD", "BAD"], key=f"review_{serial_nos}")

                if st.button(f"Save Prompt {selected_prompt_index + 1}", key=f"save_prompt_{serial_nos}"):
                    update_prompt(serial_nos, new_prompt, prompt_review)
            else:
                st.warning(f"No prompts found for image {i}.")

            # Section to add a new prompt for the current image
            st.write(f"Add a new prompt for Image {i}:")
            new_prompt_input = st.text_area(f"New Prompt for Image {i}", key=f"new_prompt_{i}")
            if st.button(f"Add New Prompt for Image {i}"):
                if new_prompt_input.strip():
                    add_new_prompt(i, new_prompt_input)
                else:
                    st.warning("New prompt cannot be empty.")

        st.markdown("<hr style='border: 2px solid #ddd; margin: 20px 0;'>", unsafe_allow_html=True)
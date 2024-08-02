import streamlit as st
import PyPDF2
import json
import openai
import os
import re
from google.cloud import vision
from google.oauth2 import service_account
from PIL import Image
import xml.etree.ElementTree as ET
import time

# Set up Google Cloud Vision client using Streamlit secrets
credentials_dict = {
    "type": st.secrets["gcp_service_account"]["type"],
    "project_id": st.secrets["gcp_service_account"]["project_id"],
    "private_key_id": st.secrets["gcp_service_account"]["private_key_id"],
    "private_key": st.secrets["gcp_service_account"]["private_key"],
    "client_email": st.secrets["gcp_service_account"]["client_email"],
    "client_id": st.secrets["gcp_service_account"]["client_id"],
    "auth_uri": st.secrets["gcp_service_account"]["auth_uri"],
    "token_uri": st.secrets["gcp_service_account"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["gcp_service_account"]["client_x509_cert_url"]
}

credentials = service_account.Credentials.from_service_account_info(credentials_dict)
client = vision.ImageAnnotatorClient(credentials=credentials)

# Retrieve the OpenAI API key from Streamlit secrets
openai_api_key = st.secrets["OPENAI_API_KEY"]
openai.api_key = openai_api_key

# Set the page title
st.set_page_config(page_title="Invoice Extract")

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_image(file):
    image = Image.open(file)
    with open("temp_image.png", "wb") as f:
        image.save(f, format="PNG")
    with open("temp_image.png", "rb") as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    if response.error.message:
        raise Exception(f'{response.error.message}')
    return texts[0].description if texts else ""

def extract_text_from_xml(file):
    tree = ET.parse(file)
    root = tree.getroot()
    text = ET.tostring(root, encoding='unicode', method='text')
    return text

def extract_invoice_data(text):
    prompt = f"""
    Extract the following information from this invoice in JSON format:

    {{
        "Header Information": {{
            "Invoice Number": "",
            "Date": "",
            "Supplier Name": "",
            "Supplier Address": "",
            "Customer Name": "",
            "Customer Address": ""
        }},
        "Line Items": [
            {{
                "Description": "",
                "Quantity": "",
                "Unit Price": "",
                "Total": ""
            }}
        ]
    }}

    Invoice Text:
    {text}
    """
    response = openai.Completion.create(
        model="gpt-4",  # Use the correct model name
        prompt=prompt,
        max_tokens=500,
        temperature=0.5
    )
    return response['choices'][0]['text'].strip()

def main():
    st.title("Invoice Data Extractor")
    st.write("Upload your invoices to receive a structured JSON output. The following file formats are supported for upload (PDF, XML, TIF, PNG, or JPEG format).")

    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "xml", "tif", "tiff", "png", "jpeg", "jpg"])
    if uploaded_file is not None:
        start_time = time.time()  # Start the timer

        # Initialize the progress bar
        progress_text = st.empty()
        progress_bar = st.progress(0)
        
        progress_text.text("Extracting text from file...")
        progress_bar.progress(10)  # Update progress bar

        file_type = uploaded_file.name.split('.')[-1].lower()
        if file_type == 'pdf':
            text = extract_text_from_pdf(uploaded_file)
        elif file_type in ['png', 'jpeg', 'jpg', 'tif', 'tiff']:
            text = extract_text_from_image(uploaded_file)
        elif file_type == 'xml':
            text = extract_text_from_xml(uploaded_file)
        else:
            st.error("Unsupported file type.")
            return
        
        progress_text.text("Text extraction completed. Processing data...")
        progress_bar.progress(50)  # Update progress bar

        invoice_data = extract_invoice_data(text)

        progress_text.text("Data extraction completed. Preparing output...")
        progress_bar.progress(90)  # Update progress bar

        st.write("Extracted Data:")
        try:
            # Extract JSON from response
            json_data_match = re.search(r'\{.*\}', invoice_data, re.DOTALL)
            if json_data_match:
                json_data = json.loads(json_data_match.group())
                st.json(json_data)
                st.success("JSON is valid!")  # Display JSON validity message
            else:
                st.error("Could not find JSON data in the response. Please check the raw output.")
                st.text(invoice_data)
        except json.JSONDecodeError:
            st.error("Failed to parse JSON. Here is the raw output:")
            st.text(invoice_data)

        end_time = time.time()  # End the timer
        total_time = end_time - start_time
        st.write(f"Processing Time: {total_time:.2f} seconds")

        progress_text.text("Done!")
        progress_bar.progress(100)  # Complete the progress bar

if __name__ == "__main__":
    main()

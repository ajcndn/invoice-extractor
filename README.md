## UPDATE: Google Vision API is required. Tesseract is no longer used. 

# Invoice Data Extractor
Invoice Extractor is a simple web application built using Streamlit that allows users to upload invoices in various formats (PDF, XML, TIF, PNG, JPEG) and receive the extracted data in JSON format.

# Features
Upload invoices in multiple formats: Supports PDF, XML, TIF, PNG, and JPEG.
Data extraction: Extracts structured information from invoices, such as header details and line items.

# Requirements
Python 3.7+
Streamlit
PyPDF2
OpenAI
python-dotenv
pytesseract
Pillow

# Installation and Running the Application
pip install -r requirements.txt

# Tesseract Installation
Tesseract is required for OCR functionality on image files. Make sure Tesseract is installed on your machine.

# Set Up Environment Variables
Create a .env file in the root directory and add your OpenAI API key. This key is necessary to use OpenAI's GPT-4 model for data extraction.

OPENAI_API_KEY=your_openai_api_key

# Running the Application
To start the Streamlit application, run the following command:

streamlit run invoiceextract.py
This command will launch the app, and you can access it via your web browser at http://localhost:8501.

# Notes
Google Vision API Support: the application may include support for Google's Vision API as an alternative to Tesseract for OCR functionality.

#   i n v o i c e - e x t r a c t o r 
 
 

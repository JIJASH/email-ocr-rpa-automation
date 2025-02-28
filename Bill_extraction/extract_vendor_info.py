import os
import google.generativeai as genai
from PIL import Image
import pytesseract

# Load API key
API_KEY = "AIzaSyB98lwkMnIzfdNWF30uFpDut0MksFtZ5xU"
if not API_KEY:
    raise ValueError("API Key not found. Set GEMINI_API_KEY environment variable.")

# Configure Gemini Flash 1.5
genai.configure(api_key=API_KEY)

def extract_text_from_image(image_path):
    # Extract raw text from the image using OCR
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def extract_vendor_details(text):
    # Use Gemini Flash 1.5 to extract structured details from text.
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    Extract the following fields from this invoice text:
    - Name of the shopping store
    - Address
    - Contact Information
    - Total Amount
    - what is this image for

    Text:
    {text}
    
    Format the response in JSON.
    """

    response = model.generate_content(prompt)
    return response.text

def main(image_path):

    print("Extracting text from image...")
    text = extract_text_from_image(image_path)
    
    print("Extracting structured details using Gemini Flash 1.5...")
    extracted_info = extract_vendor_details(text)
    
    print("\nExtracted Vendor Details:")
    print(extracted_info)

if __name__ == "__main__":
    image_path = "Receipt.jpg"  # Replace with the actual file path
    main(image_path)

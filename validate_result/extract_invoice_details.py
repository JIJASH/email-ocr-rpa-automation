import requests
from PIL import Image
from dotenv import load_dotenv
import json
import pytesseract
import google.generativeai as genai
from mistralai import Mistral
import os
import re


def extract_text_from_image(image_path):
    """Extract raw text from an invoice image using OCR."""
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text


# Load API keys
load_dotenv()
GOOGLE_API_KEY = "AIzaSyAdGZuGWqNgPnnfE92DVi-ySi95H0MDYjc"

# Configure Google Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

#gemini
def extract_invoice_details(text):
    # to extract structured details from text usiing gemini
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    Extract Vendor Name, 
    Vendor ID,
    Vendor Contact,
    Vendor Address,

    Text:
    {text}
    
    Format the response in JSON.
    """
    #sending prompt to gemini
    response = model.generate_content(prompt)
    return response.text



#deepseek-r1-distill-llama-70b
# api key is passed from main function
def get_vendor_details(extracted_text, api_key):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    prompt = f"""
    Extract and structure the following details from the given text:
    - Vendor Name
    - Vendor ID
    - Vendor Contact
    - Vendor Address
    
    Respond ONLY in JSON format without any additional text.

    ----
    Text:
    {extracted_text}
    ----
    """

    data = {
        "model": "deepseek/deepseek-r1-distill-llama-70b:free",
        "messages": [{"role": "user", "content": prompt}],
    }

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        response_json = response.json()
        try:
            # Extract response text
            raw_text = response_json["choices"][0]["message"]["content"].strip()

            # Extract JSON part using regex (handles cases where LLM adds extra text)
            json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if json_match:
                structured_data = json.loads(json_match.group(0))
                return structured_data
            else:
                return {"error": "DeepSeek returned an invalid JSON format. Try adjusting the prompt."}
            
        except (KeyError, json.JSONDecodeError):
            return {"error": "Invalid response format from DeepSeek"}
    else:
        return {"error": f"API Error {response.status_code}: {response.text}"}

#mistral part
api_key = "uoZgiYf5wy8bscIAzH8h4E6YzXwjej5g"
model = "mistral-large-latest"

client = Mistral(api_key=api_key)

def extract_vendor_details_mistral(text):
    url = "https://api.mistral.ai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    Extract the following details from the given text:
    - Vendor Name
    - Vendor ID
    - Vendor Contact
    - Vendor Address

    Provide the response strictly in valid JSON format without any extra text.

    Text:
    {text}
    """

    payload = {
        "model": "mistral-large-latest",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        return {"error": f"API request failed with status {response.status_code}: {response.text}"}
    try:
        data = response.json()
        raw_content = data["choices"][0]["message"]["content"]
        print("Raw Response from Mistral:", raw_content)  # Debugging line

        # Try parsing JSON response
        return json.loads(raw_content)
    except (KeyError, json.JSONDecodeError) as e:
        return {"error": f"Invalid response format from Mistral: {str(e)}"}

def main(image_path):

    print("Extracting text from image...")
    text = extract_text_from_image(image_path)
    
    print("Extracting structured details using Gemini Flash 1.5...")
    extracted_info = extract_invoice_details(text)
    
    
    print("\nExtracted invoice Details using Gemini flash 1.5:")
    print(extracted_info)


    # Get structured vendor details
    api_key="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" 
    vendor_details = get_vendor_details(text,api_key)

    print("\nVendor Details using deepseek-r1-distill-llama-70b:")
    print(json.dumps(vendor_details, indent=4))

    #mistral part
    print("Using Mistral to extract vendor details...")
    vendor_details = extract_vendor_details_mistral(text)

    print(vendor_details) 


if __name__ == "__main__":
    image_path = "invoice.jpg"  
    main(image_path)







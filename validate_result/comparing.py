import json

def calculate_accuracy(predicted, expected):
    """Compares extracted vendor details with the expected values and calculates accuracy."""
    total_fields = len(expected)
    correct_fields = 0
    
    for key in expected:
        if key in predicted and predicted[key] == expected[key]:
            correct_fields += 1
        elif key in predicted and isinstance(predicted[key], str) and isinstance(expected[key], str):
            # Partial match check
            if expected[key].lower() in predicted[key].lower():
                correct_fields += 0.5
    
    return correct_fields / total_fields


def rank_models(gemini_response, deepseek_response, mistral_response):
    """Ranks models based on their extraction accuracy."""
    expected_data = {
        "Vendor Name": "AP Global Logistic",
        "Vendor ID": "AKUPB7482M",
        "Vendor Contact": ["9873806384, 9873599450, 0129 2281711"],
        "Vendor Address": "17/6, Mathura road, Sarpanch colony, Faridabad-121002 (Haryana)"
    }
    
    results = {
        "Gemini Flash 1.5": calculate_accuracy(gemini_response, expected_data),
        "DeepSeek R1 Distill": calculate_accuracy(deepseek_response, expected_data),
        "Mistral Large": calculate_accuracy(mistral_response, expected_data)
    }
    
    ranked_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    
    print("\nModel Ranking Based on Accuracy:")
    for rank, (model, score) in enumerate(ranked_results, 1):
        print(f"{rank}. {model}: {score * 100:.2f}% accuracy")


# Example extracted responses from models (Replace these with actual responses)
gemini_extracted = {
    "Vendor Name": "AP GLOBAL LOGISTICS",
    "Vendor ID": "OGAKUPB7482M1ZG", 
    "Vendor Contact": "9873806384, 9873599450, 0129 2281711",
    "Vendor Address": "17/6, Mathura road, Sarpanch colony, Faridabad-121002 (Haryana)"
}

deepseek_extracted = {
    "Vendor ID": "GSTIN-OGAKUPB7482M1ZG",
    "Vendor Name": "HGL AP GLOBAL LOGISTICS",
    "Vendor Contact": [ "9873806384","9873599450" ,"0129 2281711"],
    "Vendor Address": "Regd. Office : 17/6, Mathura road, Sarpanch colony, Faridabad-121002 (Haryana)"
}

mistral_extracted = {
    "Vendor Name": "HGL AP GLOBAL LOGISTICS",
    "Vendor ID": "",
    "Vendor Contact": "9873806384, 9873599450, 0129 2281711",
    "Vendor Address": "17/6, Mathura road, Sarpanch colony, Faridabad-121002 (Haryana)"
}

# Call ranking function
rank_models(gemini_extracted, deepseek_extracted, mistral_extracted)

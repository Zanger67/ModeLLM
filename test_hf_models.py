import os
import requests
import time
import dotenv
from typing import Dict, List

# Load environment variables from .env file
dotenv.load_dotenv()

# Models to test
MODELS_TO_TEST = [
    "gpt2",
    "facebook/opt-125m",
    "microsoft/phi-1_5",
    "distilgpt2",
    "microsoft/phi-2",
    "google/gemma-7b-it",
    "meta-llama/Llama-3.1-8B-Instruct",
    "meta-llama/Llama-2-7b-chat-hf",
    "mistralai/Mistral-7B-Instruct-v0.2",
    "mistralai/Mistral-7B-Instruct-v0.3"
]

def test_huggingface_model(model_name: str) -> Dict:
    """
    Test if a Hugging Face model can be queried via the API.
    
    Args:
        model_name: Name of the model to test
        
    Returns:
        Dictionary with test results
    """
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        return {
            "model": model_name,
            "status": "error",
            "message": "HUGGINGFACE_API_KEY environment variable not set"
        }
    
    api_url = f"https://api-inference.huggingface.co/models/{model_name}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Simple test prompt
    prompt = "The global carbon tax is"
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 50,
            "temperature": 0.7,
            "return_full_text": False
        }
    }
    
    start_time = time.time()
    
    try:
        print(f"Testing model: {model_name}...")
        response = requests.post(api_url, headers=headers, json=payload, timeout=20)
        elapsed_time = time.time() - start_time
        
        # Check if request was successful
        if response.status_code == 200:
            try:
                output = response.json()
                return {
                    "model": model_name,
                    "status": "success",
                    "response_time": f"{elapsed_time:.2f}s",
                    "output": output
                }
            except Exception as e:
                return {
                    "model": model_name,
                    "status": "error",
                    "response_time": f"{elapsed_time:.2f}s",
                    "message": f"Failed to parse response JSON: {str(e)}",
                    "raw_response": response.text[:500]  # First 500 chars only
                }
        else:
            return {
                "model": model_name,
                "status": "error",
                "response_time": f"{elapsed_time:.2f}s",
                "message": f"API request failed with status code {response.status_code}",
                "raw_response": response.text[:500]  # First 500 chars only
            }
            
    except requests.exceptions.Timeout:
        elapsed_time = time.time() - start_time
        return {
            "model": model_name,
            "status": "error",
            "response_time": f"{elapsed_time:.2f}s",
            "message": "Request timed out after 10 seconds"
        }
    except requests.exceptions.RequestException as e:
        elapsed_time = time.time() - start_time
        return {
            "model": model_name,
            "status": "error",
            "response_time": f"{elapsed_time:.2f}s",
            "message": f"Request failed: {str(e)}"
        }

def main():
    print("Testing Hugging Face model API access...")
    print(f"API key present: {'Yes' if os.getenv('HUGGINGFACE_API_KEY') else 'No'}")
    print("=" * 50)
    
    results = []
    for model in MODELS_TO_TEST:
        result = test_huggingface_model(model)
        results.append(result)
        
        # Print result summary
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"{status_icon} {result['model']} - {result['status']} ({result.get('response_time', 'N/A')})")
        
        if result["status"] == "error":
            print(f"  Error: {result.get('message', 'Unknown error')}")
        elif result["status"] == "success":
            try:
                if isinstance(result["output"], list) and len(result["output"]) > 0:
                    if "generated_text" in result["output"][0]:
                        print(f"  Output: {result['output'][0]['generated_text'][:100]}...")
                    else:
                        print(f"  Output: {str(result['output'])[:100]}...")
                else:
                    print(f"  Output: {str(result['output'])[:100]}...")
            except:
                print(f"  Output: {str(result['output'])[:100]}...")
        
        print("-" * 50)
        time.sleep(1)  # Avoid rate limiting
    
    # Print final summary
    successful_models = [r["model"] for r in results if r["status"] == "success"]
    
    print("\nSUMMARY:")
    print(f"Total models tested: {len(MODELS_TO_TEST)}")
    print(f"Successful models: {len(successful_models)}")
    
    if successful_models:
        print("\nModels you can use in your simulation:")
        for model in successful_models:
            print(f"- {model}")
    
    if len(successful_models) == 0:
        print("\nNo models were successfully queried. Possible issues:")
        print("1. Hugging Face API might be down or experiencing issues")
        print("2. Your API token might be invalid or expired")
        print("3. You might be rate limited")
        print("\nConsider using mock_mode=True in your simulation for now.")

if __name__ == "__main__":
    main() 
import os
import time
import dotenv
from typing import Dict, List
from openai import OpenAI

# Load environment variables from .env file
dotenv.load_dotenv()

# Models to test
MODELS_TO_TEST = [
    "gpt-3.5-turbo",
    "gpt-4",
    "gpt-4-turbo-preview",
    "o3"
]

def test_openai_model(model_name: str) -> Dict:
    """
    Test if an OpenAI model can be queried via the API.
    
    Args:
        model_name: Name of the model to test
        
    Returns:
        Dictionary with test results
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "model": model_name,
            "status": "error",
            "message": "OPENAI_API_KEY environment variable not set"
        }
    
    # Create OpenAI client
    try:
        client = OpenAI(api_key=api_key)
    except Exception as e:
        return {
            "model": model_name,
            "status": "error",
            "message": f"Failed to create OpenAI client: {str(e)}"
        }
    
    # Simple test prompt
    prompt = "The global carbon tax is"
    
    start_time = time.time()
    
    try:
        print(f"Testing model: {model_name}...")
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.7
        )
        elapsed_time = time.time() - start_time
        
        return {
            "model": model_name,
            "status": "success",
            "response_time": f"{elapsed_time:.2f}s",
            "output": response.choices[0].message.content
        }
    
    except Exception as e:
        elapsed_time = time.time() - start_time
        return {
            "model": model_name,
            "status": "error",
            "response_time": f"{elapsed_time:.2f}s",
            "message": f"API request failed: {str(e)}"
        }

def main():
    print("Testing OpenAI model API access...")
    print(f"API key present: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
    print("=" * 50)
    
    results = []
    for model in MODELS_TO_TEST:
        result = test_openai_model(model)
        results.append(result)
        
        # Print result summary
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"{status_icon} {result['model']} - {result['status']} ({result.get('response_time', 'N/A')})")
        
        if result["status"] == "error":
            print(f"  Error: {result.get('message', 'Unknown error')}")
        elif result["status"] == "success":
            print(f"  Output: {result['output'][:100]}...")
        
        print("-" * 50)
        time.sleep(1)  # Be nice to the API
    
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
        print("1. Your API key might be invalid or expired")
        print("2. You might not have access to these models")
        print("3. You might be rate limited or have billing issues")
        print("\nConsider using mock_mode=True in your simulation for now.")

if __name__ == "__main__":
    main() 
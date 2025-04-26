#!/usr/bin/env python3
"""
HuggingFace Chat - Terminal interface for chatting with HuggingFace models
via their inference API.
"""

import os
import json
import sys
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API token from environment variable
HF_API_TOKEN = os.getenv("HUGGINGFACE_API_KEY")
if not HF_API_TOKEN:
    print("Error: HUGGINGFACE_API_KEY not found in .env file")
    print("Please add your Hugging Face API token to the .env file")
    sys.exit(1)

# Default model to use (can be changed)
DEFAULT_MODEL = "tiiuae/Falcon3-10B-Instruct"

# ANSI escape codes for colored output
class Colors:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def format_chat_prompt(messages, model_name):
    """
    Format the chat prompt according to the model's expected format.
    Different models may require different formats.
    """
    if "llama" in model_name.lower():
        # Llama-specific chat format
        formatted_prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                formatted_prompt += f"<|system|>\n{content}</s>\n"
            elif role == "user":
                formatted_prompt += f"<|user|>\n{content}</s>\n"
            elif role == "assistant":
                formatted_prompt += f"<|assistant|>\n{content}</s>\n"
        
        # Add final assistant prompt
        formatted_prompt += "<|assistant|>\n"
        return formatted_prompt
    
    elif "mistral" in model_name.lower():
        # Mistral-specific chat format
        formatted_prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                formatted_prompt += f"<s>[INST] {content} [/INST]"
            elif role == "user":
                formatted_prompt += f"<s>[INST] {content} [/INST]"
            elif role == "assistant":
                formatted_prompt += f" {content} </s>"
        
        return formatted_prompt
    
    else:
        # Generic format - works with many models
        # Just concatenate messages with roles
        formatted_prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            formatted_prompt += f"{role.upper()}: {content}\n"
        
        formatted_prompt += "ASSISTANT: "
        return formatted_prompt

def query_huggingface_api(model_name, prompt, api_token, temperature=0.7, max_length=1024):
    """
    Send a query to the Hugging Face Inference API and return the response.
    """
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    # API endpoint
    api_url = f"https://api-inference.huggingface.co/models/{model_name}"
    
    # Request payload
    payload = {
        "inputs": prompt,
        "parameters": {
            "temperature": temperature,
            "max_new_tokens": max_length,
            "return_full_text": False,
        }
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                if "generated_text" in result[0]:
                    return result[0]["generated_text"]
                else:
                    return str(result[0])
            else:
                return str(result)
        else:
            error_msg = f"Error {response.status_code}: {response.text}"
            print(f"{Colors.RED}API Error: {error_msg}{Colors.RESET}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}Request error: {str(e)}{Colors.RESET}")
        return None

def main():
    # Get model name from command line args or use default
    model_name = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODEL
    
    # Display welcome message
    clear_screen()
    print(f"{Colors.BOLD}{Colors.BLUE}🤖 HuggingFace Chat Terminal{Colors.RESET}")
    print(f"Model: {Colors.GREEN}{model_name}{Colors.RESET}")
    print(f"Type {Colors.YELLOW}'exit'{Colors.RESET} or {Colors.YELLOW}'quit'{Colors.RESET} to end the conversation.")
    print(f"Type {Colors.YELLOW}'clear'{Colors.RESET} to clear the conversation history.")
    print("-" * 50)
    
    # Initialize conversation history
    conversation = [
        {"role": "system", "content": "You are a helpful, respectful, and honest assistant. Always answer as helpfully as possible."}
    ]
    
    # Main chat loop
    while True:
        # Get user input
        user_input = input(f"{Colors.BOLD}You:{Colors.RESET} ")
        
        # Handle special commands
        if user_input.lower() in ["exit", "quit"]:
            print(f"{Colors.BLUE}Goodbye!{Colors.RESET}")
            break
        elif user_input.lower() == "clear":
            clear_screen()
            conversation = [
                {"role": "system", "content": "You are a helpful, respectful, and honest assistant. Always answer as helpfully as possible."}
            ]
            print(f"{Colors.BLUE}Conversation history cleared.{Colors.RESET}")
            continue
        
        # Add user message to conversation
        conversation.append({"role": "user", "content": user_input})
        
        # Format the prompt according to the model's requirements
        formatted_prompt = format_chat_prompt(conversation, model_name)
        
        # Show thinking indicator
        print(f"{Colors.BOLD}Assistant:{Colors.RESET} {Colors.YELLOW}Thinking...{Colors.RESET}", end="\r")
        
        # Query the model
        response = query_huggingface_api(model_name, formatted_prompt, HF_API_TOKEN)
        
        # Clear the thinking indicator
        print(" " * 50, end="\r")
        
        if response:
            # Display the response
            print(f"{Colors.BOLD}Assistant:{Colors.RESET} {response.strip()}")
            
            # Add assistant response to conversation history
            conversation.append({"role": "assistant", "content": response.strip()})
        else:
            print(f"{Colors.RED}Failed to get a response from the model.{Colors.RESET}")
        
        print("-" * 50)

if __name__ == "__main__":
    main() 
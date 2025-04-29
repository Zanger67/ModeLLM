import json
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

import dotenv
import replicate
from icecream import ic
from openai import OpenAI

from programs.history import CommitteeHistory, Message, Note

dotenv.load_dotenv()

class Model(ABC):
    def __init__(self, model_name: str | None = None, *args, **kwargs) -> None :
        self.model_name     = model_name
        self.model          = self._load_model()

    @abstractmethod
    def _load_model(self) -> Any :
        '''
        Load the model based on the appropriate API using a .env API key.
        '''
        pass

    @abstractmethod
    def query(self, messages) -> str :
        '''
        Query the model with the given messages.
        '''
        pass
    
    # @abstractmethod
    # def generate_payload(self, messages) -> Any :
    #     '''
    #     Generate the payload for the model based on the messages.
    #     '''
    #     pass

class OpenAIModel(Model) :
    def _load_model(self) -> OpenAI :
        '''
        Load the model based on the appropriate API using a .env API key.
        '''
        # self.model_name = "gpt-3.5-turbo"
        if self.model_name is None :
            raise ValueError("Model name must be specified")
        
        # # # NO LONGER REQUIRED DUE TO THIS BEING A DUTY OF THE MODEL MANAGER
        # # If no model_options exists, all models are permitted
        # if self.model_options and self.model_name not in self.model_options :
        #     raise ValueError(f"Model {self.model_name} not found in model list." + 
        #                       "Either model is invalid or model is not currently permitted.")
        # else :
        #     ic(f"Model {self.model_name} found in model list.")
            
        
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    
    def parse_response_message(self, response) -> str :
        try :
            return response.choices[0].message.content
        except AttributeError as e :
            ic(f"Error parsing response: {e}")
            ic("Response:", response)
            ic("Traceback:", e.__traceback__)
            return "ERROR RESPONSE"
    
    _MESSAGE_TEMPLATE = '[{time}] {content}'
    def _format_msg(self, message: Message) -> str :
        return self._MESSAGE_TEMPLATE.format(
            time=message.time,
            # speaker=message.speakers[0],
            content=message.content
            # TODO: word cap context? context as to what type of conversation 
            #       it was e.g. a group discussion or a speech?
        )
    
    _NOTE_TEMPLATE = '[{time}] NOTE TO SELF: {content}'
    def _format_note(self, note: Note) -> str :
        return self._NOTE_TEMPLATE.format(
            time=note.time,
            content=note.content
        )
    
    def generate_payload(self, 
                         instructions: str, 
                         character_name: str, 
                         history: CommitteeHistory,
                         send_only_instructions: bool = False) -> List[Dict[str, str]] :
        '''
        Generate the payload for an OpenAI model from a list of messages.
        '''
        if send_only_instructions or history is None :
            return [
                {
                    'role': 'user',
                    'content': instructions
                }
            ]
            
        payload = []
        
        # Insert context of the scenario in terms of structure here
        
        
        
        # Give context of the character's personality here
        
        character_history = history.get_character_context(character_name)
        if character_history :
            ic(f"Character history found and added to payload for '{character_name}'")
            payload.append({
                'role': 'system',
                'content': (
                    "You are a member of a diplomatic committee with the following description:" + 
                    f"\n{character_history}"
                )
            })
        else :
            ic(f"No character history found for '{character_name}'")
        
        
        # Give context of the other characters here
        
        
        # Give context of the chatlogs and notes here
        
        chat_history = history.get_chat_history(character_name)
        if chat_history :
            ic(f"Chat history found and added to payload for '{character_name}'")
            for message in chat_history :
                if character_name in message.speakers :
                    payload.append({
                        'role': 'assistant',
                        'content': self._format_msg(message)
                    })
                else :
                    speaker = message.speakers[0] # should only be one speaker at 
                                                  # any given time. This is just in case
                                                  # of a need for future implementations
                    payload.append({
                        'role': 'user',
                        'name': speaker,
                        'content': self._format_msg(message)
                    })
        else :
            ic(f"No chat history found for '{character_name}'")

        # TODO: see if it would be preferable to insert these alongside the messages so
        #       that everything's in creation order rather than having notes separate and at the end
        note_history = history.get_notes(character_name)
        if note_history :
            ic(f"Note history found and added to payload for '{character_name}'")
            for note in note_history :
                payload.append({
                    'role': 'assistant',
                    'content': self._format_note(note)
                })
        else :
            ic(f"No note history found for '{character_name}'")
            
        # Add the current instruction
        payload.append({
            'role': 'user',
            'content': instructions
        })
        
        return payload
    
    def generate_payload_from_str(self, message: str) -> List[Dict[str, str]] :
        '''
        Generate the payload for an OpenAI model from a single string message. 
        NO CONTEXT HISTORY PROVIDED.
        '''
        return [
            {
                'role': 'user',
                'content': message
            }
        ]
    
    # NOTE: format message so the last message is a SYSTEM message telling 
    #       the word limits and intent
    def query(self, messages: str | List[Any]) -> str :
        '''
        Query the model with the given messages.
        '''
        if isinstance(messages, str) :
            messages = self.generate_payload_from_str(messages)
            # raise NotImplementedError("String messages not implemented")
        
        response = self.model.chat.completions.create(
            model=self.model_name,
            messages=messages
        )
        
        ic(f"Response: {response}")
        ic()
        
        return self.parse_response_message(response)
    

class HuggingFaceModel(Model):
    def _load_model(self) -> Any:
        """
        Set up to use Hugging Face Inference API instead of loading models locally.
        """
        if self.model_name is None:
            raise ValueError("Model name must be specified")
        
        try:
            import requests
            
            # No model loading needed, just return the API key for use in API calls
            self.api_key = os.getenv("HUGGINGFACE_API_KEY")
            if not self.api_key:
                raise ValueError("HUGGINGFACE_API_KEY environment variable not set")
            
            # Set up the API endpoint
            self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
            self.headers = {"Authorization": f"Bearer {self.api_key}"}
            
            ic(f"Using Hugging Face API for model: {self.model_name}")
            
            # Return anything (not used directly)
            return self.api_key
            
        except ImportError as e:
            ic(f"Error importing required packages: {e}")
            raise ImportError("Please install required packages: 'pip install requests'")
    
    def parse_response_message(self, response) -> str:
        """
        Parse the response from Hugging Face API.
        """
        try:
            # The response format varies by model type, but for text generation
            # it usually returns a list of generated texts
            if isinstance(response, list) and len(response) > 0:
                if isinstance(response[0], dict) and "generated_text" in response[0]:
                    return response[0]["generated_text"]
                else:
                    return str(response[0])
            else:
                return str(response)
        except Exception as e:
            ic(f"Error parsing response: {e}")
            ic("Response:", response)
            return "ERROR RESPONSE"
    
    _MESSAGE_TEMPLATE = '[{time}] {content}'
    def _format_msg(self, message: Message) -> str:
        return self._MESSAGE_TEMPLATE.format(
            time=message.time,
            content=message.content
        )
    
    _NOTE_TEMPLATE = '[{time}] NOTE TO SELF: {content}'
    def _format_note(self, note: Note) -> str:
        return self._NOTE_TEMPLATE.format(
            time=note.time,
            content=note.content
        )
    
    def _format_messages_for_hf(self, messages: List[Dict[str, str]]) -> str:
        """
        Format messages for Hugging Face models. This combines all messages
        into a single prompt string with appropriate formatting.
        """
        formatted_prompt = ""
        
        for msg in messages:
            role = msg.get('role', '')
            content = msg.get('content', '')
            name = msg.get('name', '')
            
            if role == 'system':
                formatted_prompt += f"<|system|>\n{content}\n"
            elif role == 'user':
                if name:
                    formatted_prompt += f"<|user|>{name}: {content}\n"
                else:
                    formatted_prompt += f"<|user|>\n{content}\n"
            elif role == 'assistant':
                formatted_prompt += f"<|assistant|>\n{content}\n"
        
        # Add final assistant prompt to trigger generation
        formatted_prompt += "<|assistant|>\n"
        
        return formatted_prompt
    
    def generate_payload(self, 
                         instructions: str, 
                         character_name: str, 
                         history: CommitteeHistory,
                         send_only_instructions: bool = False) -> List[Dict[str, str]]:
        """
        Generate the payload for a Hugging Face model from a list of messages.
        """
        if send_only_instructions or history is None:
            return [
                {
                    'role': 'user',
                    'content': instructions
                }
            ]
        
        payload = []
        
        # Character context/personality
        character_history = history.get_character_context(character_name)
        if character_history:
            ic(f"Character history found and added to payload for '{character_name}'")
            payload.append({
                'role': 'system',
                'content': (
                    "You are a member of a diplomatic committee with the following description:" + 
                    f"\n{character_history}"
                )
            })
        else:
            ic(f"No character history found for '{character_name}'")
        
        # Chat history
        chat_history = history.get_chat_history(character_name)
        if chat_history:
            ic(f"Chat history found and added to payload for '{character_name}'")
            for message in chat_history:
                if character_name in message.speakers:
                    payload.append({
                        'role': 'assistant',
                        'content': self._format_msg(message)
                    })
                else:
                    speaker = message.speakers[0]
                    payload.append({
                        'role': 'user',
                        'name': speaker,
                        'content': self._format_msg(message)
                    })
        else:
            ic(f"No chat history found for '{character_name}'")
        
        # Notes
        note_history = history.get_notes(character_name)
        if note_history:
            ic(f"Note history found and added to payload for '{character_name}'")
            for note in note_history:
                payload.append({
                    'role': 'assistant',
                    'content': self._format_note(note)
                })
        else:
            ic(f"No note history found for '{character_name}'")
        
        # Add the current instruction
        payload.append({
            'role': 'user',
            'content': instructions
        })
        
        return payload
    
    def generate_payload_from_str(self, message: str) -> List[Dict[str, str]]:
        """
        Generate the payload for a Hugging Face model from a single string message.
        NO CONTEXT HISTORY PROVIDED.
        """
        return [
            {
                'role': 'user',
                'content': message
            }
        ]
    
    def query(self, messages: str | List[Any]) -> str:
        """
        Query the Hugging Face model via API.
        """
        if isinstance(messages, str):
            messages = self.generate_payload_from_str(messages)
        
        # Format messages for Hugging Face
        prompt = self._format_messages_for_hf(messages)
        
        # Generate response via API
        try:
            import requests
            import json
            import time
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 1024,
                    "temperature": 0.7,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            # Make the API request
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 20))
                ic(f"Rate limited. Waiting for {retry_after} seconds...")
                time.sleep(retry_after)
                response = requests.post(self.api_url, headers=self.headers, json=payload)
            
            # Handle other errors
            if response.status_code != 200:
                error_msg = f"API request failed with status code {response.status_code}: {response.text}"
                ic(error_msg)
                return f"ERROR: {error_msg}"
            
            # Parse the response
            result = response.json()
            ic(f"HF API Response: {result}")
            
            # Extract the generated text
            generated_text = self.parse_response_message(result)
            
            # Remove the prompt part to get only the model's response
            if generated_text.startswith(prompt):
                return generated_text[len(prompt):].strip()
                
            return generated_text
            
        except Exception as e:
            ic(f"Error querying HuggingFace API: {e}")
            return f"ERROR: Failed to query model: {str(e)}"

# TODO: Implement this; map aliases (names of delegations/delegates) to 
# specific models and their proper implementations
class ModelManager:
    characters: Dict[str, str]          # {delegate name: model name}
    models: Dict[str, Model]            # {model name: model class}
    
    def __init__(self) -> None :
        self.model_options = None
        self.class_name_to_class = None
        self._load_model_options()
        
        self.characters = {}
        self.models = {}
    
    def _is_permitted_model(self, model_name: str) -> bool :
        '''
        Check if the model is one of the permitted models.
        '''
        return (model_name in self.model_options)
    
    def _get_model(self, model_name: str) -> Model :
        '''
        Get the model class based on the model name.
        '''
        if model_name not in self.model_options :
            raise ValueError(f"Model {model_name} not found in model list." +
                                "Either model is invalid or model is not currently permitted.")
            
        if model_name in self.models :
            ic(f"Model {model_name} already exists. Returning...")
            return self.models[model_name]

        # Adding a new model if necessary
        ic(f"Model {model_name} not found in model list. Creating new instance of model...")
        class_name  = self.model_options[model_name]["class"].lower()
        model_class = self.class_name_to_class.get(class_name, None)
        
        if model_class is None :
            raise ValueError(f"Model class {class_name} not found in model list." +
                             "Either model is invalid or model is not currently permitted.")
            
        self.models[model_name] = model_class(model_name=model_name)
        ic(f"Model {model_name} created.")
        
        return self.models[model_name]

    def add_character(self, character_name: str, model_name: str) -> None :
        # raise NotImplementedError("ModelManager.add_character() not implemented")
        if character_name in self.characters :
            ic(f"Character {character_name} already exists. Cancelling add.")
            return

        # model = None
        # if model_name not in self.models :
        #     if not self._is_permitted_model(model_name) :
        #         ic(f"Model {model_name} is not permitted. Cancelling add.")
        #         raise ValueError(f"Model {model_name} is not permitted.")
            
            # TODO
            
        model = self._get_model(model_name)
        self.characters[character_name] = model_name
        
    
    def remove_character(self, character_name: str) -> None :
        raise NotImplementedError("ModelManager.remove_character() not implemented")
    
    def get_character_model(self, character_name: str) -> Model :
        raise NotImplementedError("ModelManager.get_character_model() not implemented")
    
    def get_model(self, model_name: str) -> Model :
        raise NotImplementedError("ModelManager.get_model() not implemented")
    
    # TODO: plan speaking method to prevent AI from performing speeches that aren't permitted
    #       e.g. talking to multiple groups at the same time
    # def character_turn(self, character_name: str, messages: str | List[Any]) -> str :
    
    def get_character_list_tuple(self) -> List[Tuple[str, str]] :
        '''
        Get the list of characters.
        '''
        return sorted([(character, model) for character, model in self.characters.items()], key=lambda x: x[-1])
    
    def get_character_list_str_list(self) -> str :
        max_character_length = max([len(character) for character in self.characters.keys()]) + 3
        return [f"{character:<{max_character_length}} ({model})" for character, model in self.characters.items()]
    
    def get_character_list_str(self) -> str :
        '''
        Get the list of characters as a string.
        '''
        return "\n".join(self.get_character_list_str_list())
    
    
    def _load_model_options(self, model_options_path: str = None) -> None :
        output = {}
        
        try :
            if model_options_path is None :
                model_options_path = os.path.join(os.path.dirname(__file__), "models.json")
            
            with open(model_options_path, "r") as f :
                output = json.load(f)
        except FileNotFoundError as e :
            ic(f"Error loading model options: {e}")
            output = {}
            
        
            
        self.model_options = output
        self.class_name_to_class = { # TODO: once implemented, add this
            'openai': OpenAIModel,
            'replicate': None,
            'huggingface': HuggingFaceModel
        }
    
    def query_character(self, character_name: str, message: str, history: CommitteeHistory) -> str :
        '''
        Query the character with the given message. This performs a single
        API call with the message and its context history.
        '''
        if character_name not in self.characters :
            raise ValueError(f"Character {character_name} not found in character list.")
        
        model_name = self.characters[character_name]
        model = self._get_model(model_name)
        
        # Generate payload with context history
        payload = model.generate_payload(message, character_name, history)
        return model.query(payload)


def main() -> None : # tester
    pass
    
if __name__ == "__main__":
    main()
from abc import ABC, abstractmethod
import json

from openai import OpenAI
import replicate

import os
import dotenv
from icecream import ic

from typing import Any, List

dotenv.load_dotenv()


# Maps the model text name to the class
MODEL_MAP = {
    
}

class Model(ABC):
    def __init__(self, model_name: str | None = None, *args, **kwargs) -> None :
        self.model_name     = model_name
        self.model_options  = self._load_model_options()
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
    
    
    def _load_model_options(self, model_options_path: str = None) -> None :
        try :
            if model_options_path is None :
                model_options_path = os.path.join(os.path.dirname(__file__), "models.json")
            
            with open(model_options_path, "r") as f :
                self.model_options = json.load(f)
        except FileNotFoundError as e :
            ic(f"Error loading model options: {e}")
            self.model_options = {}

class OpenAIModel(Model) :
    def _load_model(self) -> OpenAI :
        '''
        Load the model based on the appropriate API using a .env API key.
        '''
        # self.model_name = "gpt-3.5-turbo"
        if self.model_name is None :
            raise ValueError("Model name must be specified")
        
        # If no model_options exists, all models are permitted
        if self.model_options and self.model_name not in self.model_options :
            raise ValueError(f"Model {self.model_name} not found in model list." + 
                              "Either model is invalid or model is not currently permitted.")
        else :
            ic(f"Model {self.model_name} found in model list.")
            
        
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    
    def parse_response_message(self, response) -> str :
        try :
            return response.choices[0].message.content
        except AttributeError as e :
            ic(f"Error parsing response: {e}")
            ic("Response:", response)
            ic("Traceback:", e.__traceback__)
            return "ERROR RESPONSE"
    
    # NOTE: format message so the last message is a SYSTEM message telling 
    #       the word limits and intent
    def query(self, messages: str | List[Any]) -> str :
        '''
        Query the model with the given messages.
        '''
        if isinstance(messages, str) :
            raise NotImplementedError("String messages not implemented")
        
        response = self.model.chat.completions.create(
            model=self.model_name,
            messages=messages
        )
        
        ic(f"Response: {response}")
        ic()
        
        return self.parse_response_message(response)
    

# TODO: Implement this; map aliases (names of delegations/delegates) to 
# specific models and their proper implementations
class ModelManager:
    pass



def openai_test() -> None :
    # model_name = 'gpt-3.5-turbo'
    # model_name = 'o4-mini'
    # model_name = 'o1-mini'
    model_name = 'gpt-4o-2024-11-20'
    # model_name = 'o1'
    # model_name = 'gpt-4'
    oaim = OpenAIModel(model_name=model_name)
    print(oaim.model_name)
    print(oaim.query(messages=[
        {
            'role': 'user',
            'content': 'what\'s the best way to bake a baguette? can you give me a series of instructions?'
        }
    ]))
    

def replicate_llama_4_test() -> None :
    input = {
        "prompt": "Hello, Llama!"
    }

    output = []
    for event in replicate.stream(
        "meta/llama-4-maverick-instruct",
        input=input
    ):
        print(event, end="")
        output.append(event)
    
    print()
    # print(output)
    print("---".join([str(x) for x in output]))

    # for x in output :
        # print(str(x))
        # print(f'{type(x) = }')

    
def main() -> None : # tester
    openai_test()
    # replicate_llama_4_test()
    
if __name__ == "__main__":
    main()
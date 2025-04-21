from abc import ABC, abstractmethod

from openai import OpenAI
import replicate

import os
import dotenv
from icecream import ic

from typing import Any, List

dotenv.load_dotenv()





class Model(ABC):
    def __init__(self, model_name: str | None = None, *args, **kwargs) -> None :
        self.model_name = model_name
        self.model = self._load_model()

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

class OpenAIModel(Model) :
    def _load_model(self) -> None :
        '''
        Load the model based on the appropriate API using a .env API key.
        '''
        # self.model_name = "gpt-3.5-turbo"
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
        
        print(f"Response: {response}")
        print()
        
        return self.parse_response_message(response)
    


def openai_test() -> None :
    oaim = OpenAIModel(model_name="gpt-3.5-turbo")
    print(oaim.model_name)
    print(oaim.query(messages=[
        {
            'role': 'user',
            'content': 'what\'s the best way to bake a baguette? can you give me a series of instructions?'
        }
    ]))
    
    # openai_client = OpenAI(
    #     api_key=os.getenv("OPENAI_API_KEY")
    # )
    
    # response = openai_client.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         # {
    #         #     "role": "user",
    #         #     "content": "What is the capital of France?"
    #         # }
            
    #         {
    #             "role": "system",
    #             "content": "What is the capital of France?"
    #         }
    #     ]
    # )
    # print(response.choices[0].message.content)

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
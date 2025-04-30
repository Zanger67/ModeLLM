
from openai import OpenAI
import os

from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    client = OpenAI(
        api_key = os.getenv('OPENAI_API_KEY')
    )
    models = client.models.list()
    for model in models:
        print(f'"{model.id}",')
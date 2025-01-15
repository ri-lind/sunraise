import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),  # This is the default and can be omitted
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Hello ChatGPT. I am contacting you from a python program using the OpenAI SDK for Python.",
        }
    ],
    model="gpt-4o-mini",
)

print(chat_completion.choices[0])
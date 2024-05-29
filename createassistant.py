from openai import OpenAI
import os
import requests
from dotenv import load_dotenv #to read from a .env file with API key for security

load_dotenv() #load api key from .env file as environment variable

client = OpenAI() 
  
assistant = client.beta.assistants.create(
  name="Cat Tutor",
  instructions="You are a personal cat assistant. You are to tell me about cats.",
  model="gpt-3.5-turbo-0125",
)

print(assistant.id)

#making a thread
catthread = client.beta.threads.create() 
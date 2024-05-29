tools = [
  {
    "type": "function",
    "function": {
      "name": "get_cat",
      "description": "Get a picture of a cat to display",
      "parameters": {
        "type": "object",
        "properties": {
          "breed": {
            "type": "string",
            "description": "The breed of cat",
          },
        },
        "required": ["breed"],
      },
    }
  }
]


import requests
import os


def get_breed_code(breed):
    url = f'https://api.thecatapi.com/v1/breeds/search?q={breed}'
    
    try:
        response = requests.get(url)
        data = response.json()
        if data:
            return data[0]['id']
        else:
            return "No breed found with that name."
    except Exception as e:
        return f"Error occurred: {e}"

def get_cat_image_url(breed):
    breed_code = get_breed_code(breed)
    if breed_code == "No breed found with that name.":
        return breed_code
    else:
        api_key = os.getenv('cat_api')  
        url = f'https://api.thecatapi.com/v1/images/search?breed_ids={breed_code}&api_key={api_key}'
        
        try:
            response = requests.get(url)
            data = response.json()
            if data:
                return data[0]['url']
            else:
                return "No image found for this breed."
        except Exception as e:
            return f"Error occurred: {e}"
        
import json

#function to get outputs from the initial call, to put into the second call. returns a json format
def get_outputs_for_tool_call(tool_call): 
    breed = json.loads(tool_call.function.arguments)["breed"]
    cat_url = get_cat_image_url(breed)
    return {"tool_call_id": tool_call.id,
            "output": cat_url}
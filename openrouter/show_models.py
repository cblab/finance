import os
import requests
import json
from dotenv import load_dotenv

# .env laden
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise EnvironmentError("OPENROUTER_API_KEY nicht gefunden!")

# Verfügbare Modelle abfragen
def get_models():
    response = requests.get(
        "https://openrouter.ai/api/v1/models",
        headers={
            "Authorization": f"Bearer {api_key}"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        # Debug: Was liefert die API wirklich?
        if isinstance(result, dict):
            if "data" in result:
                return [model["id"] for model in result["data"]]
            else:
                # falls die API direkt eine Liste liefert oder das Ergebnis anders strukturiert ist
                return [model["id"] for model in result]  # falls result eine Liste ist
        else:
            raise Exception(f"Unerwartetes Format: {type(result)}\n{result}")
    else:
        raise Exception(f"Fehler beim Abrufen der Modelle: {response.status_code}\n{response.text}")

# Chat mit Claude-3-Opus führen
def chat_with_claude(prompt, model="anthropic/claude-sonnet-4"):
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://deinprojekt.local",  # Optional
            "X-Title": "Testskript mit Claude"            # Optional
        },
        data=json.dumps({
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        })
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Trying model: {model}")
    
    try:
        response_data = response.json()
        
        if response.status_code == 200:
            if "choices" in response_data and len(response_data["choices"]) > 0:
                return response_data["choices"][0]["message"]["content"]
            else:
                raise Exception(f"Unexpected response format: {response_data}")
        else:
            # Check if it's an overloaded error
            if "error" in response_data and "message" in response_data["error"]:
                if "Overloaded" in response_data["error"]["message"]:
                    raise Exception(f"Model {model} is currently overloaded. Try a different model.")
            raise Exception(f"API Error: {response.status_code}\n{response_data}")
    except json.JSONDecodeError as e:
        print(f"Raw response text: {response.text}")
        raise Exception(f"Failed to parse JSON response: {e}")

def try_multiple_models(prompt):
    """Try multiple models in case one is overloaded"""
    models_to_try = [
        "anthropic/claude-sonnet-4",
        "anthropic/claude-3-5-sonnet",
        "anthropic/claude-3-haiku",
        "openai/gpt-4o",
        "openai/gpt-4o-mini"
    ]
    
    for model in models_to_try:
        try:
            print(f"\nTrying model: {model}")
            result = chat_with_claude(prompt, model)
            print(f"Success with {model}!")
            return result
        except Exception as e:
            print(f"Failed with {model}: {str(e)}")
            continue
    
    raise Exception("All models failed. Please try again later.")

# Beispielnutzung
if __name__ == "__main__":
    #print("Verfügbare Modelle:")
    #print(get_models())

    print("\nAntwort von Claude:")
    try:
        result = try_multiple_models("9.11 and 9.9, which one is larger?")
        print(f"\nAnswer: {result}")
    except Exception as e:
        print(f"Error: {e}")

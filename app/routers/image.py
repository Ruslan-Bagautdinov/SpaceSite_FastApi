from fastapi import (FastAPI,
                     HTTPException,
                     APIRouter)
import requests

app = FastAPI()

# Replace 'X_RAPIDAPI_KEY' with your actual RapidAPI key
RAPIDAPI_KEY = "X_RAPIDAPI_KEY"


@app.get("/generate_image/")
async def generate_image(prompt: str):
    url = "https://ai-image-generator3.p.rapidapi.com/generate"
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "ai-image-generator3.p.rapidapi.com"
    }
    payload = {
        "prompt": prompt,
        "page": 1
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        return response.json()
    except requests.exceptions.HTTPError as errh:
        raise HTTPException(status_code=400, detail="HTTP error occurred: " + str(errh))
    except requests.exceptions.ConnectionError as errc:
        raise HTTPException(status_code=500, detail="Error Connecting: " + str(errc))
    except requests.exceptions.Timeout as errt:
        raise HTTPException(status_code=500, detail="Timeout Error: " + str(errt))
    except requests.exceptions.RequestException as err:
        raise HTTPException(status_code=500, detail="An error occurred: " + str(err))

# Run the server with: uvicorn main:app --reload
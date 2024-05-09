from fastapi import UploadFile
import aiofiles
import base64
import httpx
import random

from app.config import UNSPLASH_ACCESS_KEY


async def save_upload_file(upload_file: UploadFile, destination: str):
    async with aiofiles.open(destination, 'wb') as out_file:
        while content := await upload_file.read(1024):  # Read file in chunks
            await out_file.write(content)


async def read_and_encode_photo(photo_path):
    try:
        async with aiofiles.open(photo_path, 'rb') as photo_file:
            photo_data = await photo_file.read()
            photo_base64 = base64.b64encode(photo_data).decode('utf-8')
            return photo_base64
    except FileNotFoundError:
        print(f"File not found: {photo_path}")
        return None
    except Exception as e:
        print(f"Error encoding photo {photo_path}: {e}")
        return None


async def load_unsplash_photo(query: str = "cosmos") -> str | None:
    url = "https://api.unsplash.com/search/photos"
    headers = {
        "Accept-Version": "v1",
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }
    params = {
        "query": query,
        "orientation": "landscape",
        "per_page": 30  # Fetch up to 30 photos per search
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
            data = response.json()

            # Check if there are any results
            if data.get('results'):
                # Get a random index within the range of the results list length
                random_index = random.randint(0, len(data['results']) - 1)
                # Get the URL of a random result
                image_url = data['results'][random_index]['urls']['regular']
            else:
                image_url = None
        except httpx.HTTPStatusError as errh:
            print("HTTP error occurred:", errh)
            image_url = None
        except httpx.RequestError as err:
            print("An error occurred:", err)
            image_url = None

    return image_url

import base64
import os
import random
import tempfile
from uuid import uuid4

import aiofiles
import httpx
from PIL import Image
from fastapi import (UploadFile,
                     Request,
                     status
                     )
from fastapi.responses import RedirectResponse
from loguru import logger

from app.config import UNSPLASH_ACCESS_KEY


async def save_file_with_uuid(upload_file: UploadFile, destination_dir: str):
    if upload_file is None:
        logger.debug("No file provided.")
        return None

    _, ext = os.path.splitext(upload_file.filename)
    uuid_filename = f"{uuid4()}{ext}"
    destination = os.path.join(destination_dir, uuid_filename)

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_filename = temp_file.name
        async with aiofiles.open(temp_filename, 'wb') as out_file:
            while content := await upload_file.read(1024):  # Read file in chunks
                await out_file.write(content)

    try:
        img = Image.open(temp_filename)
        width, height = img.size

        if max(width, height) > 1024:
            aspect_ratio = min(1024 / width, 1024 / height)
            new_size = (int(width * aspect_ratio), int(height * aspect_ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        img.save(destination)
    finally:
        os.remove(temp_filename)

    return destination


async def read_and_encode_photo(photo_path):
    try:
        async with aiofiles.open(photo_path, 'rb') as photo_file:
            photo_data = await photo_file.read()
            photo_base64 = base64.b64encode(photo_data).decode('utf-8')
            return photo_base64
    except FileNotFoundError:
        logger.debug(f"File not found: {photo_path}")
        return None
    except Exception as e:
        logger.debug(f"Error encoding photo {photo_path}: {e}")
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
        "per_page": 50
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get('results'):
                random_index = random.randint(0, len(data['results']) - 1)
                image_url = data['results'][random_index]['urls']['regular']
            else:
                image_url = None
        except httpx.HTTPStatusError as errh:
            logger.debug("HTTP error occurred:", errh)
            image_url = None
        except httpx.RequestError as err:
            logger.debug("An error occurred:", err)
            image_url = None

    return image_url


async def redirect_with_message(request: Request,
                                message_class: str,
                                message_icon: str,
                                message_text: str,
                                endpoint: str = None,
                                logout: bool = False):
    top_message = {
        "class": message_class,
        "icon": message_icon,
        "text": message_text
    }
    request.session['top_message'] = top_message
    if logout:
        endpoint = "/logout/?login=True"
    response = RedirectResponse(url=endpoint,
                                status_code=status.HTTP_302_FOUND)
    return response

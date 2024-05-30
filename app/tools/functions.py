from fastapi import (UploadFile,
                     Request,
                     status
                     )
from fastapi.responses import RedirectResponse

from datetime import datetime
from time import sleep
from PIL import Image
import tempfile
import subprocess
import aiofiles
import base64
import httpx
import random
import os

from app.config import UNSPLASH_ACCESS_KEY, BASE_DIR


def perform_migrations():

    alembic_path = os.path.join(BASE_DIR, 'alembic')
    if os.path.exists(alembic_path):
        print("Alembic directory found")
    else:
        sleep(15)
        command = ['alembic', 'init', '-t', 'async', 'alembic']
        subprocess.run(command)
        print('Alembic initialized')

    version_path = os.path.join(BASE_DIR, 'alembic', 'versions')
    if os.listdir(version_path):
        print("Versions directory not empty")
    else:
        print("Versions directory empty")
        sleep(20)
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        print('Alembic revision started...')
        subprocess.run(['alembic', 'revision', '--autogenerate', '-m', now])
        print('Alembic revision finished')
        sleep(10)
        print('Alembic migration started...')
        subprocess.run(['alembic', 'upgrade', 'head'])
        print('Alembic migration finished')


def resize_image(input_image_path, size_limit):
    with Image.open(input_image_path) as img:
        if max(img.size) > size_limit:
            aspect_ratio = min(size_limit / img.size[0], size_limit / img.size[1])
            new_size = (int(img.size[0] * aspect_ratio), int(img.size[1] * aspect_ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        return img


async def save_upload_file(upload_file: UploadFile, destination: str):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_filename = temp_file.name
        async with aiofiles.open(temp_filename, 'wb') as out_file:
            while content := await upload_file.read(1024):  # Read file in chunks
                await out_file.write(content)

    resized_image = resize_image(temp_filename, 1024)
    resized_image.save(destination)
    resized_image.close()
    os.unlink(temp_filename)


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
            print("HTTP error occurred:", errh)
            image_url = None
        except httpx.RequestError as err:
            print("An error occurred:", err)
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

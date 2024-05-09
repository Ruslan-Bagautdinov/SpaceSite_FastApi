from fastapi import UploadFile
import aiofiles
import base64


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

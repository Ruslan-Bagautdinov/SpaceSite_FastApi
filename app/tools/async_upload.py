import aiofiles
from fastapi import UploadFile


async def save_upload_file(upload_file: UploadFile, destination: str):
    async with aiofiles.open(destination, 'wb') as out_file:
        while content := await upload_file.read(1024):  # Read file in chunks
            await out_file.write(content)

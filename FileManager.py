import io
import discord
import requests
from typing import List



class FileManager:
    CHUNK = 25 * 1024 ** 2 # 25 MB
    IDO = 2

    def __init__(self):
        pass

    def split_file_data(self, file_data: bytes) -> List[io.BytesIO]:
        return [io.BytesIO(file_data[pos: pos + self.CHUNK]) for pos in range(0, len(file_data), self.CHUNK)]

    def assemble_file(self, sorted_reply_messages: List[discord.message.Message]) -> None:
        file_data = b""
        for replay in sorted_reply_messages:
            chunk_link = replay.attachments[0].url
            chunk_data = requests.get(chunk_link).content
            file_data += chunk_data

        with open("recreated-file", "wb") as file:
            file.write(file_data)


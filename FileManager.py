import io
import os
import base64
from typing import List


class FileManager:
    CHUNK = 25 * 1024 ** 2 # 25 MB

    def __init__(self):
        pass

    def split_file_data(self, file_data: bytes) -> List[io.BytesIO]:
        return [io.BytesIO(file_data[pos: pos + self.CHUNK]) for pos in range(0, len(file_data), self.CHUNK)]

    def assemble_file(self, file_chunk_list: List[str]) -> str:
        return "".join(file_chunk_list)


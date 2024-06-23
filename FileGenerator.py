import os

def generate_file(size_mb):
    # Convert size from MB to bytes
    size_bytes = size_mb * 1024 * 1024
    data = b'0' * size_bytes  # This generates a file filled with zeros
    file_name = f"{size_mb}MB.bin"
    with open(file_name, 'wb') as file:
        file.write(data)

    print(f"File '{file_name}' generated successfully with size {size_mb} MB.")

generate_file(70)
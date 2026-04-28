def save_file(file_path: str, content):
    with open(file_path, "wb") as f:
        f.write(content)
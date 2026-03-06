import os

def lister(folder: str, format: str):
    files_dir = os.path.join(os.path.dirname(__file__), folder)
    files = sorted([
        filename
        for filename in os.listdir(files_dir)
        if filename.lower().endswith(format)
    ])
    return files
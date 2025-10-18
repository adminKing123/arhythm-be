from config import CONFIG

def get_download_url(file_path):
    return f'{CONFIG["MAIN_SRC_URL"]}{file_path}'
import re
import requests
import json
import os
import hashlib

from  concurrent.futures import ThreadPoolExecutor
from logging import Logger
from datetime import datetime
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError, Timeout, ConnectionError

ARCHIVE_PAGE_URL = 'https://xkcd.com/archive/'
COMIC_BASE_URL = 'https://imgs.xkcd.com/comics/'
URL_API = ['https://c.xkcd.com/api-0/jsonp/comic/', '']
DIRECTORY = 'comics'
HEADERS = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}
counts = {'.png': 0, '.jpg': 0, '.gif': 0, 'other': 0, 'total': 0}

def _request_img_from_api( comic_id:int) -> requests.models.Response:
    if comic_id % 100 == 0:
        print(comic_id)
    api_response = requests.get(URL_API[0] + str(comic_id) + URL_API[1] ,timeout=10, headers=HEADERS)
    if api_response.status_code != 200:
        print(f'[Warning] Error {api_response.status_code} in API request from comic id {comic_id}')
        return None

    comic_img_url = json.loads(api_response.content)['img']

    img_response = requests.get(comic_img_url ,timeout=10, headers=HEADERS)

    if img_response.status_code != 200:
        print(f'[Warning] Error {img_response.status_code} in IMG request from comic id {comic_id}')
        return None
    if img_response.content.startswith(b'<html>'):
        print(f'[Warning] Error comic id {comic_id} não é imagem')
    extension = comic_img_url[-4:]
    counts[f'{extension}'] += 1
    counts['total'] += 1
    _save_img_file_in_disk(f'{comic_id}.{extension}', img_response.content)

def _save_img_file_in_disk( file_name: str, file_content: bytes) -> bool:
    
    try:
        with open(f'{DIRECTORY}/{file_name}', 'wb') as img_file:
            img_file.write(file_content)
        return True 
    except PermissionError:
        print(f'Error ao salvar id:{file_name}')

with ThreadPoolExecutor(max_workers=4) as executor:
    executor.map(_request_img_from_api, range(1, 2672))
print(counts)

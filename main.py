import requests
from pprint import pprint


# def get_ya_token():
#     with open('ya_token.txt', 'r') as file:
#         return file.read().strip()


def get_vk_token():
    with open('vk_token.txt', 'r') as file:
        return file.read().strip()


class VkApiClient:
    def __init__(self, vktoken, api_version):
        self.vktoken = vktoken
        self.api_version = api_version

    def get_photos(self, owner_id):
        url = 'https://api.vk.com/method/photos.get'
        photo_links = []
        params = {
            'owner_id': owner_id,
            'album_id': 'profile',
            'extended': '1',
            'access_token': self.vktoken,
            'v': self.api_version
            }
        response = requests.get(url, params=params)
        #pprint(response.json())
        if not response.ok:
            print(f'Ошибка! Статус ответа: {response.status_code}')
            return False
        if not response.json().get('response').get('items'):
            print(f'Ошибка! У этого пользователя нет фотографий профиля!')
            return False

        photos_downloaded = []
        for item in response.json().get('response').get('items'):
            picture = requests.get(item.get('sizes')[-1].get('url'))
            name = str(item.get('likes').get('count'))
            for photo in photos_downloaded:
                if f'{name}.jpg' == photo['file_name']:
                    name += str(item.get('date'))
            with open(f'{name}.jpg', 'wb') as file:
                file.write(picture.content)
            photo_info = {
                "file_name": f"{name}.jpg",
                "size": f"{item.get('sizes')[-1].get('type')}"
            }
            photos_downloaded.append(photo_info)
        pprint(photos_downloaded)


class YaUploader:
    files_url = 'https://cloud-api.yandex.net/v1/disk/resources/files'
    upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'

    def __init__(self, yatoken):
        self.yatoken = yatoken

    @property
    def header(self):
        return self.get_headers()

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.yatoken}'
        }

    def get_upload_link(self, file_path):
        params = {'path': file_path, 'overwrite': 'true'}
        response = requests.get(self.upload_url, params=params, headers=self.header)
        return response.json()

    def upload(self, file_path):
        href = self.get_upload_link(file_path).get('href')
        if not href:
            print('Не удалось получить ссылку для загрузки')
            return
        with open(file_path, 'rb') as file:
            response = requests.put(href, data=file)
            if response.status_code == 201:
                print('Файл загружен')
                return True
            else:
                print(f'Ошибка, файл не загружен. Код ответа - {response.status_code}')
                return False


user_id = input('Введите ID пользователя ВКонтакте: ')
vk_client = VkApiClient(vktoken=get_vk_token(), api_version="5.131")
result = vk_client.get_photos(user_id)


# # path_to_file = input('Введите путь к файлу: ')
# uploader = YaUploader(yatoken=input('Введите токен для Яндекс Диска: '))
# # result = uploader.upload(path_to_file)



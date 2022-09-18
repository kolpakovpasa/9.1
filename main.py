import requests
import json
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
        params = {
            'owner_id': owner_id,
            'album_id': 'profile',
            'extended': '1',
            'photo_sizes': '1',
            'access_token': self.vktoken,
            'v': self.api_version
            }
        response = requests.get(url, params=params)
        if not response.ok:
            print(f'Ошибка! Статус ответа: {response.status_code}')
            return False
        if not response.json().get('response').get('items'):
            print(f'Ошибка! У этого пользователя нет фотографий профиля!')
            return False
        pprint(response.json())
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
                "size": item.get('sizes')[-1].get('type'),
            }
            photos_downloaded.append(photo_info)

        json_data = json.dumps(photos_downloaded, indent=4)
        with open('data.json', 'w') as file:
            file.write(json_data)

        return photos_downloaded


class YaClient:
    base_url = 'https://cloud-api.yandex.net/v1/disk/'

    def __init__(self, yatoken):
        self.yatoken = yatoken

    @property
    def header(self):
        return self.get_headers()

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.yatoken}',
            'Accept': 'application/json'
        }

    def get_upload_link(self, file_path):
        params = {'path': file_path, 'overwrite': 'true'}
        response = requests.get(f'{self.base_url}resources/upload', params=params, headers=self.header)
        return response.json()

    def upload(self, file_path):
        href = self.get_upload_link(f'photos/{file_path}').get('href')
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

    def create_folder(self, folder_title):
        params = {'path': folder_title}
        response = requests.put(f'{self.base_url}resources', params=params, headers=self.header)
        if response.status_code == 201:
            print('Папка создана')
        elif response.status_code == 409:
            print('Ошибка! Папка с таким именем уже есть')
        else:
            print(f'Ошибка! Не удалось создать папку. Код ответа {response.status_code}')


def main():
    user_id = input('Введите ID пользователя ВКонтакте: ')
    vk_client = VkApiClient(vktoken=get_vk_token(), api_version="5.131")
    result = vk_client.get_photos(user_id)
    pprint(result)
    ya_token = input('Введите токен для Яндекс Диска: ')
    downloader = YaClient(yatoken=ya_token)
    downloader.create_folder('photos')
    for picture in result:
        downloader.upload(picture.get('file_name'))


if __name__ == '__main__':
    main()





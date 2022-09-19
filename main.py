import requests
import json


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
        print('Получаю информацию о фото...')
        response = requests.get(url, params=params)
        if 'error' in response.json():
            print(f"Ошибка! Статус ответа: {response.json().get('error').get('error_msg')}")
            return False
        if not response.ok:
            print(f'Ошибка! Статус ответа: {response.status_code}')
            return False
        if not response.json().get('response').get('items'):
            print(f'Ошибка! У этого пользователя нет фотографий профиля!')
            return False
        number_of_photos = len(response.json().get('response').get('items'))
        print(f'У пользователя {number_of_photos} фото профиля')
        photos_downloaded = []
        print('Загружаю фото...')
        photo_count = 0
        for item in response.json().get('response').get('items'):
            photo_count += 1
            sizes_sorted = sorted(item.get('sizes'), key=lambda x: x['height'])
            picture = requests.get(sizes_sorted[-1].get('url'))
            name = str(item.get('likes').get('count'))
            for photo in photos_downloaded:
                if f'{name}.jpg' == photo['file_name']:
                    name = f"{name}-{item.get('date')}"
            with open(f'{name}.jpg', 'wb') as file:
                file.write(picture.content)
            photo_info = {
                "file_name": f"{name}.jpg",
                "size": sizes_sorted[-1].get('type'),
                "height": sizes_sorted[-1].get('height')
            }
            photos_downloaded.append(photo_info)
            print(f'Загружено фото {photo_count} из {number_of_photos} под именем {name}.jpg')

        photos_downloaded_strip_height = [{
                'file_name': dct['file_name'],
                'size': dct['size']
            } for dct in photos_downloaded]
        json_data = json.dumps(photos_downloaded_strip_height, indent=4)
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
        print('Получаю ссылку для загрузки файла на Яндекс.Диск...', end=' ')
        return response.json()

    def upload(self, folder_title, file_name):
        href = self.get_upload_link(f'{folder_title}/{file_name}').get('href')
        if not href:
            print('Не удалось получить ссылку для загрузки')
            return
        print('Ссылка получена!')
        with open(file_name, 'rb') as file:
            response = requests.put(href, data=file)
            if response.status_code == 201:
                print(f'Файл {file_name} загружен на Яндекс.Диск в папку {folder_title}')
                return True
            else:
                print(f'Ошибка, файл не загружен. Код ответа - {response.status_code}')
                return False

    def create_folder(self, folder_title='photos'):
        params = {'path': folder_title}
        response = requests.put(f'{self.base_url}resources', params=params, headers=self.header)
        if response.status_code == 201:
            print(f'Папка {folder_title} для загрузки фото на Яндекс.Диск создана')
        elif response.status_code == 409:
            print('Ошибка! Папка с таким именем уже есть')
        else:
            print(f'Ошибка! Не удалось создать папку. Код ответа {response.status_code}')
        return folder_title


def get_top_n_pictures(list_of_photos, n=3):
    if len(list_of_photos) > n:
        return sorted(list_of_photos, key=lambda x: x['height'], reverse=True)[:n]
    else:
        return sorted(list_of_photos, key=lambda x: x['height'], reverse=True)


def main():
    user_id = input('Введите ID пользователя ВКонтакте: ')
    vk_client = VkApiClient(vktoken=get_vk_token(), api_version="5.131")
    photos_downloaded = vk_client.get_photos(user_id)
    if not photos_downloaded:
        return
    ya_token = input('Введите токен для Яндекс Диска: ')
    downloader = YaClient(yatoken=ya_token)
    folder_destination = downloader.create_folder()
    download_count = 0
    for picture in get_top_n_pictures(photos_downloaded):
        download_count += 1
        print(f'Загружаю на Яндекс.Диск файл {download_count} из {len(get_top_n_pictures(photos_downloaded))}')
        downloader.upload(folder_destination, picture.get('file_name'))
    print(f'Загрузка {len(get_top_n_pictures(photos_downloaded))} файлов выполнена')


if __name__ == '__main__':
    main()





import requests


class BarcodeData:
    BASE_URL = 'https://barcode.monster/api/'

    @classmethod
    def get_barcode(cls, data):
        try:
            r = requests.get(f"{cls.BASE_URL}{data}")
            r.raise_for_status()
        except requests.exceptions.RequestException as err:
            print(err.request, err.response)
        else:
            print(r.json())


if __name__ == '__main__':
    BarcodeData.get_barcode('027000520055')

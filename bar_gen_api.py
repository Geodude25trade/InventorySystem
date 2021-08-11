import requests
from enum import Enum
from os import makedirs, path


class BarcodeGenerator:
    BASE_URL = 'http://www.barcode-generator.org/zint/api.php'

    class ImageType(Enum):
        PNG = 0
        SVG = 1
        EPS = 2

        def __str__(self):
            return str(self.value)

    class ImageSize(Enum):
        SMALL = 's'
        MEDIUM = 'm'
        LARGE = 'l'

        def __str__(self):
            return str(self.value)

    class CodeType(Enum):
        QR_CODE = 0
        CODE_11 = 1
        STANDARD_2OF5 = 2
        INTERLEAVED_2OF5 = 3
        IATA_2OF5 = 4
        DATA_LOGIC = 6
        INDUSTRIAL_2OF5 = 7
        EXTENDED_CODE_39 = 9
        EAN = 13
        GS1_128 = 16
        EAN_128 = 16
        CODE_128_STANDARD = 20
        LEITCODE = 21
        IDENTCODE = 22
        CODE_16K = 23
        CODE_49 = 24
        CODE_93 = 25
        FLATTERMARKEN = 28
        DATABAR_14 = 29
        DATABAR_LIMITED = 30
        DATABAR_EXTENDED = 31
        TELEPEN_ALPHA = 32
        UPC_A = 34
        UPC_E = 37
        CODE_39 = 39
        POSTNET = 40
        MSI_PLESSEY = 47
        FIM = 49
        LOGMARS = 50
        PHARMA_ONE_TRACK = 51
        PZN = 52
        PHARMA_TWO_TRACK = 53
        PDF417 = 55
        PDF417_TRUNCATED = 56
        MAXICODE = 57
        CODE_128_B = 60
        AP_REPLY_PAID = 66
        AP_ROUTING = 67
        AP_REDIRECTION = 68
        ISBN = 69
        RM4SCC = 70
        DATA_MATRIX = 71
        EAN_14 = 72
        NVE_18 = 75
        JAPANESE_POST = 76
        KOREA_POST = 77
        DATABAR_14_STACK = 79
        DATABAR_14_STACK_OMNI = 80
        PLANET = 82
        MICRO_PDF = 84
        UK_PLESSEY = 86
        TELEPEN_NUMERIC = 87
        ITF_14 = 89
        KIX_CODE = 90
        AZTEC_CODE = 92
        MICRO_QR_CODE = 97
        HIBC_CODE_128 = 98
        HIBC_CODE_39 = 99
        HIBS_DATA_MATRIX = 102
        HIBC_QR_CODE = 104
        HIBC_PDF417 = 106
        HIBC_MICROPDF417 = 108
        HIBC_AZTEC_CODE = 112
        AZTEC_RUNES = 128
        CHANNEL_CODE = 140
        CODE_ONE = 141
        GRID_MATRIX = 142

        def __str__(self):
            return str(self.value)

    @classmethod
    def get_barcode(cls, data, code=CodeType.UPC_A, image_type=ImageType.SVG, image_size=ImageSize.MEDIUM):
        directory = path.join('.data', 'barcodes', code.name.lower())
        try:
            r = requests.get(cls.BASE_URL, params={'bc_number': code, 'bc_data': data, 'bc_format': image_type, 'bc_size': image_size})
            r.raise_for_status()
        except requests.exceptions.RequestException as err:
            print(err.request, err.response)
        else:
            with open('.data/barcodes/invalid/invalid.png', 'rb') as file:
                invalid = file.read()
            if invalid == r.content:
                print("Invalid Code")
            else:
                filename = path.join(directory, f'{data}.{image_type.name.lower()}')
                if not path.exists(filename):
                    print(f"Generating Barcode for data: {data}")
                    makedirs(directory, exist_ok=True)
                    with open(filename, 'wb') as file:
                        file.write(r.content)


if __name__ == '__main__':
    BarcodeGenerator.get_barcode('7055260011')

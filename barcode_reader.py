from bar_gen_api import BarcodeGenerator
from gtin import GTIN


def capture_barcodes():
    while True:
        barcode = input()
        print(bytes(barcode, 'utf-8'))
        code_obj = GTIN('51000000118')
        print(tuple(code_obj))
        # BarcodeGenerator.get_barcode(barcode.gcp)


if __name__ == '__main__':
    capture_barcodes()

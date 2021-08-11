from bar_gen_api import BarcodeGenerator
from gtin import GTIN


def capture_barcodes():
    while True:
        barcode = input()
        code_obj = GTIN(barcode)
        print(tuple(code_obj))
        BarcodeGenerator.get_barcode(code_obj.raw)


if __name__ == '__main__':
    capture_barcodes()

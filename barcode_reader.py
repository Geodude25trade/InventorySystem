from bar_gen_api import BarcodeGenerator
from bar_data_api import BarcodeData
from gtin import GTIN


def capture_barcodes():
    while True:
        barcode = input()
        code_obj = GTIN(barcode)
        BarcodeGenerator.get_barcode(code_obj.raw)
        data = BarcodeData.get_barcode(code_obj)
        print(data)


if __name__ == '__main__':
    capture_barcodes()

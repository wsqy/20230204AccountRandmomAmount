from Account.models import BusinessCompany, Buyer, Seller

from openpyxl import Workbook, load_workbook

def open_xlsx(xlsx_file,is_buyer=True):
    workbook = load_workbook(filename=xlsx_file)
    #  获取表格 只有一张表格的时候，可以直接 active
    sheet = workbook.active

    for row in sheet.rows:
        if is_buyer:
            Buyer.objects.create(
                name = row[0].value,
                scope_id = int(row[6].value),
                corporation = row[1].value,
                registered_capital = int(int(row[2].value) * 10000),
                registered_capital_currency = row[3].value,
                registered_province = row[4].value,
                telphone = row[5].value,
                is_activate = True,
                company_id = int(row[9].value),
                mouth_buy_limit = int(row[7].value),
                total_range = str(int(row[8].value))
            )
        else:
            Seller.objects.create(
                name = row[0].value,
                scope_id = int(row[6].value),
                corporation = row[1].value,
                registered_capital = int(int(row[2].value) * 10000),
                registered_capital_currency = row[3].value,
                registered_province = row[4].value,
                telphone = row[5].value,
                is_activate = True,
            )
# open_xlsx('买方-2021.11.10.xlsx')

from Tran.models import Task, TaskBatch, Transaction
from Statistics.models import (DayBuyer, DaySeller, MouthBuyer, MouthSeller,
                                DayCompany, MouthCompany, DaySellerProducts, DayAccount)
from Account.models import Company, Account, Buyer

def delete_statistics():
    DayBuyer.objects.all().delete()
    DaySeller.objects.all().delete()
    MouthBuyer.objects.all().delete()
    MouthSeller.objects.all().delete()
    DayCompany.objects.all().delete()
    MouthCompany.objects.all().delete()
    DaySellerProducts.objects.all().delete()
    DayAccount.objects.all().delete()


def delete_tran():
    Transaction.objects.all().delete()
    TaskBatch.objects.all().delete()
    Task.objects.all().delete()


def vacuum_table():
    from django.db import connection, transaction
    cursor = connection.cursor()

    cursor.execute("vacuum main")
    transaction.commit_unless_managed()

def delete_all():
    delete_statistics()
    delete_tran()
    vacuum_table()

def move_company(old_id, new_id):
    old_company = Company.objects.get(id=old_id)
    new_company = Company.objects.get(id=new_id)
    Account.objects.filter(company=old_company).update(company=new_company)
    Buyer.objects.filter(company=old_company).update(company=new_company)
    old_company.delete()
    



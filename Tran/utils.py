import random
import string

from django.conf import settings 
from django.db.models import Q
from django.core.exceptions import ValidationError

from .models import Task, TaskBatch, Transaction
from Account.models import Buyer, Seller, Account, Products, Company
from Statistics.models import (DayBuyer, DaySeller, MouthBuyer, MouthSeller,
                                DayCompany, MouthCompany, DaySellerProducts, DayAccount)



def random_int(len=5):
    return ''.join(random.sample(string.digits, len))

def random_str(len=6):
    return ''.join(random.sample(string.ascii_letters + string.digits, len))

def get_download_zipfile(instance):
    date_str = instance.date.strftime('%Y-%m-%d')
    filepath = instance.date.strftime(r'/media/baobiao/%Y-%m/%d/')
    
    filename_content = '{}-{}'.format(date_str, instance.file_no)
    return filepath+filename_content+'.zip'

def get_download_excelfile(instance, type='转账文件'):
    date_str = instance.task.date.strftime('%Y-%m-%d')
    filepath = instance.task.date.strftime(r'/media/baobiao/%Y-%m/%d/')
    
    filename_content = '{}-{}'.format(date_str, instance.task.file_no)
    return '{}{}-{}-{}.xlsx'.format(filepath, filename_content, type, instance.num)

def taskbatch_add_one(task, _num):
    corporation = task.corporation

    nums = 0
    while True:
        if nums > 50:
            raise ValidationError('批次的笔数、单笔金额范围、任务金额范围检查下！！！试了50次都不能找到匹配的任务设计') 
        nums += 1
        
        batch_num=random.randint(task.batch_num_min, task.batch_num_max)
        if task.amount_total_min >= 2500:
            batch_num = max(5, batch_num)
        
        limit_min = batch_num * ( task.danbi_min or settings.DEFAULT_TRAN_MIN_AMOUNT)
        limit_max = batch_num * ( task.danbi_max or settings.DEFAULT_TRAN_MAX_AMOUNT)
        fin_total_min = max(task.amount_total_min, limit_min)
        fin_total_max = min(task.amount_total_max, limit_max)
        
        print('-----  ------')
        print("---- 本批次数量为: %s-----" % (batch_num))
        print("---- 根据单笔最低限额测算下限是: %s -----" % limit_min)
        print("---- 根据单笔最高限额测算上限是: %s -----" % limit_max)
        print("---- 综合任务金额，测算下限是: %s -----" % fin_total_min)
        print("---- 综合任务金额，测算上限是: %s -----" % fin_total_max)
        print("---- -----")
        
        if fin_total_max < fin_total_min:
            continue
        else:
            amount_total=random.randint(fin_total_min, fin_total_max)

        print("---- amount_total-----")
        print(amount_total)
        print("---- -----")
        if amount_total >= 2500:
            batch_num = max(5, batch_num)
            print("---- 更新后的本批次数量为: %s-----" % (batch_num))
        print('--批次总金额:%s ,批次总个数:%s ----'% (amount_total, batch_num))
        break
    return TaskBatch(task=task, num=_num, batch_total=batch_num, amount_total=amount_total)

def hongbao(_min=settings.DEFAULT_TRAN_MIN_AMOUNT, _max=settings.DEFAULT_TRAN_MAX_AMOUNT, total=0, num=0):
    print('红包算法设定条件: 最小值: %s, 最大值: %s, 总数: %s, 总个数: %s' % (_min, _max, total, num))
    if _min * num > total:
        raise ValidationError('设定条件有问题, 无法匹配: 最小值: %s, 最大值: %s, 总数: %s, 总个数: %s' % (_min, _max, total, num))
    if _max * num < total:
        raise ValidationError('设定条件有问题, 无法匹配: 最大值: %s, 最大值: %s, 总数: %s, 总个数: %s' % (_min, _max, total, num))
    hongbao_list = []
    if num < 1:
        return hongbao_list
    if num == 1:
        hongbao_list.append(total)
        return hongbao_list
    i = 1
    totalMoney = total
    while(i < num):
        __max = max(min(totalMoney - _min*(num-i), _max, int(totalMoney/i * 2)), _min)
        monney = random.randint(_min, __max)
        totalMoney = totalMoney - monney
        hongbao_list.append(monney)
        i += 1
    hongbao_list.append(totalMoney)
    hongbao_list.sort()
    while True >= 0:
        if hongbao_list[0] < _min:
            chazhi = _min + random.randint(1, hongbao_list[0])
            hongbao_list[0] += chazhi
            hongbao_list[-1] -= chazhi
            hongbao_list.sort()
            continue
        if hongbao_list[-1] > _max:
            chazhi = hongbao_list[-1] - _max + random.randint(1, hongbao_list[0])
            hongbao_list[0] += chazhi
            hongbao_list[-1] -= chazhi
            hongbao_list.sort()
            continue
        break
    return hongbao_list

def get_total_range(amount):
    if amount > 500:
        return '3'
    elif amount < 200:
        return '1'
    return '2'

def get_products(total_range, scope):
    return Products.objects.filter(is_activate=True, total_range__contains=total_range, scope=scope).order_by('?').first()

def transaction_add_list(instance):
    min_danbi_amount = instance.task.danbi_min or settings.DEFAULT_TRAN_MIN_AMOUNT
    max_danbi_amount = instance.task.danbi_max or settings.DEFAULT_TRAN_MAX_AMOUNT
 
    hongbao_list = hongbao(min_danbi_amount, max_danbi_amount, instance.amount_total, instance.batch_total)
    print('--获取到红包金额列表: %s ----'% (hongbao_list, ))
    if (max(hongbao_list) > settings.DEFAULT_TRAN_MAX_AMOUNT) or (min(hongbao_list) < settings.DEFAULT_TRAN_MIN_AMOUNT):
        raise ValidationError('设定条件有问题,重新生成一下任务')
    
    # company_list = get_company_list(instance.task.corporation, num, instance.task.date)
    # print('--本次获取到的公司列表: %s ----'% (company_list, ))
    account_list, hongbao_list = get_account_list(instance, hongbao_list)
    transaction_list = []
    for i, account in enumerate(account_list, 0):
        amount = hongbao_list[i]
        total_range = get_total_range(amount)
        max_try = 0
        while True:
            max_try += 1
            if max_try > 100:
                raise ValidationError('设定条件有问题, 重新生成一下任务,如果还不行就删除一些任务或者增加买方吧')
            buyer = get_buyer(total_range, instance.task.date, account.company)
            print('--本次买方: %s ----'% (buyer, ))
            
            if not buyer:
                continue
            scope = buyer.scope
            products = get_products(total_range, scope)
            print('--本次商品列表: %s ----'% (products, ))
            if not products:
                continue

            seller = get_seller(scope)
            print('--本次卖方: %s ----'% (seller, ))
            if not seller:
                continue
            price = get_price(seller, products)
            quantity = int(amount*10000/0.3/price)
            for ii in range(10):
                real_amount = round(quantity * price *0.3 / 10000, 0)
                if real_amount ==  amount:
                    break
                elif real_amount <  amount:
                    quantity += 1
                elif real_amount >  amount:
                    quantity -= 0.5
                    break

            transaction = Transaction(date=instance.task.date, account = account,
                                        buyer=buyer, seller=seller,
                                        amount=amount, task_batch=instance,
                                        price=price, products=products,
                                        total_range=total_range, quantity=quantity,
                                        tran_tatal=int(price*quantity),
                                        order_no=gen_order_no(buyer, instance, i)
            )
            transaction.save()    
            transaction_list.append(transaction)
            print('--添加完成一条记录: %s ----'% (instance.num, ))
            break
    return transaction_list

def transaction_add_statistics(transaction):
    daybuyer = DayBuyer.objects.select_for_update().get_or_create(buyer=transaction.buyer, date=transaction.date)[0]
    daybuyer.amount_total += transaction.amount
    daybuyer.save()

    dayseller = DaySeller.objects.select_for_update().get_or_create(seller=transaction.seller, date=transaction.date)[0]
    dayseller.amount_total += transaction.amount
    dayseller.save()

    daycompany = DayCompany.objects.select_for_update().get_or_create(company=transaction.buyer.company, date=transaction.date)[0]
    daycompany.amount_total += transaction.amount
    daycompany.save()

    dayaccount = DayAccount.objects.select_for_update().get_or_create(account=transaction.account, date=transaction.date)[0]
    dayaccount.amount_total += transaction.amount
    dayaccount.save()
    
    mouthbuyer = MouthBuyer.objects.select_for_update().get_or_create(buyer=transaction.buyer, date=transaction.date.strftime("%Y年%m月"))[0]
    mouthbuyer.amount_total += transaction.amount
    mouthbuyer.save()

    mouthseller = MouthSeller.objects.select_for_update().get_or_create(seller=transaction.seller, date=transaction.date.strftime("%Y年%m月"))[0]
    mouthseller.amount_total += transaction.amount
    mouthseller.save()
    
    mouthcompany = MouthCompany.objects.select_for_update().get_or_create(company=transaction.buyer.company, date=transaction.date.strftime("%Y年%m月"))[0]
    mouthcompany.amount_total += transaction.amount
    mouthcompany.save()

    daysellerproducts = DaySellerProducts.objects.select_for_update().get_or_create(seller=transaction.seller, date=transaction.date, products=transaction.products)[0]
    daysellerproducts.price = transaction.price
    daysellerproducts.quantity += (int(transaction.quantity) * int(daysellerproducts.choice_scale))
    daysellerproducts.save()

def get_price(seller, products):
    try:
        transaction = Transaction.objects.get(seller=seller, products=products)
        return transaction.price
    except Exception as e:
        return random.randint(products.price_min, products.price_max)


def get_buyer(total_range, date, company):
    _year = date.year
    _month = date.month
    for i in range(settings.SEARCH_BUSINESSCOMPANY_LIMIT):
        buyer_list = Buyer.objects.filter(is_activate=True, total_range__icontains=total_range, company=company).order_by('?')[:settings.SEARCH_BUSINESSCOMPANY_PER_LIMIT]
        print('-----buyer_list---' )
        print(buyer_list)
        print('-----buyer_list---' )
        for buyer in buyer_list:
            mouth_total = Transaction.objects.filter(buyer=buyer, total_range=total_range, date__month=_month, date__year=_year).count()
            print('-----买方本月交易量: %s 笔---' % mouth_total)
            if mouth_total < buyer.mouth_buy_limit:
                return buyer


def get_seller(scope):
    return Seller.objects.filter(is_activate=True, scope=scope).order_by('?').first()

def get_company_list(corporation, num, date):
    print('----start----      准备筛选公司列表开始       -----start----')

    print('-- 集团: %s, 总笔数: %s ----' % (corporation.name, num))
    
    # 筛选条件1 交易场所及状态
    _company_list = Company.objects.filter(is_activate=True, corporation=corporation).order_by('?')
    # 筛选条件2 子公司必须存在可用的账户 
    _company_list = [ _company for _company in _company_list if Account.objects.filter(company=_company, is_activate=True).exists()]
    # 筛选条件3 子公司今天限额检查
    company_list = []
    for company in _company_list:
        dayCompanySeller = 0
        daycompany = DayCompany.objects.filter(company=company, date=date)
        if daycompany.count() == 1:
            dayCompanySeller =  daycompany[0].amount_total
        if company.day_max > dayCompanySeller:
            company_list.append(company)
            

    print('-- 随机生成的公司列表: %s ----' % (company_list, ))
    
    max_in = max((num // len(company_list) ) * 2, 1)
    print('-- 子公司最多出现: %s 次 ----' % (max_in, ))
    
    new_company_list = random.sample(company_list * max_in, num)
    print('---end-----      准备筛选公司列表结束       -----end----')
    return new_company_list


def gen_order_no(buyer, instance, no):
    task_id = get_task_randmon_id_list(instance)
    return '{0}{1:%Y%m%d}{2:0>3}{3:0>3}{4:0>3}'.format(buyer.company.company_code, 
                                                        instance.task.date,
                                                        str(task_id),
                                                        str(instance.num)[-3:], 
                                                        str(no+1)[-3:])


def get_task_randmon_id_list(instance):
    str_date = str(instance.task.date)
    today_task_randmon_id_list = settings.TASK_RANDOM_ID_LIST_DICT.get(str_date, None)
    if today_task_randmon_id_list is None:
        today_task_randmon_id_list = [i for i in range(1000)]
    random.shuffle(today_task_randmon_id_list)
    try:
        today_task_randmon_id = today_task_randmon_id_list.pop()
        settings.TASK_RANDOM_ID_LIST_DICT[str_date] = today_task_randmon_id_list
        settings.TASK_TEMP_ID_LIST.append(today_task_randmon_id)
        return today_task_randmon_id
    except Exception as e:
        print('-- 订单号生成失败,  日期: %s,  当前列表: %s,  总列表:%s --' % (str_date,today_task_randmon_id_list, settings.TASK_RANDOM_ID_LIST_DICT))
        raise ValidationError('重启一下服务吧！！！！！！！')


def get_account_list(instance, hongbao_list):
    corporation = instance.task.corporation
    num=instance.batch_total
    budan_model = instance.task.budan_model
    
    print('----start----      准备筛选公司及账号列表开始       -----start----')

    print('-- 集团: %s, 总笔数: %s ----' % (corporation.name, num))
    
    # 筛选条件1 交易场所及状态
    _company_list = Company.objects.filter(is_activate=True, corporation=corporation).order_by('?')
    print("状态符合的公司: %s" % _company_list)
    # 筛选条件2 子公司必须存在可用的账户 
    _company_list = [ _company for _company in _company_list if Account.objects.filter(company=_company, is_activate=True).exists()]
    print("有可用账号的公司: %s" % _company_list)
    # 筛选条件3 子公司今天限额检查
    company_list = []
    for company in _company_list:
        daycompany = DayCompany.objects.filter(company=company, date=instance.task.date)
        if daycompany.count() > 0 and (company.day_max > daycompany[0].amount_total):
            company_list.append(company)
        else:
            company_list.append(company)
    print("限额检查通过的公司: %s" % company_list)
    # 筛选条件4 账户今天限额检查
    account_list = []
    for account in Account.objects.filter(is_activate=True, company__in=company_list).order_by('?'):
        dayAccountSeller = 0
        dayaccount = DayAccount.objects.filter(account=account, date=instance.task.date)
        if dayaccount.count() >0 and (account.day_max >dayaccount[0].amount_total):
            account_list.append(account)
        else:
            account_list.append(account)
    if len(account_list) == 0:
        raise ValidationError('子公司账户无可用, 请检查子公司状态、账号状态、子公司限额、账号限额')
    print("限额检查通过的账号: %s" % account_list)
    if instance.task.budan_model:
        print("补单模式计算")
        len_list_id, new_hongbao_list = move_hongbao_list(hongbao_list, instance.task.budan_danbi_max, instance.task.budan_danbi_min)
        print("len_list_id: %s" % len_list_id)
        print("new_hongbao_list: %s" % new_hongbao_list)
        coudan_account_list = [account for account in account_list if account.bank_sort_name.id in [1,3]]
        if len(coudan_account_list) == 0:
            raise ValidationError("凑单模式下凑单的建行跟恒丰账户一个都没有")
        print("coudan_account_list: %s" % coudan_account_list)
        real_account_list = [account for account in account_list if account.bank_sort_name.id == 2]
        if len(real_account_list) == 0:
            raise ValidationError("凑单模式下凑单的邮储的账户都没有")
        print("real_account_list: %s" % real_account_list)
        
        # 凑单交易
        if len_list_id == 0:
            new_coudan_account_list = []
        else:
            max_in = max((len_list_id // len(coudan_account_list) ) * 2, 1)
            print('-- 账号最多出现: %s 次 ----' % (max_in, ))
            new_coudan_account_list = random.sample(coudan_account_list * max_in, len_list_id)
            print("new_coudan_account_list: %s" % new_coudan_account_list)
        
        # 真实交易
        real_num = num - len_list_id
        max_in = max((real_num // len(real_account_list) ) * 2, 1)
        print('-- 账号最多出现: %s 次 ----' % (max_in, ))
        new_real_account_list = random.sample(real_account_list * max_in, real_num)
        print("new_real_account_list: %s" % new_real_account_list)
        print('---end-----      补单模式筛选公司及账号列表结束       -----end----')
        return new_coudan_account_list+new_real_account_list, new_hongbao_list
        
    else:
        # 非补单模式
        max_in = max((num // len(account_list) ) * 2, 1)
        print('-- 账号最多出现: %s 次 ----' % (max_in, ))
        
        new_account_list = random.sample(account_list * max_in, num)
        print('---end-----      准备筛选公司及账号列表结束       -----end----')
        return new_account_list, hongbao_list

def move_hongbao_list(_list, _max, _min):
    _listid = []
    for i in range(len(_list)):
        if _list[i] > _min and _list[i] < _max:
            _listid = [i]
    len_list_id = min(len(_listid), 2)
    if len(_listid) > 1:
        _list[0], _list[_listid[0]] = _list[_listid[0]], _list[0]
        _list[1], _list[_listid[1]] = _list[_listid[1]], _list[1]
    if len(_listid) == 1:
        _list[0], _list[_listid[0]] = _list[_listid[0]], _list[0]
    return len_list_id, _list
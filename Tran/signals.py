from copy import deepcopy
from django.conf import settings 
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import transaction as shiwu
from django.core.exceptions import ValidationError


from Tran.models import Task, Transaction
from Account.models import Account
from Tran import utils as task_utils
# from Tran.excel import CreateExcel, FujianTranExcel, TranInfoExcel, JiangxiTranExcel
from Tran.excel_order import CreateExcel, FujianTranExcel, TranInfoExcel, JiangxiTranExcel


@shiwu.atomic
@receiver(post_save, sender=Task)
def task_post_save(sender, instance=None, created=False, **kwargs):
    if not created:
        return

    print('------ 任务关键信息 -----------')
    print('任务名称: %s' % instance.name)
    print('所属交易场所: %s' % instance.corporation)
    print('生成批次个数: %s' % instance.batch_total)
    print('单笔范围: %s - %s' % (instance.danbi_min, instance.danbi_max))
    print('每批次笔数范围: %s - %s' % (instance.batch_num_min, instance.batch_num_max))
    print('任务总金额范围: %s - %s' % (instance.amount_total_min, instance.amount_total_max))
    print('是否是补单模式: %s' % instance.budan_model)
    print('补单模式单笔范围: %s - %s' % (instance.budan_danbi_min, instance.budan_danbi_max))
    print('------ 任务关键信息 -----------')
        
    # 事务--创建保存点
    save_id = shiwu.savepoint()

    # 初始化汇总表
    tran_huizong_excel = CreateExcel(instance)
    SubCompanyList = {'闽侯': [],  '高新区': [], '仓山': [], '福州': [], '晋安': [], '鼓楼': [], '台江': [],}
    tran_huizong_excel_dict = {'邮储': deepcopy(SubCompanyList), '恒丰': deepcopy(SubCompanyList), '建行': deepcopy(SubCompanyList), }
    tran_huizong_excel.set_jine_huizong_header(instance.corporation.sub_bankuai, tran_huizong_excel_dict)
    # 初始化转账信息表
    traninfo_excel = TranInfoExcel(instance)
    traninfo_count = 1
    print('--准备为: %s 填充数据 ----' % instance)
    # 清除本次的id暂存区
    settings.TASK_TEMP_ID_LIST = []
    
    # 循环创建批次
    for i in range(1, instance.batch_total+1):
        print(i)
        print('--准备生成第 %i 个交易批次信息----' % i)
        taskbatch = task_utils.taskbatch_add_one(instance, i)
        print('--生成第 %d 个交易批次信息结束----'% i)
        if not taskbatch:
            print('--第 %s 个交易批次信息生成不了 回退并退出----'% i)

            # 事务 -- 回滚到保存点
            shiwu.savepoint_rollback(save_id)
            # 任务失败, 释放id暂存区
            settings.TASK_RANDOM_ID_LIST_DICT[str(instance.date)].extend(settings.TASK_TEMP_ID_LIST)
            print('--当天id列表----'% settings.TASK_RANDOM_ID_LIST_DICT[str(instance.date)])
            raise ValidationError('--第 %s 个交易批次信息生成不了 回退并退出----'% i)

        taskbatch.save()
        # 汇总表插入一条数据
        tran_huizong_excel.insert(taskbatch)

        # 初始化转账记录表
        if instance.corporation.template == '1':
            tran_excel = FujianTranExcel(taskbatch)
        else:
            tran_excel = JiangxiTranExcel(taskbatch)
        print('--准备为第 %s 个批次添加交易记录----'% i)
        
        # 记录新的汇总批次明显
        tran_huizong_excel_dict = {'邮储': deepcopy(SubCompanyList), '恒丰': deepcopy(SubCompanyList), '建行': deepcopy(SubCompanyList), }

        # 循环添加交易
        transaction_list = task_utils.transaction_add_list(taskbatch)
        print('--为第 %s 个批次获取交易记录列表结束----'% i)
        if not transaction_list:
            # 异常退出
            print('--为第 %s 个批次获取交易记录列表失败，回退并退出----'% i)
            traninfo_excel.close()
            tran_huizong_excel.close()

            # 事务 -- 回滚到保存点
            shiwu.savepoint_rollback(save_id)
            # 任务失败, 释放id暂存区
            settings.TASK_RANDOM_ID_LIST_DICT[str(instance.date)].extend(settings.TASK_TEMP_ID_LIST)
            print('--当天id列表----'% settings.TASK_RANDOM_ID_LIST_DICT[str(instance.date)])
            raise ValidationError('--为第 %s 个批次获取交易记录列表失败，回退并退出----'% i)
        
        print('--为第 %s 个批次获取交易记录列表成功， 准备写入数据----'% i)
        for j, transaction in enumerate(transaction_list, 2):
            # transaction.save()
            task_utils.transaction_add_statistics(transaction)
            # # 转账记录表&转账信息表插入一条数据

            tran_excel.insert(j, transaction, show_detail = instance.show_order_info)
            traninfo_count += 1
            traninfo_excel.insert(traninfo_count, transaction)
            
            tran_huizong_excel_dict[str(transaction.account.bank_sort_name)][transaction.buyer.company.sub_comp.name].append(transaction.amount)
            
        print('--第 %s 个交易批次完成， 待写入表格, ----' % i)
        # 写入转账记录表&转账信息表
        tran_excel.close()
        traninfo_excel.close()
        
        # 写汇总金额
        tran_huizong_excel.set_jine_huizong(i, instance.corporation.sub_bankuai, tran_huizong_excel_dict)

    # 写入 汇总表
    tran_huizong_excel.close()
    
    # 创建zip文件
    tran_huizong_excel.creat_zipfile()
    # 设置任务已完成
    instance.status = True
    instance.save()

    # 事务 -- 提交从保存点到当前状态的所有数据库事务操作
    shiwu.savepoint_commit(save_id)
    
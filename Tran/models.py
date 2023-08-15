import time
import random
import string
import datetime

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError

from Account.models import Buyer, Seller, Account, Products, Corporation


def random_str(len=6):
    return ''.join(random.sample(string.ascii_letters + string.digits, len))

class Task(models.Model):
    """
    每日任务表
    """
    corporation =  models.ForeignKey(Corporation, on_delete=models.CASCADE, verbose_name='所属交易场所')
    date = models.DateField(verbose_name='任务日期',  default=timezone.now, )
    name = models.CharField(max_length=40, verbose_name='任务名称', blank=True, null=True,
                            help_text='同一日有多个任务最好设置本次任务名称')
    amount_total_min = models.PositiveIntegerField(verbose_name='每日总金额下限(万元)', help_text='每日总金额下限(万元),建议值2000')
    amount_total_max = models.PositiveIntegerField(verbose_name='每日总金额上限(万元)', help_text='每日总金额上限(万元),建议值4000')
    batch_total = models.PositiveSmallIntegerField(verbose_name='批次数', help_text='每个任务生成的excel转账文件数,建议值15-30')
    batch_num_min = models.PositiveSmallIntegerField(verbose_name='每批次交易笔数下限', help_text='每批次交易笔数下限,建议值3')
    batch_num_max = models.PositiveSmallIntegerField(verbose_name='每批次交易笔数上限',  help_text='每批次交易笔数上限,建议值5')
    status = models.BooleanField(default=False, verbose_name='是否完成')
    remark = models.CharField(max_length=40, verbose_name='交易备注', blank=True, null=True,
                              help_text='该备注信息会自动填充到每笔转账备注中')
    file_no = models.CharField(max_length=6, verbose_name='文件编号', default=random_str)
    show_order_info = models.BooleanField(default=True, verbose_name='订单支付是否显示订单详情', help_text='订单支付是否显示订单详情')
    danbi_min = models.PositiveIntegerField(verbose_name='单笔金额下限(万元)', default=settings.DEFAULT_TRAN_MIN_AMOUNT,
                                            help_text='单笔金额下限(万元), 建议值%s' % settings.DEFAULT_TRAN_MIN_AMOUNT)
    danbi_max = models.PositiveIntegerField(verbose_name='单笔金额上限(万元)',default=settings.DEFAULT_TRAN_MAX_AMOUNT,
                                            help_text='单笔金额上限(万元), 建议值%s' % settings.DEFAULT_TRAN_MAX_AMOUNT)
    budan_model = models.BooleanField(default=False, verbose_name='是否是补单模式', help_text='补单模式将优先使用邮储账号, 恒丰、建行账号将出现不多于2笔')
    budan_danbi_min = models.PositiveIntegerField(verbose_name='补单模式单笔金额下限(万元)', default=settings.DEFAULT_BUDAN_TRAN_MIN_AMOUNT,
                                            help_text='补单模式单笔金额下限(万元), 默认值%s' % settings.DEFAULT_BUDAN_TRAN_MIN_AMOUNT)
    budan_danbi_max = models.PositiveIntegerField(verbose_name='补单模式无效交易单笔金额上限(万元)',default=settings.DEFAULT_BUDAN_TRAN_MAX_AMOUNT,
                                            help_text='补单模式无效交易单笔金额上限(万元), 默认值%s' % settings.DEFAULT_BUDAN_TRAN_MAX_AMOUNT)
    class Meta:
        verbose_name = '每日任务'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name or self.show_date() or self.id
    
    def show_date(self):
        return self.date.strftime('%Y-%m-%d')
    
    def clean(self):
        if self.amount_total_max < self.amount_total_min:
            raise ValidationError({'amount_total_max': '每日总金额上限小于每日总金额下限, 请检查条件'})
        if self.batch_num_max < self.batch_num_min:
            raise ValidationError({'batch_num_max': '批次交易笔数上限小于批次交易笔数下限, 请检查条件'})
        if self.danbi_max < self.danbi_min:
            raise ValidationError({'danbi_max': '单笔金额上限小于单笔金额下限, 请检查条件'})



class TaskBatch(models.Model):
    """
    任务批次表
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name='所属日任务')
    amount_total = models.PositiveIntegerField(verbose_name='批次总金额(万元)')
    batch_total = models.PositiveSmallIntegerField(verbose_name='批次交易笔数',default=3)
    num = models.PositiveSmallIntegerField(verbose_name='批次编号')

    class Meta:
        verbose_name = '任务批次'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{}-{}'.format(self.task, self.num) or self.id
        # return self.id


class Transaction(models.Model):
    """
    交易明细表
    """
    task_batch = models.ForeignKey(TaskBatch, on_delete=models.CASCADE, verbose_name='所属日批次')
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, verbose_name='买方')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, verbose_name='卖方')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='子公司账号')
    date = models.DateField(verbose_name='任务日期', default=timezone.now)
    amount = models.IntegerField(verbose_name='定金金额(万元)',  help_text='交易定金金额')
    total_range = models.CharField(choices=settings.TOTAL_RANGE, max_length=1, verbose_name='总价范围', help_text='总价范围')
    products = models.ForeignKey(Products, on_delete=models.CASCADE, verbose_name='购买商品')
    price = models.PositiveIntegerField(verbose_name='购买单价(元)', help_text='购买单价')
    tran_tatal = models.IntegerField(verbose_name='订货金额(元)',  help_text='交易定金金额')
    quantity = models.FloatField(verbose_name='订货量', help_text='订货量')
    order_no = models.CharField(max_length=30, verbose_name='订单号', blank=True, null=True, help_text='订单号', default='')

    class Meta:
        verbose_name = '交易明细'
        verbose_name_plural = verbose_name

    def __str__(self):
        # return self.id
        return '{}向{}购买{}元'.format(self.buyer,self.seller, self.amount) or self.id

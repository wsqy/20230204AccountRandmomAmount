
from datetime import datetime
from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.

class SubCompany(models.Model):    
    """
    子公司地址表
    """
    name = models.CharField(max_length=40, verbose_name='子公司地址', help_text='子公司地址')
    update_time_one = models.DateTimeField(verbose_name='修改时间', default=datetime.now)

    class Meta:
        verbose_name = '子公司地址表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name or self.id


class BanKuai(models.Model):    
    """
    板块名称表
    """
    name = models.CharField(max_length=40, verbose_name='板块名称', help_text='板块名称')
    update_time_one = models.DateTimeField(verbose_name='修改时间', default=datetime.now)

    class Meta:
        verbose_name = '板块名称表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name or self.id

class Corporation(models.Model):    
    """
    交易场所表
    """
    TEMPLATE = (
        ('1', '福建模板'),
        ('2', '江西模板'),
    )
    name = models.CharField(max_length=40, verbose_name='交易场所名称',help_text='交易场所')
    template = models.CharField(max_length=2, verbose_name='转账文件模板', choices=TEMPLATE)
    sub_bankuai = models.ForeignKey(BanKuai, on_delete=models.CASCADE, verbose_name='板块')
    is_activate = models.BooleanField(default=True, verbose_name='状态', help_text='该交易场所是否继续使用')

    class Meta:
        verbose_name = '交易场所'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name or self.id

class Bank(models.Model):    
    """
    银行表
    """
    name = models.CharField(max_length=40, verbose_name='银行简称', help_text='银行简称')
    update_time_one = models.DateTimeField(verbose_name='修改时间', default=datetime.now)

    class Meta:
        verbose_name = '银行表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name or self.id
    
class Company(models.Model):
    """
    集团子公司表
    """
    name = models.CharField(max_length=40, verbose_name='子公司名称', help_text='子公司名称')
    corporation = models.ForeignKey(Corporation, on_delete=models.CASCADE, verbose_name='所属交易场所', 
                                    help_text='子公司所属集团')
    sub_comp = models.ForeignKey(SubCompany, on_delete=models.CASCADE, verbose_name='子公司地址')
    is_activate = models.BooleanField(default=True, verbose_name='状态', help_text='该公司是否继续使用')
    company_code = models.CharField(max_length=10, verbose_name='子公司代码', help_text='子公司代码', default='')
    day_max = models.IntegerField(verbose_name='每日交易上限', default=1000000, help_text='每日交易上限(默认不限制-100亿;单位万元)')

    class Meta:
        verbose_name = '集团子公司'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sort_name
    
    @property
    def sort_name(self):
        return '%s%s' % (self.corporation.sub_bankuai, self.sub_comp)


class BusinessScope(models.Model):
    """
    经营分类
    """
    name = models.CharField(max_length=40, verbose_name='经营分类', help_text='经营分类')
    is_activate = models.BooleanField(verbose_name='状态', default=True, help_text='该分类是否继续使用')

    class Meta:
        verbose_name = '经营分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name or self.id


class Products(models.Model):
    """
    商品表
    """
    scope = models.ForeignKey(BusinessScope, on_delete=models.CASCADE, verbose_name='分类', help_text='大的经营分类')
    name = models.CharField(max_length=40, verbose_name='商品名称', help_text='商品名称')
    type = models.CharField(max_length=511, verbose_name='商品型号', help_text='商品型号')
    price_min = models.PositiveIntegerField(verbose_name='单价下限', help_text='单价下限(元)')
    price_max = models.PositiveIntegerField(verbose_name='单价上限', help_text='单价上限(元)')
    unit = models.CharField(max_length=40, verbose_name='计量单位', help_text='计量单位')
    total_range = models.CharField(choices=settings.TOTAL_RANGE, max_length=3, 
                                   verbose_name='单笔定金范围', help_text='单笔定金范围')
    is_activate = models.BooleanField(verbose_name='状态', default=True, help_text='该商品是否继续使用')

    class Meta:
        verbose_name = '商品表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name or self.id


class BusinessCompany(models.Model):
    """
    交易公司表
    """
    name = models.CharField(max_length=100, verbose_name='企业名称', help_text='企业名称', default='')
    scope = models.ForeignKey(BusinessScope, on_delete=models.CASCADE, verbose_name='企业经营分类', default='')
    corporation = models.CharField(max_length=20, verbose_name='企业法人姓名', blank=True, null=True, help_text='企业法人姓名')
    registered_capital = models.IntegerField(verbose_name='企业注册资金(元)', blank=True, null=True, help_text='企业注册资金')
    registered_capital_currency = models.CharField(max_length=10, verbose_name='注册资金币种', 
                                                   blank=True, null=True, help_text='注册资金币种', default='元人名币')
    registered_province = models.CharField(max_length=15, verbose_name='注册省份', blank=True, null=True, help_text='注册省份')
    telphone = models.CharField(max_length=15, verbose_name='企业办公电话', blank=True, null=True, help_text='企业办公电话')
    is_activate = models.BooleanField(verbose_name='状态', default=True, help_text='该公司是否继续使用')

    class Meta:
        verbose_name = '交易公司'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name or self.id


class Buyer(BusinessCompany):
    """
    买方表
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='所属集团子公司')
    mouth_buy_limit = models.PositiveSmallIntegerField(verbose_name='每月交易上限', default=5, help_text='买方每月交易笔数上限')
    total_range = models.CharField(choices=settings.TOTAL_RANGE, max_length=1, verbose_name='单笔定金范围', help_text='单笔定金范围')
    
    class Meta:
        verbose_name = '买方'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name or self.id


class Seller(BusinessCompany):
    """
    卖方表
    """
    class Meta:
        verbose_name = '卖方'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name or self.id


class Account(models.Model):
    """
    账号表
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='所属集团子公司')
    account_name = models.CharField(max_length=40, verbose_name='账号名称', help_text='账号名称')
    account = models.CharField(max_length=40, verbose_name='账号', help_text='账号')
    bank_sort_name = models.ForeignKey(Bank, on_delete=models.CASCADE, verbose_name='银行简称')
    bank_name = models.CharField(max_length=40, verbose_name='开户行名称', help_text='开户行名称')
    bank_code = models.CharField(max_length=40, verbose_name='开户行联行号', help_text='开户行联行号')
    day_max = models.IntegerField(verbose_name='每日交易上限', default=1000000, help_text='每日交易上限(默认不限制-100亿;单位万元)')
    is_activate = models.BooleanField(verbose_name='状态', default=True, help_text='该账户是否使用')
    is_corporate = models.BooleanField(verbose_name='是否对公户', default=False,
                                       help_text='该账户是否是对公户, 勾选代表是对公户, 取消勾选代表是单位结算卡(默认)')

    class Meta:
        verbose_name = '账号'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s-%s" % (self.company, self.bank_sort_name) or self.id

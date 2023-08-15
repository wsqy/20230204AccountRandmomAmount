import xadmin
from django.utils.html import format_html
from xadmin.models import Log

from Account.models import Company, BusinessScope, Buyer, Seller, Account, Products, Corporation, Bank, SubCompany, BanKuai

class BaseSetting:
    enable_themes = True
    use_bootswatch = True


class GlobalSettings:
    # 站点标题
    site_title = '转账生成系统管理后台'
    # 站点底部显示问题
    site_footer = '-- wsqy --'
    # 设置菜单可折叠
    menu_style='accordion'


class AccountInline:
    model = Account
    extra = 1

class BankInline:
    model = Bank
    extra = 1


class CompanyAdmin:
    
    def sort_name(self, obj):
        return obj.sort_name
    sort_name.short_description = '子公司简称'
    
    list_display = ['id', 'sub_comp', 'sort_name', 'name', 'corporation', 'company_code', 'is_activate', ]
    list_display_links = ['id', 'sort_name', 'name', ]
    list_filter = ['corporation', 'sub_comp', 'is_activate', ]
    list_editable = ['sub_comp', 'is_activate',  ]
    search_fields = ['name', ]
    import_excel = True
    # inlines = [AccountInline, ]
    model_icon = 'fa fa-credit-card'
    
    # 这里是admin的该法，下面的才是xadmin的
    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == 'corporation':   #外键字段
    #         kwargs["queryset"] = Corporation.objects.filter(is_activate=True)
    #     return super(CompanyAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_form_helper(self, *args, **kwargs):
        bankuai_list = BanKuai.objects.filter(id__in=self.request.user.last_name)
        self.form_obj.fields['corporation'].queryset = Corporation.objects.filter(is_activate=True, sub_bankuai__in=bankuai_list)
        return super(CompanyAdmin, self).get_form_helper(*args, **kwargs) 
    
    def queryset(self):
        # 列表筛选
        qs = super(CompanyAdmin, self).queryset()
        bankuai_list = BanKuai.objects.filter(id__in=self.request.user.last_name)
        return qs.filter(corporation__sub_bankuai__in=bankuai_list)
        super().queryset(self)

class BusinessScopeAdmin:
    list_display = ['id', 'name', 'is_activate']
    list_display_links = ['id', 'name']
    list_editable = ['name', 'is_activate']
    search_fields = ['name',]
    list_filter =['is_activate',]
    model_icon = 'fa fa-credit-card'


class ProductsAdmin:
    list_display = ['id', 'name','scope', 'type', 'price_min', 'price_max', 'unit', 'total_range', 'is_activate',]
    list_display_links = ['id', 'name']
    list_editable = ['scope', 'name', 'type', 'price_min', 'price_max', 'unit', 'total_range', 'is_activate',]
    list_filter = ['scope','total_range', 'is_activate',]
    search_fields = ['name', 'type',]    
    model_icon = 'fa fa-credit-card'


class BusinessCompanyAdmin:
    list_display = ['id', 'name', 'scope', 'registered_province']
    list_editable = ['scope', ]
    list_filter = ['scope', 'is_activate',]
    search_fields = ['name', 'corporation', 'registered_province']
    model_icon = 'fa fa-credit-card'


class AccountAdmin:
    list_display = ['id', 'bank_sort_name',  'account_name', 'account', 'company', 'is_activate']
    list_display_links = ['id', 'account_name']
    list_editable = ['is_activate', ]
    search_fields = ['company', 'account', 'bank_code']
    list_filter = ['is_activate', 'company', ]
    # import_excel = True
    model_icon = 'fa fa-credit-card'
        
    def get_form_helper(self, *args, **kwargs):
        bankuai_list = BanKuai.objects.filter(id__in=self.request.user.last_name)
        self.form_obj.fields['company'].queryset = Company.objects.filter(is_activate=True, corporation__sub_bankuai__in=bankuai_list)
        return super(AccountAdmin, self).get_form_helper(*args, **kwargs)

    def queryset(self):
        qs = super(AccountAdmin, self).queryset()
        bankuai_list = BanKuai.objects.filter(id__in=self.request.user.last_name)
        return qs.filter(company__corporation__sub_bankuai__in=bankuai_list)
        super().queryset(self)


class BuyerAdmin:
    list_display = ['id', 'name', 'company', 'scope', 'mouth_buy_limit', 'total_range', 'is_activate']
    list_display_links = ['id', 'name']
    list_editable = ['scope', 'company', 'mouth_buy_limit', 'total_range', 'is_activate']
    list_filter = ['scope', 'is_activate', 'company', 'mouth_buy_limit', 'total_range', 'registered_province']
    search_fields = ['name', 'corporation', 'registered_province']
    model_icon = 'fa fa-credit-card'

    def get_form_helper(self, *args, **kwargs):
        bankuai_list = BanKuai.objects.filter(id__in=self.request.user.last_name)
        self.form_obj.fields['company'].queryset = Company.objects.filter(is_activate=True, corporation__sub_bankuai__in=bankuai_list)
        return super(BuyerAdmin, self).get_form_helper(*args, **kwargs)

    def queryset(self):
        qs = super(BuyerAdmin, self).queryset()
        bankuai_list = BanKuai.objects.filter(id__in=self.request.user.last_name)
        return qs.filter(company__corporation__sub_bankuai__in=bankuai_list)
        super().queryset(self)
   
class SellerAdmin:
    list_display = ['id', 'name', 'scope', 'is_activate']
    list_display_links = ['id', 'name']
    list_editable = ['scope', 'is_activate']
    list_filter = ['scope', 'is_activate', 'registered_province']
    search_fields = ['name', 'corporation', 'registered_province']
    model_icon = 'fa fa-credit-card'

class CorporationAdmin:
    list_display = ['id', 'sub_bankuai', 'name', 'template', 'is_activate']
    list_display_links = ['id', 'name',]
    list_editable = ['sub_bankuai', 'template', 'is_activate']
    list_filter = ['sub_bankuai', 'template', 'is_activate',]
    search_fields = ['sub_bankuai', 'name', 'template',]
    model_icon = 'fa fa-credit-card'

    def get_form_helper(self, *args, **kwargs):
        bankuai_list = BanKuai.objects.filter(id__in=self.request.user.last_name)
        self.form_obj.fields['sub_bankuai'].queryset = bankuai_list
        return super(CorporationAdmin, self).get_form_helper(*args, **kwargs) 
    
    def queryset(self):
        qs = super(CorporationAdmin, self).queryset()
        bankuai_list = BanKuai.objects.filter(id__in=self.request.user.last_name)
        return qs.filter(sub_bankuai__in=bankuai_list)
        super().queryset(self)

class BankAdmin:
    list_display = ['id', 'name']
    list_display_links = ['id', 'name',]

class SubCompanyAdmin:
    list_display = ['id', 'name']
    list_display_links = ['id', 'name',]

class BanKuaiAdmin:
    list_display = ['id', 'name']
    list_display_links = ['id', 'name',]
    

xadmin.site.unregister(Log)
# xadmin.site.register(Bank, BankAdmin)
# xadmin.site.register(SubCompany, SubCompanyAdmin)
xadmin.site.register(BanKuai, BanKuaiAdmin)
xadmin.site.register(xadmin.views.CommAdminView, GlobalSettings)
xadmin.site.register(Corporation, CorporationAdmin)
xadmin.site.register(Company, CompanyAdmin)
xadmin.site.register(BusinessScope, BusinessScopeAdmin)
xadmin.site.register(Products, ProductsAdmin)
xadmin.site.register(Buyer, BuyerAdmin)
xadmin.site.register(Seller, SellerAdmin)
xadmin.site.register(Account, AccountAdmin)

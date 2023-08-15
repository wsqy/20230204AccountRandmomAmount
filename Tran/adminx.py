import xadmin
from django.utils.html import format_html
from .models import Task, TaskBatch, Transaction
from .utils import get_download_zipfile, get_download_excelfile
from Account.models import BanKuai, Corporation
# from .forms import TaskForm



class TaskAdmin:
    def download(self, obj):
        if obj.status:
            button_html = "<a class='changelink' href={}>下载</a>".format(get_download_zipfile(obj))
        else:
            button_html = "<p class='changelink' >异常, 请检查条件重新添加任务</p>"
        return format_html(button_html)
    download.short_description = '下载汇总文件'

    list_display = ['name', 'date', 'batch_total', 'corporation', 'budan_model', 'status', 'download']
    # empty_value_display = '无'
    exclude = ['file_no',]
    model_icon = 'fa fa-tasks'
    list_filter = ['corporation', 'status', 'date']
    search_fields = ['name']
    ordering = ['-date', '-id']
    # form = TaskForm

    def get_context(self):
        context = super(TaskAdmin, self).get_context()
        context.update({
            'show_save_as_new': False, 
            'show_save_and_continue': False,
            'show_save_and_add_another': False,
            'show_delete_link': False,
        })
        return context

    def get_readonly_fields(self, obj=None):
        if 'update' in self.request.path:
            return  ['amount_total_min', 'amount_total_max', 'batch_num_min', \
                     'batch_num_max', 'batch_total','status', 'remark']
        else:
            return ['status',]
        
    def get_form_helper(self, *args, **kwargs):
        bankuai_list = BanKuai.objects.filter(id__in=self.request.user.last_name)
        self.form_obj.fields['corporation'].queryset = Corporation.objects.filter(sub_bankuai__in=bankuai_list)
        return super(TaskAdmin, self).get_form_helper(*args, **kwargs)
    
    def queryset(self):
        qs = super(TaskAdmin, self).queryset()
        bankuai_list = BanKuai.objects.filter(id__in=self.request.user.last_name)
        return qs.filter(corporation__sub_bankuai__in=bankuai_list)
        super().queryset(self)


class TaskBatchAdmin:
    def download_zz(self, obj):
        if obj.task.status:
            button_html = "<a class='changelink' href={}>下载</a>".format(get_download_excelfile(obj, '转账文件'))
        else:
            button_html = "<p class='changelink' >异常, 请检查条件重新添加任务</p>"
        return format_html(button_html)

    download_zz.short_description = '下载转账文件'
    list_display = ['task', 'num', 'batch_total', 'amount_total', 'download_zz']
    list_filter = ['task', ]
    readonly_fields = ['task', 'num', 'batch_total', 'amount_total',]
    empty_value_display = '无'
    model_icon = 'fa fa-info'

    def has_add_permission(self):
        return False

    def get_context(self):
        context = super(TaskBatchAdmin, self).get_context()
        context.update({
            'show_save': False,
            'show_save_as_new': False, 
            'show_save_and_continue': False, 
            'show_delete_link': False,
        })
        return context

    def queryset(self):
        qs = super(TaskBatchAdmin, self).queryset()
        bankuai_list = BanKuai.objects.filter(id__in=self.request.user.last_name)
        return qs.filter(task__corporation__sub_bankuai__in=bankuai_list)
        super().queryset(self)
        
        
class TransactionAdmin:
    def company(self, obj):
        return obj.accoun.company
    company.short_description = '代定人'
    
    def task(self, obj):
        return obj.task_batch.task
    task.short_description = '所属任务'
    
    list_display = ['order_no', 'task', 'task_batch', 'buyer', 'seller',  'company']
    list_filter = ['task_batch', 'buyer', 'seller', 'order_no']
    readonly_fields = ['task_batch', 'buyer', 'seller', 'amount', ]
    empty_value_display = '无'
    model_icon = 'fa fa-archive'

    def has_add_permission(self):
        return False

    def get_context(self):
        context = super(TransactionAdmin, self).get_context()
        context.update({
            'show_save': False,
            'show_save_as_new': False, 
            'show_save_and_continue': False, 
            'show_delete_link': False,
        })
        return context

    def queryset(self):
        qs = super(TransactionAdmin, self).queryset()
        bankuai_list = BanKuai.objects.filter(id__in=self.request.user.last_name)
        return qs.filter(task__task_batch__corporation__sub_bankuai__in=bankuai_list)
        super().queryset(self)
        

xadmin.site.register(Task, TaskAdmin)
xadmin.site.register(TaskBatch, TaskBatchAdmin)
xadmin.site.register(Transaction, TransactionAdmin)

# adminx_actions.py
from xadmin.plugins.actions import BaseActionView


class ClearAction(BaseActionView):
    '''清空action'''
    action_name = "clear_yue"    # 相当于这个Action的唯一标示, 尽量用比较针对性的名字
    description = '清空选中子公司当日已用额度'  # 出现在 Action 菜单中名称
    model_perm = 'change'       # 该 Action 所需权限
    icon = 'fa fa-bug'

    # 执行的动作
    def do_action(self, queryset):
        for obj in queryset:
            obj.amount_total = 0
            obj.save()
        return None  # 返回的url地址

def clear_yue(obj):
    obj.amount_total = 0
    obj.save()
    return ''
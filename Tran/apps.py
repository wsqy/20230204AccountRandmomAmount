from django.apps import AppConfig


class TranConfig(AppConfig):
    name = 'Tran'    
    verbose_name = '日常交易管理'
        
    def ready(self):
        import Tran.signals

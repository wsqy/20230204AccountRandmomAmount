from django.apps import AppConfig


class StatisticsConfig(AppConfig):
    name = 'Statistics'    
    verbose_name = '数据统计'
        
    def ready(self):
        import Statistics.signals

from django.contrib import admin

from .models import MainHelpTopic, MainHelpTopicDetail, SpecificViewTopicDetail, SpecificViewHelpTopic

# Register your models here.
admin.site.register(MainHelpTopic)
admin.site.register(MainHelpTopicDetail)
admin.site.register(SpecificViewHelpTopic)
admin.site.register(SpecificViewTopicDetail)

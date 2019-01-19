from django.contrib import admin

from .models import MainHelpTopic, MainHelpTopicDetails, SpecificViewTopicDetails, SpecificViewHelpTopic

# Register your models here.
admin.site.register(MainHelpTopic)
admin.site.register(MainHelpTopicDetails)
admin.site.register(SpecificViewHelpTopic)
admin.site.register(SpecificViewTopicDetails)

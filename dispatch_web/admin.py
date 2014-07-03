from django.contrib import admin
from dispatch_web.models import TransferLog, Poller, Server, ErrorMgr

admin.site.register(TransferLog)
admin.site.register(Poller)
admin.site.register(Server)
admin.site.register(ErrorMgr)

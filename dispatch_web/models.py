from django.db import models

class TransferLog(models.Model):

    name = models.CharField(max_length=200)
    filename = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    started = models.DateTimeField('date started')
    ended = models.DateTimeField('date ended', null=True)
    error = models.TextField(null=True)
    server = models.CharField(max_length=200)
    filesize = models.BigIntegerField()

    def __unicode__(self):
        return self.name + ":" + self.filename

class Poller(models.Model):

    name = models.CharField(max_length=200)
    path = models.CharField(max_length=200)
    host = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    ssh_key = models.TextField()
    poller_type = models.CharField(max_length=200)
    transfer_speed = models.IntegerField()
    excludes = models.CharField(max_length=200)
    ssh_port = models.IntegerField()
    destination = models.CharField(max_length=200)
#    disable_on_error = models.BooleanField()
    encrypt = models.BooleanField()
    encrypt_passphrase = models.CharField(max_length=200)
    max_transfers = models.IntegerField()
    enabled = models.BooleanField()

    def __unicode__(self):
        return self.name

    def set_from_dict(self, d):
        for k,v in d.items():
            setattr(self, k, v)

class Server(models.Model):

    name = models.CharField(max_length=200)
    ipaddr = models.IPAddressField()
    enabled = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

    def set_from_dict(self, d):
        for k,v in d.items():
            setattr(self, k, v)

class ErrorMgr(models.Model):

    name = models.CharField(max_length=200)
    total_errors = models.IntegerField(default=0)
    time_disabled = models.DateTimeField(default=None, null=True)
    locking_agent = models.CharField(max_length=50, default=None, null=True)

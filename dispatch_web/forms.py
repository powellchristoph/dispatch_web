from django import forms
from django.core.exceptions import ValidationError
from bootstrap_toolkit.widgets import BootstrapDateInput, BootstrapTextInput, BootstrapUneditableInput

from models import Poller, Server, TransferLog

class PollerForm(forms.Form):

    name = forms.CharField(
        max_length=100,
        help_text=u'The affiliate name. Lowercase, seperated by underbars',
        widget=forms.TextInput()
    )

    path = forms.CharField(
        max_length=200,
        help_text='The filesystem path to watch for files.',
        widget=forms.TextInput(
            attrs={
                'value': '/home/docker/'
            })
    )

    host = forms.CharField(
        max_length=100,
        help_text='The remote Aspera server.',
        widget=forms.TextInput()
    )

    username = forms.CharField(
        max_length=100,
        help_text='The remote Aspera username.',
        widget=forms.TextInput()
    )

    password = forms.CharField(
        max_length=100,
        help_text='The remote Aspera password. Only use if not using an SSH key.',
        required=False,
        widget=forms.TextInput()
    )

    ssh_key = forms.CharField(
        max_length=2000,
        help_text='Paste in SSH key if not using a password.',
        required=False,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Optional'
            })
    )

    poller_type = forms.ChoiceField(
        choices=(
            ('----------', '-----------'),
            ('FilePoller', 'File Poller'),
            ('DirPoller', 'Directory Poller'),
            ('SubDirPoller', 'Sub-directory Poller'),
            ('PAPoller', 'Provider/Asset Poller'),
            ('TelusPoller', 'Telus Poller'),
            ('GooglePoller', 'Google Poller'),
            ('DirTarPoller', 'Dir-Tar Poller')
        ),
        help_text='Defined pollers.'
    )

    transfer_speed = forms.IntegerField(
        help_text='The transfer speed in Mbps.',
        required=False,
        initial=150,
        widget=forms.TextInput()
    )

    excludes = forms.CharField(
        max_length=100,
        help_text='A comma seperated list of files to exclude. Ask before using.',
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Optional'
            })
    )

    ssh_port = forms.IntegerField(
        required=False,
        initial=22,
        widget=forms.TextInput()
    )

    destination = forms.CharField(
        max_length=100,
        help_text='A destination folder on the remote Aspera server.',
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Optional'
            })
    )

    encrypt = forms.BooleanField(
            required=False,
            initial=False,
            help_text='Perform filebase encryption.',
            widget=forms.CheckboxInput(
                attrs={
                    'id': 'id_encrypt'
                })
    )

    encrypt_passphrase = forms.CharField(
        max_length=100,
        required=False,
        help_text='The passphrase used to encrypt the file.',
        widget=forms.TextInput()
    )

    max_transfers = forms.IntegerField(
        help_text='The maximum number of concurrent transfers.',
        required=False,
        initial=3,
        widget=forms.TextInput()
    )

    enabled = forms.BooleanField(
            required=False,
            initial=True,
            help_text='Enable the poller'
    )

    def clean(self):
        cleaned_data = super(PollerForm, self).clean()

        data = cleaned_data.get('poller_type')
        if data == self.fields['poller_type'].choices[0][0]:
            msg = u'You must select a poller.'
            self._errors['poller_type'] = self.error_class([msg])
            del cleaned_data['poller_type']

        password = cleaned_data.get('password')
        ssh_key = cleaned_data.get('ssh_key')

        if password and ssh_key or not password and not ssh_key:
            msg = u'Please set either a password OR ssh key, not both.'
            self._errors['password'] = self.error_class([msg])
            self._errors['ssh_key'] = self.error_class([msg])
            del cleaned_data['password']
            del cleaned_data['ssh_key']

        if ssh_key:
            print 'Converting newlines...'
            cleaned_data['ssh_key'] = str(ssh_key).replace('\r\n', '\n')

        encrypt = cleaned_data.get('encrypt')
        encrypt_passphrase = cleaned_data.get('encrypt_passphrase')
        if encrypt and not encrypt_passphrase:
            msg = u'You must supply a passphrase if using file encryption.'
            self._errors['encrypt_passphrase'] = self.error_class([msg])
            del cleaned_data['encrypt_passphrase']
        if not encrypt and encrypt_passphrase:
            msg = u'You have supplied a passphrase but not enabled encryption.'
            self._errors['encrypt'] = self.error_class([msg])
            del cleaned_data['encrypt']

        return cleaned_data


class ServerForm(forms.Form):

    name = forms.CharField(
        max_length=100,
        help_text=u'The hostname of the server.',
        widget=forms.TextInput()
    )

    ipaddr = forms.CharField(
        max_length=100,
        help_text=u'The IP address of the server',
    )

    def clean(self):
        cleaned_data = super(ServerForm, self).clean()

        ip = cleaned_data.get('ipaddr')
        existing = Server.objects.filter(ipaddr=ip).exists()

        if existing:
            msg = u'A server with that IP already exists.'
            self._errors['ipaddr'] = self.error_class([msg])
            del cleaned_data['ipaddr']

        return cleaned_data

class SearchForm(forms.Form):

    filename = forms.CharField(
            max_length=100,
            label = "",
            required=False,
            widget=forms.TextInput(
                attrs={
                    'placeholder': 'Filename'
                })
        )

    status = forms.ChoiceField(
            label = '',
            choices=(
                ('None', 'Status'),
                ('Transferring', 'Transferring'),
                ('Complete', 'Completed'),
                ('Cancelled', 'Cancelled'),
                ('Error', 'Error')
            ),
            widget=forms.Select(
                attrs={
                    'class': 'span2'
                })
        )
    
    def __init__(self, *args, **kwargs):
        pollers = kwargs.pop('poller_choices')
        servers = kwargs.pop('server_choices')
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['poller'] = forms.ChoiceField(
            choices=pollers,
            label="",
            widget=forms.Select(attrs={'class': 'span2'})
        )
        self.fields['server'] = forms.ChoiceField(
            choices=servers,
            label="",
            widget=forms.Select(attrs={'class': 'span2'})
        )

    def clean(self):
        cleaned_data = super(SearchForm, self).clean()

        return cleaned_data





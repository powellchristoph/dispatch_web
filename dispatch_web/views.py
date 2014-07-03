from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms.models import model_to_dict
from django.utils import simplejson
from django import forms

from bootstrap_toolkit.widgets import BootstrapUneditableInput

from dispatch_web.models import TransferLog, Poller, Server, ErrorMgr

from forms import PollerForm, ServerForm, SearchForm

import paramiko

def home(request):

    data = {}

    active_transfers = TransferLog.objects.filter(status__exact='Transferring').order_by('-started')
    completed_transfers = TransferLog.objects.exclude(status__exact='Transferring').order_by('-started')

    data['active_transfers'] = active_transfers[:10]
    data['completed_transfers'] = completed_transfers[:25]

    return render(request, 'dispatch_web/home.html', data)

def all_active(request):

    transfers = TransferLog.objects.filter(status__exact='Transferring').order_by('-started')
    return render(request, 'dispatch_web/transfers.html', {'transfers': transfers, 'status': 'Active'})

def all_completed(request):

    transfers = TransferLog.objects.exclude(status__exact='Transferring').order_by('-started')
    return render(request, 'dispatch_web/transfers.html', {'transfers': transfers, 'status': 'Completed'})

def search(request):
    
    def make_tups(list, name='None'):
        tup = (('None', '%s' % name),)
        for item in list:
            tup = tup + ((item, item),)
        return tup

    poller_choices = make_tups(Poller.objects.all().values_list('name', flat=True).order_by('name'), 'Pollers')
    server_choices = make_tups(Server.objects.all().values_list('name', flat=True).order_by('name'), 'Servers')

    if request.method == 'POST':
        form = SearchForm(request.POST, poller_choices=poller_choices, server_choices=server_choices)
        if form.is_valid():
            data = form.cleaned_data

            transfers = TransferLog.objects.all().order_by('-started')
            if data['server'] != 'None':
                transfers = transfers.filter(server__exact=data['server']).order_by('-started')
            if data['poller'] != 'None':
                transfers = transfers.filter(name__exact=data['poller']).order_by('-started')
            if data['status'] != 'None':
                transfers = transfers.filter(status__exact=data['status']).order_by('-started')
            if data['filename'] != '':
                transfers = transfers.filter(filename__icontains=data['filename']).order_by('-started')

            return render(request, 'dispatch_web/search.html', {'form': form, 'transfers': transfers})

    else:
        form = SearchForm(poller_choices=poller_choices, server_choices=server_choices)

    return render(request, 'dispatch_web/search.html', {'form': form})

def servers(request):

    all_servers = Server.objects.all().order_by('name')

    if request.method == 'POST':
        form = ServerForm(request.POST)
        if form.is_valid():
            s = Server()
            s.set_from_dict(form.cleaned_data)

            all_pollers = Poller.objects.all().order_by('name')
            for p in all_pollers:
                try:
                    create_poller_dir(p.path, s.ipaddr)
                except Exception, e:
                    print str(e)
                    messages.error(request, 'There was an error creating the %s path on the server. Server not saved.' % p.path)
                    return render(request, 'dispatch_web/servers.html', {'form': form, 'servers': all_servers})

            s.save()
            return HttpResponseRedirect(reverse('dispatch:servers'))
        else:
            messages.error(request, 'There was an error submitting your information.')

    else:
        form = ServerForm()

    return render(request, 'dispatch_web/servers.html', {'form': form, 'servers': all_servers})

def delete_server(request, server_id):
#    server = get_object_or_404(Server, pk=server_id)
#    name = server.name
#    server.delete()

    messages.error(request, 'This function has been disabled, please contact the SE team.')
    return HttpResponseRedirect(reverse('dispatch:servers'))

def pollers(request):

    all_pollers = Poller.objects.all().order_by('name')

    return render(request, 'dispatch_web/pollers.html', {'pollers': all_pollers})

def create_poller_dir(path, server_ip):
    
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(server_ip, username='docker', password='EbIflb02')
        stdin, stdout, stderr = client.exec_command('mkdir %s' % path)
    except Exception, e:
        try:
            client.close()
        except:
            pass
        raise e

def add_poller(request):

    if request.method == 'POST':
        form = PollerForm(request.POST)
        if form.is_valid():
            p = Poller()
            p.set_from_dict(form.cleaned_data)

            all_servers = Server.objects.all().order_by('name')
            for s in all_servers:
                try:
                    create_poller_dir(p.path, s.ipaddr)
                except Exception, e:
                    messages.error(request, 'There was an error creating the poller path on %s. Poller not saved.' % s)
                    return render(request, 'dispatch_web/add_poller.html', {'form': form})

            p.total_errors = 0
            p.save()

            # Create entry for errors
            e = ErrorMgr(name=p.name, pk=p.id)
            e.save()

            return HttpResponseRedirect(reverse('dispatch:pollers'))
    else:
        form = PollerForm()

    return render(request, 'dispatch_web/add_poller.html', {'form': form})

def poller_detail(request, poller_id):
    poller = get_object_or_404(Poller, pk=poller_id)
    return render(request, 'dispatch_web/detail_poller.html', {'poller': poller})

def edit_poller(request, poller_id):
    poller = get_object_or_404(Poller, pk=poller_id)

    if request.method == 'POST':
        form = PollerForm(request.POST)
#        for k,v in form.__dict__.iteritems():
#            print '%s :: %s' % (k, v)
        if form.is_valid():
            poller.set_from_dict(form.cleaned_data)
            poller.save()
            return HttpResponseRedirect(reverse('dispatch:poller_detail', kwargs={'poller_id': poller_id}))
    else:
        settings = model_to_dict(poller, fields=[], exclude=[])
        form = PollerForm(settings)
        form.fields['name'].widget = BootstrapUneditableInput()
        form.fields['path'].widget = BootstrapUneditableInput()

    return render(request, 'dispatch_web/edit_poller.html', {'form': form})

def enable_poller(request, poller_id):

    poller = get_object_or_404(Poller, pk=poller_id)
    poller.enabled = True
    poller.save()

    return HttpResponseRedirect(reverse('dispatch:poller_detail', kwargs={'poller_id': poller_id}))

def disable_poller(request, poller_id):

    poller = get_object_or_404(Poller, pk=poller_id)
    poller.enabled = False 
    poller.save()

    return HttpResponseRedirect(reverse('dispatch:poller_detail', kwargs={'poller_id': poller_id}))

def delete_poller(request, poller_id):
    poller = get_object_or_404(Poller, pk=poller_id)

    if poller.enabled:
        messages.error(request, 'The poller is active! You must disable it first.')
        return render(request, 'dispatch_web/detail_poller.html', {'poller': poller})

    poller.delete()

    error = get_object_or_404(ErrorMgr, pk=poller_id)
    error.delete()

    # TODO: Remove directories on servers

    return HttpResponseRedirect(reverse('dispatch:pollers'))

def stats(request):
    data = {}
    try:
        with open('/var/www/sems/dispatch_web/dispatch_stats.txt', 'r') as f:
            data['stats'] = f.read()
            print type(data['stats'])
    except:
        data['stats'] = 'Unable to find statistics data.'

    return render(request, 'dispatch_web/stats.html', data)

from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse, reverse_lazy
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from core.models import LyfeUser, GoalGroup, Document
from core.forms import DocumentForm
from django.contrib.auth import logout as auth_logout

def login(request):
    return render_to_response('core/login.html',
        {},
        context_instance=RequestContext(request))

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('core.views.dashboard'))

def dashboard(request):
    return render_to_response('core/dashboard.html',
        { 'users' : LyfeUser.objects.all().order_by('username') },
        context_instance=RequestContext(request))

def list(request):
	if request.method == 'POST':
		form = DocumentForm(request.POST, request.FILES)
		if form.is_valid():
			newDoc = Document(docfile = request.FILES['docfile'])
			newDoc.save()
			return HttpResponseRedirect(reverse('core.views.list'))
	else:
		form = DocumentForm()

	documents = Document.objects.all()

	return render_to_response(
		'core/list.html',
		{'documents': documents, 'form':form},
		context_instance=RequestContext(request)
	)
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse, reverse_lazy
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from core.models import LyfeUser, GoalGroup, Goal, Group, Membership, ShareSetting, Reward, RewardTransaction, Friend, Update, Comment, Document
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
    lyfeuser = get_object_or_404(LyfeUser, pk='Solix')
    #goalgroups = get_object_or_404(GoalGroup, ownerid = 'Solix')
    goalgroups = list(GoalGroup.objects.filter(ownerid=lyfeuser.pk))
    goals = {}
    
    for goalgroup in goalgroups:
        goals[goalgroup] = list(Goal.objects.filter(goal_id=goalgroup.pk).order_by('order_num'))
        
    return render_to_response('core/dashboard.html',
        { 'lyfeuser' : lyfeuser, 'goals' : goals},
        context_instance=RequestContext(request))

def profile(request, username):
    current_user = request.user
    lyfeuser = get_object_or_404(LyfeUser, pk=username)
    
    if current_user.pk != lyfeuser.pk:
        friendship = Friend.objects.get(requester_id=current_user.pk, recipient_id = lyfeuser.pk)
        if friendship:
        	print "fill?"
            # we know user has friend requested other user and can change behavior depending on if accepted or not
        # else friendship is null
    else:
        # user is current user, should be able to see everything
	    goalgroups = list(GoalGroup.objects.filter(ownerid=lyfeuser.pk))
	    goals = {}
    
    for goalgroup in goalgroups:
        goals[goalgroup] = list(Goal.objects.filter(goal_id=goalgroup.pk).order_by('order_num'))
    
    
    return render_to_response('core/profile.html',
    { 'lyfeuser' : lyfeuser, 'goals' : goals},
    context_instance=RequestContext(request))
    
def avatar(request):
	if request.method == 'POST':
		form = DocumentForm(request.POST, request.FILES)
		if form.is_valid():
			newDoc = Document(docfile = request.FILES['docfile'])
			newDoc.save()
			return HttpResponseRedirect(reverse('core.views.avatar'))
	else:
		form = DocumentForm()

	documents = Document.objects.all()

	return render_to_response(
		'core/list.html',
		{'documents': documents, 'form':form},
		context_instance=RequestContext(request)
	)
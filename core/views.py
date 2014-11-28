from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse, reverse_lazy
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from core.models import LyfeUser, GoalGroup, Goal, Group, Membership, ShareSetting, Reward, RewardTransaction, Friend, Update, Comment, Document
from core.forms import DocumentForm
from django.contrib.auth import logout as auth_logout
from django.db import IntegrityError
from django.forms.models import ModelForm, inlineformset_factory

FAKE_USER = get_object_or_404(LyfeUser, pk='Solix') # replace all instances with request.user when authentication works

def login(request):
    return render_to_response('core/login.html',
        {},
        context_instance=RequestContext(request))

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('core.views.dashboard'))

def dashboard(request):
    lyfeuser = FAKE_USER
    
    goalgroups = list(GoalGroup.objects.filter(ownerid=lyfeuser.pk))
    goals = {}
    
    # goals
    for goalgroup in goalgroups:
        goals[goalgroup] = list(Goal.objects.filter(goal_id=goalgroup.pk).order_by('order_num'))
    
    # friend requests
    friend_requests = list(Friend.objects.filter(recipient_id = lyfeuser, is_approved = False))
    
    # friends
    friends = list(Friend.objects.filter(requester_id = lyfeuser, is_approved = True))
    
    # following
    #following = list(Friend.objects.filter(requester_id = lyfeuser, is_approved = False))
    
    # newsfeed
    friendIDs = []
    friendIDs.append(FAKE_USER.pk) # you can see your own updates
    for friend in friends:
        friendIDs.append(friend.recipient_id)
        
    newsfeed = Update.objects.filter(user_id_id__in=friendIDs).order_by('timestamp').reverse()
    
    # update form
    updateform = UpdateForm()
    
    return render_to_response('core/dashboard.html',
        { 'lyfeuser' : lyfeuser, 'goals' : goals, 'friend_requests' : friend_requests, 'friends' : friends, 'updateform' : updateform, 'newsfeed' : newsfeed },
        context_instance=RequestContext(request))

def profile(request, username):
    current_user = FAKE_USER
    lyfeuser = get_object_or_404(LyfeUser, pk=username)
    addfriend = False
    currentuser = False
    
    if current_user.pk != lyfeuser.pk:
        try:
            friendship = Friend.objects.get(requester_id=current_user, recipient_id = lyfeuser)
            # user has friend request or accepted other user
        except Friend.DoesNotExist:
            addfriend = True
            print "friendship is null"
    else:
        currentuser = True
        print "fill"
    goalgroups = list(GoalGroup.objects.filter(ownerid=lyfeuser.pk))
    goals = {}
    
    for goalgroup in goalgroups:
        goals[goalgroup] = list(Goal.objects.filter(goal_id=goalgroup.pk).order_by('order_num'))
    
    return render_to_response('core/profile.html',
    { 'lyfeuser' : lyfeuser, 'goals' : goals, 'addfriend' : addfriend, 'currentuser' : currentuser},
    context_instance=RequestContext(request))

def addfriend(request, username):
    current_user = FAKE_USER
    lyfeuser = get_object_or_404(LyfeUser, pk=username)
    try:
        friend_request = Friend(requester_id = current_user, recipient_id = lyfeuser)
        try:
            original_request = Friend.objects.get(requester_id=lyfeuser, recipient_id = current_user)
            original_request.is_approved = True
            friend_request.is_approved = True
            
            original_request.save()
        except Friend.DoesNotExist:
            print "friend request is not accepted yet"
            
        friend_request.save()
        
    except IntegrityError:
        print "This action has already been completed."
        
    return HttpResponseRedirect(reverse('core.views.profile', kwargs={'username' : username}))
    
def unfriend(request, username):
    current_user = FAKE_USER
    lyfeuser = get_object_or_404(LyfeUser, pk=username)
    
    try:
        friend_request = Friend.objects.get(requester_id = current_user, recipient_id = lyfeuser)
        try:
            original_request = Friend.objects.get(requester_id=lyfeuser, recipient_id = current_user)
            original_request.delete()
        except Friend.DoesNotExist:
            print "friend request is not accepted yet"
            
        friend_request.delete()
        
    except Friend.DoesNotExist:
        print "This action has already been completed."
        
    return HttpResponseRedirect(reverse('core.views.profile', kwargs={'username' : username}))

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

def post_update(request, goalgroup):
    updateForm = UpdateForm(request.POST)
    # Remember to set drinker.name before updating the database, because
    # PartialDrinkerForm doesn't contain this information:
    update = updateForm.save(commit=False)
    update.goal_id_id = goalgroup
    update.user_id_id = FAKE_USER.pk
    update.save()
    
    return HttpResponseRedirect(reverse('core.views.dashboard'))

class UpdateForm(ModelForm):
    class Meta:
        model = Update
        fields = ['content']
        
    #user_id = models.ForeignKey(LyfeUser)
    #goal_id = models.ForeignKey(GoalGroup)
    #timestamp = models.DateTimeField(auto_now_add = True)
    #content = models.CharField(max_length=50) #file ref or something?
    
class CommentForm(ModelForm):
    class Meta:
        model = Comment
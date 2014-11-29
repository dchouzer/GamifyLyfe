from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse, reverse_lazy
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from core.models import LyfeUser, GoalGroup, Goal, Group, Membership, ShareSetting, Reward, RewardTransaction, Friend, Update, Comment
from core.forms import DocumentForm
from django.contrib.auth import logout as auth_logout
from django.db import IntegrityError
from django.forms.models import ModelForm, inlineformset_factory, modelform_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class MyRegistrationForm(UserCreationForm):
    #avatar = forms.FileField(required = False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')        

    def save(self,commit = True):   
        newuser = super(MyRegistrationForm, self).save(commit = False)
        #newuser.avatar = self.cleaned_data['avatar']
        if commit:
            newuser.save()
            #newlyfeuser = LyfeUser(avatar = self.cleaned_data['avatar'], username = newuser.username, user_id = newuser.pk)
            newlyfeuser = LyfeUser(username = newuser.username, user_id = newuser.pk)
            newlyfeuser.save()
        
        return newuser

#FAKE_USER = get_object_or_404(LyfeUser, pk='Solix') # replace all instances with request.user when authentication works

def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse(('core.views.dashboard')))
    else:
        return render_to_response('core/login.html',
            {},
            context_instance=RequestContext(request))

def register(request):
    if request.method == 'POST':
        form = MyRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(('core.views.login')))
    else:
        form = MyRegistrationForm()
    return render_to_response('core/register.html',
        { 'form': form, },
        context_instance=RequestContext(request))

def login(request):
    return render_to_response('core/login.html',
        {},
        context_instance=RequestContext(request))

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('core.views.login'))

def dashboard(request):
    lyfeuser = get_object_or_404(LyfeUser, pk=request.user.username)
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
    friendIDs.append(lyfeuser.pk) # you can see your own updates
    for friend in friends:
        friendIDs.append(friend.recipient_id)
        
    newsfeed = Update.objects.filter(user_id_id__in=friendIDs).order_by('timestamp').reverse()
    
    # update form
    updateform = modelform_factory(Update, fields = ('content',), widgets = {'content': forms.Textarea}, labels = {'content' : ''})
    
    # goal form
    goal_groupform = modelform_factory(GoalGroup, fields=('name',), labels = {'name' : 'Category name'})
    goal_formset = inlineformset_factory(GoalGroup, Goal, extra=1, fields = ('name', 'difficulty'), can_delete = False, labels = {'name' : 'Initial Goal name'})
        
    return render_to_response('core/dashboard.html',
        { 'lyfeuser' : lyfeuser, 'goals' : goals, 'friend_requests' : friend_requests, 'friends' : friends, 'updateform' : updateform, 'newsfeed' : newsfeed, 'goal_groupform' : goal_groupform, 'goal_formset' : goal_formset },
        context_instance=RequestContext(request))

def profile(request, username):
    current_user = get_object_or_404(LyfeUser, pk=request.user.username)
    lyfeuser = get_object_or_404(LyfeUser, pk=username)
    addfriend = False
    currentuser = False
    
    if current_user.pk != lyfeuser.pk:
        try:
            friendship = Friend.objects.get(requester_id=current_user, recipient_id = lyfeuser)
            # user has friend request or accepted other user
        except Friend.DoesNotExist:
            addfriend = True
            # not friends
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
    current_user = get_object_or_404(LyfeUser, pk=request.user.username)
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
    current_user = get_object_or_404(LyfeUser, pk=request.user.username)
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
    current_user = get_object_or_404(LyfeUser, pk=request.user.username)
    
    if request.method == 'POST':
		form = DocumentForm(request.POST, request.FILES)
		if form.is_valid():
			current_user.avatar = request.FILES['docfile']
			current_user.save()
			return HttpResponseRedirect(reverse('core.views.avatar'))
    else:
		form = DocumentForm()

    return render_to_response(
		'core/list.html',
		{'form': form, 'current_user': current_user},
		context_instance=RequestContext(request)
	)

def post_update(request, goal):
    #goal = Goal.objects.get(pk = goal)
         
    updateForm = UpdateForm(request.POST)
    update = updateForm.save(commit=False)
    update.goal_id_id = goal
    update.user_id_id = request.user.username
    update.save()
    
    return HttpResponseRedirect(reverse('core.views.dashboard'))

def add_goal(request):
    GoalGroupForm = modelform_factory(GoalGroup, fields=('name',))
    GoalFormSet = inlineformset_factory(GoalGroup, Goal, extra=1, fields = ('name', 'difficulty'), can_delete = False)
    
    goalGroupForm = GoalGroupForm(request.POST)
    goalGroup = goalGroupForm.save(commit=False)
    goalGroup.ownerid_id = request.user.username
    goalGroup.save()
    
    goalFormSet = GoalFormSet(request.POST, request.FILES)
    if goalFormSet.is_valid():
        for goalForm in goalFormSet:
            goal = goalForm.save(commit=False)
            goal.goal_id_id = goalGroup.id
            goal.start_date = goal.est_date
            if goal.difficulty == 0:
                goal.base_points = 10
            elif goal.difficulty == 1:
                goal.base_points = 20
            elif goal.difficulty == 2:
                goal.base_points = 40
            
            goal.save()
    
    return HttpResponseRedirect(reverse('core.views.dashboard'))


""" Forms for database """
#TODO: move to separate forms.py file?
class UpdateForm(ModelForm):
    class Meta:
        model = Update
        fields = ['content']
#  modelform_factory(Update, fields=("content"))
class GoalGroupForm(ModelForm):
    class Meta:
        model = GoalGroup
        fields = ['name']
       
        
class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        
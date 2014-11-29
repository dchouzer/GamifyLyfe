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
from datetime import date, datetime, tzinfo, timedelta

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
        goals[goalgroup] = Goal.objects.filter(goal_id=goalgroup.pk).order_by('order_num')
    
    # friend requests
    friend_requests = list(Friend.objects.filter(recipient_id = lyfeuser, is_approved = False))
    
    # friends
    friends = list(Friend.objects.filter(requester_id = lyfeuser, is_approved = True))
    
    # newsfeed
    friendIDs = []
    friendIDs.append(lyfeuser.pk) # you can see your own updates
    for friend in friends:
        friendIDs.append(friend.recipient_id)
        
    newsfeed = Update.objects.filter(user_id_id__in=friendIDs).order_by('timestamp').reverse()
    
    # update form
    updateform = modelform_factory(Update, fields = ('content', 'completion'), widgets = {'content': forms.Textarea}, labels = {'content' : ''})
    
    # goal category form
    goal_groupform = modelform_factory(GoalGroup, fields=('name',), labels = {'name' : 'Category name'})
    goal_formset = inlineformset_factory(GoalGroup, Goal, extra=1, fields = ('name', 'difficulty'), can_delete = False, labels = {'name' : 'Initial goal'})
      
    # goal form
    actionitem_form = modelform_factory(Goal, fields=('name', 'difficulty'), labels = {'name' : 'description'})
    
    return render_to_response('core/dashboard.html',
        { 'lyfeuser' : lyfeuser, 'goals' : goals, 'friend_requests' : friend_requests, 'friends' : friends, 'updateform' : updateform, 'newsfeed' : newsfeed, 'goal_groupform' : goal_groupform, 'goal_formset' : goal_formset, 'actionitem_form' : actionitem_form},
        context_instance=RequestContext(request))

def profile(request, username):
    current_user = get_object_or_404(LyfeUser, pk=request.user.username)
    lyfeuser = get_object_or_404(LyfeUser, pk=username)
    addfriend = False
    friendpoints = False
                    
    if current_user.pk != lyfeuser.pk:
        try:
            friendship = Friend.objects.get(requester_id=current_user, recipient_id = lyfeuser)
            # user has friend request or accepted other user
        except Friend.DoesNotExist:
            addfriend = True
            # not friends
           
        # check if enough time has passed to give friendpoints again      
        if current_user.last_fp_given:
            difference = datetime.now(UTC()) - current_user.last_fp_given
            friendpoints = difference.total_seconds() > 3600
        else:
            friendpoints = True
    
    goalgroups = list(GoalGroup.objects.filter(ownerid=lyfeuser.pk))
    goals = {}
    
    for goalgroup in goalgroups:
        goals[goalgroup] = Goal.objects.filter(goal_id=goalgroup.pk).order_by('order_num')
    
    # friends
    friends = list(Friend.objects.filter(requester_id = lyfeuser, is_approved = True))
    
    # newsfeed
    newsfeed = Update.objects.filter(user_id=lyfeuser).order_by('timestamp').reverse()
    
    return render_to_response('core/profile.html',
    { 'lyfeuser' : lyfeuser, 'goals' : goals, 'addfriend' : addfriend, 'friends' : friends, 'newsfeed' : newsfeed, 'friendpoints' : friendpoints },
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
            pass
            
        friend_request.save()
        
    except IntegrityError:
        pass # already requested
        
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
            pass # friend request not accepted
            
        friend_request.delete()
        
    except Friend.DoesNotExist:
        pass # not friends
        
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

ZERO = timedelta(0)

class UTC(tzinfo):
  def utcoffset(self, dt):
    return ZERO
  def tzname(self, dt):
    return "UTC"
  def dst(self, dt):
    return ZERO

def post_update(request, goal):
    UpdateForm = modelform_factory(Update, fields = ('content', 'completion'), widgets = {'content': forms.Textarea}, labels = {'content' : ''})
    
    current_user = get_object_or_404(LyfeUser, pk=request.user.username)
    
    updateForm = UpdateForm(request.POST, request.FILES)
    
    if updateForm.is_valid():
        update = updateForm.save(commit=False)
        updatedGoal = Goal.objects.get(pk = goal)
            
        if update.completion:
            updatedGoal.status = 1 # complete
            updatedGoal.completion_date = date.today()
            pointTotal = updatedGoal.base_points + updatedGoal.friend_points + updatedGoal.time_points
            current_user.cur_points += pointTotal
            current_user.total_points += pointTotal
            
            updatedGoal.save()
            current_user.save()
            
            try:
                nextGoal = Goal.objects.get(goal_id = updatedGoal.goal_id, order_num = updatedGoal.order_num+1)
                nextGoal.status = 0 # active
                nextGoal.save()
            except Goal.DoesNotExist:
                pass
            
        else:
            try:
                lastupdate = Update.objects.filter(goal_id = updatedGoal.pk).latest('timestamp')
                difference = datetime.now(UTC()) - lastupdate.timestamp
                if difference.total_seconds() < 3600:
                    #TODO show this: raise forms.ValidationError("You can't post an update until an hour after your last update!")  
                    
                    return HttpResponseRedirect(reverse('core.views.dashboard'))
            except Update.DoesNotExist:
                pass
            
            updatedGoal.time_points += 1
            updatedGoal.save()
        
        update.goal_id = updatedGoal
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
            goal.goal_id = goalGroup
            goal.start_date = date.today()
            if goal.difficulty == 0:
                goal.base_points = 10
            elif goal.difficulty == 1:
                goal.base_points = 20
            elif goal.difficulty == 2:
                goal.base_points = 40
            
            goal.save()
    
    return HttpResponseRedirect(reverse('core.views.dashboard'))

def delete_goal(request, goal):
    deletegoal = Goal.objects.get(pk = goal)
    
    if deletegoal.status == -1:
        ''' update order_num indices as appropriate '''
        index = deletegoal.order_num + 1
        processing = True
        
        while processing:
            try:
                updategoal = Goal.objects.get(goal_id = deletegoal.goal_id, order_num = index)
                updategoal.order_num -= 1
                index += 1
                updategoal.save()
            except Goal.DoesNotExist:
                processing = False
        
        deletegoal.delete()
    
    return HttpResponseRedirect(reverse('core.views.dashboard'))

def flip_goals(request, goal, neworder_num):
    try:
        goalone = Goal.objects.get(pk = goal)
        goaltwo = Goal.objects.get(goal_id = goalone.goal_id, order_num = neworder_num)
        
        oldorder_num = goalone.order_num
        
        if goaltwo.status == 0: # active and future flipping
            goalone.status = 0
            goaltwo.status = -1
            
        goaltwo.order_num = -1
        goaltwo.save()
        goalone.order_num = neworder_num
        goalone.save()
        goaltwo.order_num = oldorder_num
        goaltwo.save()
        
    except Goal.DoesNotExist:
        processing = False
        
    return HttpResponseRedirect(reverse('core.views.dashboard'))

def add_actionitem(request, goalgroup):
    GoalForm = modelform_factory(Goal, fields=('name', 'difficulty'), labels = {'name' : 'description'})
    
    newGoal = GoalForm(request.POST, request.FILES)
    if newGoal.is_valid():
        goal = newGoal.save(commit=False)
        goal.goal_id_id = goalgroup
        
        try:
            Goal.objects.get(goal_id_id = goalgroup, status = 0)
            goal.status = -1 #future
        except Goal.DoesNotExist:
            goal.status = 0 # active
            
        if goal.difficulty == 0:
            goal.base_points = 10
        elif goal.difficulty == 1:
            goal.base_points = 20
        elif goal.difficulty == 2:
            goal.base_points = 40
        
        goal.order_num = len(list(Goal.objects.filter(goal_id_id=goalgroup)))
    
        goal.save()
        
    return HttpResponseRedirect(reverse('core.views.dashboard'))

def add_friendpoint(request, goal):
    current_user = get_object_or_404(LyfeUser, pk=request.user.username)
    goal = Goal.objects.get(pk = goal)
    lyfeuser = goal.goal_id.ownerid
    
    # check for cheating
    if current_user.pk != lyfeuser.pk:
        if current_user.last_fp_given:
            difference = datetime.now(UTC()) - current_user.last_fp_given
            if difference.total_seconds() < 3600:
            
                return HttpResponseRedirect(reverse('core.views.profile', kwargs={'username' : lyfeuser.username}))
            
        current_user.last_fp_given = datetime.now()
        current_user.save()
        
        goal.friend_points += 1
        goal.save()
        
    return HttpResponseRedirect(reverse('core.views.profile', kwargs={'username' : lyfeuser.username}))

class MyRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')        

    def save(self,commit = True):   
        newuser = super(MyRegistrationForm, self).save(commit = False)
        if commit:
            newuser.save()
            newlyfeuser = LyfeUser(username = newuser.username, user_id = newuser.pk)
            newlyfeuser.save()
        
        return newuser

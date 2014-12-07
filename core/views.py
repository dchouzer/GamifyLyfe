from datetime import date, datetime, tzinfo, timedelta

from django import forms
from django.db import IntegrityError
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.forms.models import ModelForm, inlineformset_factory, modelform_factory

from core.forms import DocumentForm
from core.models import LyfeUser, GoalGroup, Goal, Group, Membership, ShareSetting, Reward, RewardTransaction, Friend, Update, Comment

def home(request):
    """ Redirects the user to the login page or to the dashboard depending on authentication """
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse(('core.views.dashboard')))
    else:
        return HttpResponseRedirect(reverse('django.contrib.auth.views.login'))

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
    return HttpResponseRedirect(reverse('django.contrib.auth.views.login'))

def dashboard(request):
    """ The main homepage for managing goals """
    lyfeuser = get_object_or_404(LyfeUser, pk=request.user.username)
    goalitems = make_goalitems(lyfeuser, list(GoalGroup.objects.filter(ownerid=lyfeuser.pk)))
    activegoalitems = goalitems[0]
    inactivegoalitems = goalitems[1]
    
    # friend requests
    friend_requests = list(Friend.objects.filter(recipient_id=lyfeuser, is_approved=False))
    
    # friends
    friends = list(Friend.objects.filter(requester_id=lyfeuser, is_approved=True))
    
    # groups and membership requests
    memberships = Membership.objects.filter(user_id=lyfeuser, accepted=True)
    groups = []
    membership_requests = []
    
    for membership in memberships:
        groups.append(membership.group_id)
        # if the user owns groups, show membership requests
        if membership.group_id.creator_id == lyfeuser:
            membership_requests.extend(Membership.objects.filter(group_id=membership.group_id, accepted=False))
    
    # newsfeed
    friendIDs = []
    friendIDs.append(lyfeuser.pk) # you can see your own updates
    for friend in friends:
        friendIDs.append(friend.recipient_id)
        
    updates = list(Update.objects.filter(user_id_id__in=friendIDs).order_by('timestamp').reverse()[:15]) 
    # replace this awkward comment correction with notification model in the future
    for update in updates:
        if not update.public and update.user_id != lyfeuser:
            updates.remove(update)
    newsfeed = make_newsfeed(updates, lyfeuser, private=True, friends=True, gids=groups)
    
    # update form
    updateform = modelform_factory(Update, fields=('content', 'completion'), widgets={'content': forms.Textarea(attrs={'placeholder' : 'REQUIRED: Description. Can only post an update once every 30 minutes.'})})
    
    # goal category form
    goal_groupform = modelform_factory(GoalGroup, fields=('name', 'sharee'))
    goal_formset = inlineformset_factory(GoalGroup, Goal, extra=1, fields=('name', 'difficulty'), can_delete=False, labels={'name' : 'Initial goal'})
      
    # goal form
    actionitem_form = modelform_factory(Goal, fields=('name', 'difficulty'))
    
    # comment form
    commentForm = modelform_factory(Comment, fields=('content',), widgets={'content': forms.TextInput(attrs={'placeholder' : 'Add comment'})})
    
    # group form
    groupForm = modelform_factory(Group, fields=('name', 'description', 'logo'))
    
    return render_to_response('core/dashboard.html',
        { 'lyfeuser' : lyfeuser, 'activegoalitems' : activegoalitems, 'inactivegoalitems' : inactivegoalitems, 'friend_requests' : friend_requests, 'membership_requests' : membership_requests, 'friends' : friends, 'groups' : groups, 'updateform' : updateform, 'newsfeed' : newsfeed, 'goal_groupform' : goal_groupform, 'goal_formset' : goal_formset, 'actionitem_form' : actionitem_form, 'commentForm' : commentForm, 'groupForm' : groupForm},
        context_instance=RequestContext(request))

""" HELPER METHODS """
def get_groups(lyfeuser):
    """ Get a user's groups """
    memberships = Membership.objects.filter(user_id=lyfeuser, accepted=True)
    groups = []
    
    for membership in memberships:
        groups.append(membership.group_id)
        
    return groups
    
def make_goalitems(current_user, goalgroups):
    """ Get a user's active and inactive goalitem tuples: goalgroup, goals and newsfeeds, and whether any groups are being explicitly shared with """
    activegoalitems = []
    inactivegoalitems = []
    
    for goalgroup in goalgroups:
        sharegroups = (len(ShareSetting.objects.filter(goalgroup_id=goalgroup)) > 0)
            
        goals = Goal.objects.filter(goalgroup_id=goalgroup.pk).order_by('order_num')
        goalobject = []
        for goal in goals:
            # this logic isn't needed, it's already accounted for
            tuple = (goal, make_newsfeed(Update.objects.filter(goal_id=goal, public=True), private=True, current_user=current_user, friends = True, gids = get_groups(current_user)))
            goalobject.append(tuple)
            
        goalitem = (goalgroup, goalobject, sharegroups)

        try:
            Goal.objects.get(goalgroup_id=goalgroup.pk, status=0)
            activegoalitems.append(goalitem)
        except Goal.DoesNotExist:
            inactivegoalitems.append(goalitem)
    
    return (activegoalitems, inactivegoalitems)
    
def make_newsfeed(updates, current_user=None, private=False, friends=False, gids=None):
    """ Filters updates based on updates, sharing settings, environment and attaches comments """
    newsfeed = []
    
    # Terrible logical making newsfeed based on settings and the environment in which it's being viewed... there's probably a much better way to do this.
    for newsitem in updates:
        if newsitem.goal_id:
            goalgroup = newsitem.goal_id.goalgroup_id

                    
            if (goalgroup.sharee == 1) or (private and newsitem.user_id == current_user) or (friends and goalgroup.sharee == 2):
                comments = Comment.objects.filter(update_id=newsitem).order_by('timestamp')
                tuple = (newsitem, comments)
                newsfeed.append(tuple)
            else:           
                if gids:
                    try:
                        ShareSetting.objects.filter(group_id__in=gids, goalgroup_id=goalgroup)
                        comments = Comment.objects.filter(update_id=newsitem).order_by('timestamp')
                        tuple = (newsitem, comments)
                        newsfeed.append(tuple)
                    except ShareSetting.DoesNotExist:
                        pass
        else:
            comments = Comment.objects.filter(update_id=newsitem).order_by('timestamp')
            tuple = (newsitem, comments)
            newsfeed.append(tuple)
            
    return newsfeed

def post_content_update(user, content, public=True, goal=None):
    """ Create an update """
    update = Update(user_id=user, content=content)
    update.goal_id = goal
    update.public = public
    update.save()
    
# for dealing with database timezone errors
ZERO = timedelta(0)
class UTC(tzinfo):
  def utcoffset(self, dt):
    return ZERO
  def tzname(self, dt):
    return "UTC"
  def dst(self, dt):
    return ZERO
    
""" AVATAR """
# can actually just merge this with dashboard page like in the groups page
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

""" UPDATES """
def post_update(request, goal):
    UpdateForm = modelform_factory(Update, fields=('content', 'completion'), widgets={'content': forms.Textarea}, labels={'content' : ''})
    
    current_user = get_object_or_404(LyfeUser, pk=request.user.username)
    
    updateForm = UpdateForm(request.POST, request.FILES)

    if updateForm.is_valid():
        updatedGoal = Goal.objects.get(pk=goal)
        update = updateForm.save(commit=False)
        
        # allow goal updates to complete
        if update.completion:
            updatedGoal.status = 1 # complete
            updatedGoal.completion_date = date.today()
            pointTotal = updatedGoal.base_points + updatedGoal.friend_points + updatedGoal.time_points
            current_user.cur_points += pointTotal
            current_user.total_points += pointTotal
          
            updatedGoal.save()
            current_user.save()
            
            try:
                nextGoal = Goal.objects.get(goalgroup_id=updatedGoal.goalgroup_id, order_num=updatedGoal.order_num + 1)
                nextGoal.status = 0  # active
                nextGoal.start_date = date.today()
                nextGoal.save()
            except Goal.DoesNotExist:
                pass
                
        # check non-goal updates for time. If valid, post and give time points
        else:
            try:
                lastupdate = Update.objects.filter(goal_id=updatedGoal.pk).latest('timestamp')
                difference = datetime.now(UTC()) - lastupdate.timestamp
                if difference.total_seconds() < 1800: 
                    return HttpResponseRedirect(reverse('core.views.dashboard'))
            except Update.DoesNotExist:
                pass
            
            updatedGoal.time_points += 1
            updatedGoal.save()
        
        update.goal_id = updatedGoal
        update.user_id_id = request.user.username
        update.save()
            
    return HttpResponseRedirect(reverse('core.views.dashboard'))

def add_comment(request, update):
    current_user = get_object_or_404(LyfeUser, pk=request.user.username)
    CommentForm = modelform_factory(Comment, fields=('content',), labels={'content' : 'comment'})
    newComment = CommentForm(request.POST, request.FILES)
    commentedUpdate = Update.objects.get(id=update)
    
    if newComment.is_valid():
        comment = newComment.save(commit=False)
        post_content_update(commentedUpdate.user_id, current_user.username + " commented on your update: \"" + commentedUpdate.content + "\" with \"" + comment.content + "\"", False, commentedUpdate.goal_id)
        comment.creator_uid = current_user
        comment.update_id = commentedUpdate
        comment.save()
        
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
""" GOALS """    
def add_goal(request):
    GoalGroupForm = modelform_factory(GoalGroup, fields=('name', 'sharee'))
    GoalFormSet = inlineformset_factory(GoalGroup, Goal, extra=1, fields=('name', 'difficulty'), can_delete=False)
    
    goalGroupForm = GoalGroupForm(request.POST)
    goalGroup = goalGroupForm.save(commit=False)
    goalGroup.ownerid_id = request.user.username
    goalGroup.save()
    
    goalFormSet = GoalFormSet(request.POST, request.FILES)
    if goalFormSet.is_valid():
        for goalForm in goalFormSet:
            goal = goalForm.save(commit=False)
            goal.goalgroup_id = goalGroup
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
    deletegoal = Goal.objects.get(pk=goal)
    
    if deletegoal.status == -1:
        # updateS order_num indices as appropriate
        index = deletegoal.order_num + 1
        processing = True
        
        while processing:
            try:
                updategoal = Goal.objects.get(goalgroup_id=deletegoal.goalgroup_id, order_num=index)
                updategoal.order_num -= 1
                index += 1
                updategoal.save()
            except Goal.DoesNotExist:
                processing = False
        
        deletegoal.delete()
    
    return HttpResponseRedirect(reverse('core.views.dashboard'))

def delete_goalgroup(request, goalgroup):
    deletegroup = GoalGroup.objects.get(pk=goalgroup)
    deletegroup.delete()
    
    return HttpResponseRedirect(reverse('core.views.dashboard'))

def flip_goals(request, goal, neworder_num):
    """ Flips the order of two goals """
    try:
        goalone = Goal.objects.get(pk=goal)
        goaltwo = Goal.objects.get(goalgroup_id=goalone.goalgroup_id, order_num=neworder_num)
        
        oldorder_num = goalone.order_num
        newstatus = goaltwo.status
        
        if goalone.status == 0 and goaltwo.start_date == None:
            goaltwo.start_date = date.today()
            
        elif goaltwo.status == 0 and goalone.start_date == None:
            goalone.start_date = date.today()
            
        goaltwo.status = goalone.status
        goaltwo.order_num = -1
        goaltwo.save()
        goalone.status = newstatus
        goalone.order_num = neworder_num
        goalone.save()
        
        # in case of key checking
        goaltwo.order_num = oldorder_num
        goaltwo.save()
        
    except Goal.DoesNotExist:
        processing = False
        
    return HttpResponseRedirect(reverse('core.views.dashboard'))

def add_actionitem(request, goalgroup):
    GoalForm = modelform_factory(Goal, fields=('name', 'difficulty'), labels={'name' : 'description'})
    
    newGoal = GoalForm(request.POST, request.FILES)
    if newGoal.is_valid():
        goal = newGoal.save(commit=False)
        goal.goalgroup_id_id = goalgroup
        
        try:
            Goal.objects.get(goalgroup_id_id=goalgroup, status=0)
            goal.status = -1  # future
        except Goal.DoesNotExist:
            goal.status = 0  # active
            goal.start_date = date.today()
            
        if goal.difficulty == 0:
            goal.base_points = 10
        elif goal.difficulty == 1:
            goal.base_points = 20
        elif goal.difficulty == 2:
            goal.base_points = 40
        
        goal.order_num = len(list(Goal.objects.filter(goalgroup_id_id=goalgroup)))
    
        goal.save()
        
    return HttpResponseRedirect(reverse('core.views.dashboard'))

""" SHARING """
def share_settings(request, goalgroup):
    """ Allows the user to modify who gets goal updates from a goal category """
    current_user = LyfeUser.objects.get(pk=request.user.username)
    
    goalGroup = GoalGroup.objects.get(id=goalgroup)
    goalGroupForm = modelform_factory(GoalGroup, fields=('sharee',))
    editGoalGroupForm = goalGroupForm(instance=goalGroup)

    shareSettingForm = modelform_factory(ShareSetting, fields=('group_id',))
    
    groups = get_shareable_groups(current_user, goalgroup)
    shareSettingForm.base_fields['group_id'].queryset = groups
    
    shareSettings = ShareSetting.objects.filter(goalgroup_id=goalGroup)
    showGroups = len(groups) > 0
    
    return render_to_response('core/sharesettings.html',
    { 'goalGroup' : goalGroup, 'shareSettings' : shareSettings, 'editGoalGroupForm' : editGoalGroupForm, 'showGroups' : showGroups, 'shareSettingForm' : shareSettingForm },
    context_instance=RequestContext(request))
    
def get_shareable_groups(current_user, goalgroup):
    """ Returns the queryset of a user's groups that they are not currently sharing these goal updates with """
    memberof = Membership.objects.filter(user_id=current_user).values_list('group_id', flat=True)
    groupids = []
    
    for group in memberof:
        try:
            ShareSetting.objects.get(goalgroup_id_id=goalgroup, group_id=group)
        except ShareSetting.DoesNotExist:
            groupids.append(group)
            
    return Group.objects.filter(id__in=groupids)
    
def edit_sharee(request, goalgroup):
    goalGroup = GoalGroup.objects.get(id=goalgroup)
    
    goalGroupForm = modelform_factory(GoalGroup, fields=('sharee',))
    editGoalGroupForm = goalGroupForm(request.POST, instance=goalGroup)
    editedGoalGroup = editGoalGroupForm.save(commit=False)
    editedGoalGroup.save()
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
def add_share_setting(request, goalgroup):
    goalGroup = GoalGroup.objects.get(id=goalgroup)
    
    shareSettingForm = modelform_factory(ShareSetting, fields=('group_id',))
    shareForm = shareSettingForm(request.POST)
    if shareForm.is_valid():
        newShareSetting = shareForm.save(commit=False)
        newShareSetting.goalgroup_id = goalGroup
        newShareSetting.save()
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def add_all_sharesettings(request, goalgroup):
    """ Adds sharing to all the groups that the user is not currently sharing these goal updates with """
    goalGroup = GoalGroup.objects.get(id=goalgroup)
    current_user = LyfeUser.objects.get(pk=request.user.username)
    
    groups = get_shareable_groups(current_user, goalgroup)
    for group in groups:
        newSetting = ShareSetting(goalgroup_id=goalGroup, group_id=group)
        newSetting.save()
        
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        
def delete_share_setting(request, sharesetting):
    shareSetting = ShareSetting.objects.get(id=sharesetting)
    shareSetting.delete()
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def profile(request, username):
    """ The public's view of a user """
    try:
        current_user = LyfeUser.objects.get(pk=request.user.username)
    except LyfeUser.DoesNotExist:
        current_user = None
        
    lyfeuser = get_object_or_404(LyfeUser, pk=username)
    addfriend = False
    friendship = False
    friendpoints = False
                    
    if current_user != None and current_user.pk != lyfeuser.pk:
        try:
            friendship = Friend.objects.get(requester_id=current_user, recipient_id=lyfeuser)
            # user has friend request or accepted other user
            if friendship.is_approved:
                friendship = True
        except Friend.DoesNotExist:
            addfriend = True
            # not friends or friend requested
           
        # check if enough time has passed to give friendpoints again      
        if current_user.last_fp_given:
            difference = datetime.now(UTC()) - current_user.last_fp_given
            friendpoints = difference.total_seconds() > 3600
        else:
            friendpoints = True
    
    validGoalGroups = []
    goalgroups = list(GoalGroup.objects.filter(ownerid=lyfeuser.pk))
    private = (current_user == lyfeuser)
    
    for goalgroup in goalgroups:
        if goalgroup.sharee == 1 or private or (friendship and goalgroup.sharee == 2):
            validGoalGroups.append(goalgroup)
        else:        
            memberof = Membership.objects.filter(user_id=current_user).values_list('group_id', flat=True)
            
            for group in memberof:
                try:
                    ShareSetting.objects.get(goalgroup_id_id=goalgroup, group_id=group)
                    validGoalGroups.append(goalgroup)
                except ShareSetting.DoesNotExist:
                    pass
                    
    goalitems = make_goalitems(current_user, validGoalGroups)  
    activegoalitems = goalitems[0]
    inactivegoalitems = goalitems[1]
    
    # friends
    friends = list(Friend.objects.filter(requester_id=lyfeuser, is_approved=True))
    
    # groups
    groups = get_groups(lyfeuser)
    
    # newsfeed
    updates = Update.objects.filter(user_id=lyfeuser).order_by('timestamp').reverse()[:15]
    newsfeed = make_newsfeed(updates, current_user, private=(lyfeuser == current_user), friends=friendship, gids=get_groups(current_user))
    
    # comment form
    commentForm = modelform_factory(Comment, fields=('content',), labels={'content' : 'comment'}, widgets={'content': forms.TextInput(attrs={'placeholder' : 'Add comment'})})
    
    return render_to_response('core/profile.html',
    { 'lyfeuser' : lyfeuser, 'activegoalitems' : activegoalitems, 'inactivegoalitems': inactivegoalitems, 'addfriend' : addfriend, 'friendship' : friendship, 'friends' : friends, 'groups' : groups, 'newsfeed' : newsfeed, 'friendpoints' : friendpoints, 'commentForm' : commentForm },
    context_instance=RequestContext(request))
        
""" PROFILE """   
def addfriend(request, username):
    current_user = get_object_or_404(LyfeUser, pk=request.user.username)
    lyfeuser = get_object_or_404(LyfeUser, pk=username)
    try:
        friend_request = Friend(requester_id=current_user, recipient_id=lyfeuser)
        try:
            original_request = Friend.objects.get(requester_id=lyfeuser, recipient_id=current_user)
            post_content_update(lyfeuser, lyfeuser.username + " is now friends with " + current_user.username + "!")
            post_content_update(current_user, current_user.username + " is now friends with " + lyfeuser.username + "!")

            original_request.is_approved = True
            friend_request.is_approved = True
            
            original_request.save()
        except Friend.DoesNotExist:
            pass
            
        friend_request.save()
        
    except IntegrityError:
        pass  # already requested
        
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
def unfriend(request, username):
    current_user = get_object_or_404(LyfeUser, pk=request.user.username)
    lyfeuser = get_object_or_404(LyfeUser, pk=username)
    
    try:
        friend_request = Friend.objects.get(requester_id=current_user, recipient_id=lyfeuser)
        try:
            original_request = Friend.objects.get(requester_id=lyfeuser, recipient_id=current_user)
            original_request.delete()
        except Friend.DoesNotExist:
            pass  # friend request not accepted
            
        friend_request.delete()
        
    except Friend.DoesNotExist:
        # denying friend request
        try:
            original_request = Friend.objects.get(requester_id=lyfeuser, recipient_id=current_user)
            original_request.delete()
        except Friend.DoesNotExist:
            pass
        
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def add_friendpoint(request, goal):
    current_user = get_object_or_404(LyfeUser, pk=request.user.username)
    goal = Goal.objects.get(pk=goal)
    lyfeuser = goal.goalgroup_id.ownerid
    
    # check for cheating
    if current_user.pk != lyfeuser.pk:
        if current_user.last_fp_given:
            difference = datetime.now(UTC()) - current_user.last_fp_given
            if difference.total_seconds() < 600:
            
                return HttpResponseRedirect(reverse('core.views.profile', kwargs={'username' : lyfeuser.username}))
            
        current_user.last_fp_given = datetime.now()
        current_user.save()
        
        goal.friend_points += 1
        goal.save()
        
    return HttpResponseRedirect(reverse('core.views.profile', kwargs={'username' : lyfeuser.username}))

""" GROUPS """
def group(request, group):
    try:
        current_user = LyfeUser.objects.get(pk=request.user.username)
    except LyfeUser.DoesNotExist:
        current_user = None
        
    group = get_object_or_404(Group, pk=group)
    memberships = Membership.objects.filter(group_id=group)
    
    members = []
    user_ismember = None
    requested = False
    
    for membership in memberships:
        if membership.accepted == True:
            members.append(membership.user_id)
        if current_user == membership.user_id:
            user_ismember = membership
            requested = True
    
    # logoform    
    logoform = DocumentForm()

    # newsfeed
    updates = Update.objects.filter(user_id__in=members).order_by('timestamp').reverse()[:15]
    newsfeed = make_newsfeed(updates, current_user, gids=(group,))
    
    # comment form
    commentForm = modelform_factory(Comment, fields=('content',), labels={'content' : 'comment'}, widgets={'content': forms.TextInput(attrs={'placeholder' : 'Add comment'})})
    
    # edit group form
    groupForm = modelform_factory(Group, fields=('name', 'description'))
    editGroupForm = groupForm(instance=group)
        
    return render_to_response('core/group.html',
    { 'group' : group, 'user_ismember' : user_ismember, 'memberships' : memberships, 'members' : members, 'newsfeed' : newsfeed, 'commentForm' : commentForm, 'logoform' : logoform, 'editGroupForm' : editGroupForm, 'requested' : requested},
    context_instance=RequestContext(request))

def new_group_logo(request, group):
    group = Group.objects.get(id=group)
    
    form = DocumentForm(request.POST, request.FILES)
    if form.is_valid():
        group.logo = request.FILES['docfile']
        group.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def edit_group(request, group):
    current_user = LyfeUser.objects.get(pk=request.user.username)
    group = Group.objects.get(id=group)
    
    GroupForm = modelform_factory(Group, fields=('name', 'description'))
    groupForm = GroupForm(request.POST, instance=group)
    editedGroup = groupForm.save(commit=False)
    editedGroup.save()
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def delete_group(request, group):
    current_user = LyfeUser.objects.get(pk=request.user.username)
    group = Group.objects.get(id=group)
    
    # permission check
    if current_user == group.creator_id:
        group.delete()
    
    return HttpResponseRedirect(reverse('core.views.dashboard'))

def add_group(request):
    current_user = LyfeUser.objects.get(pk=request.user.username)
    
    GroupForm = modelform_factory(Group, fields=('name', 'description', 'logo'))
    
    newGroup = GroupForm(request.POST, request.FILES)
    if newGroup.is_valid():
        group = newGroup.save(commit=False)
        group.creator_id = current_user
        group.save()
        
        defaultMembership = Membership(group_id=group, user_id=current_user)
        defaultMembership.save()
        
    return HttpResponseRedirect(reverse('core.views.dashboard'))

def add_membership(request, group):
    current_user = LyfeUser.objects.get(pk=request.user.username)
    
    newMembership = Membership(user_id=current_user, group_id_id=group, accepted=False)
    newMembership.save()
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
def approve_membership(request, membership):
    membership = Membership.objects.get(id=membership)
    
    post_content_update(membership.user_id, membership.user_id.username + " joined group: " + membership.group_id.name + "!")
    membership.accepted = True
    membership.save()
        
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def deny_membership(request, membership):
    membership = Membership.objects.get(id=membership)
    
    # remove sharing with that group
    if membership.accepted:
        goalGroups = GoalGroup.objects.filter(ownerid=membership.user_id)
        shareSettings = ShareSetting.objects.filter(group_id=membership.group_id, goalgroup_id__in=goalGroups)
        for setting in shareSettings:
            setting.delete()
        
    membership.delete()
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
""" REWARDS """
def rewards(request):
    current_user = LyfeUser.objects.get(pk=request.user.username)
    rewards = Reward.objects.filter(user_id=current_user)
    
    rewardform = modelform_factory(Reward, fields=('description', 'worth', 'multiples'))
    
    purchasedRewards = RewardTransaction.objects.filter(reward_id__in=rewards).order_by('timestamp').reverse()[:10]
    
    return render_to_response('core/rewards.html',
    { 'rewards' : rewards, 'rewardform' : rewardform, 'purchasedRewards' : purchasedRewards, 'current_points' : current_user.cur_points },
    context_instance=RequestContext(request))
    
def add_reward(request):
    current_user = LyfeUser.objects.get(pk=request.user.username)
    
    RewardForm = modelform_factory(Reward, fields=('description', 'worth', 'multiples'))
    rewardForm = RewardForm(request.POST)
    reward = rewardForm.save(commit=False)
    reward.user_id = current_user
    reward.save()
    
    return HttpResponseRedirect(reverse('core.views.rewards'))
    
def buy_reward(request, reward):
    current_user = LyfeUser.objects.get(pk=request.user.username)
    reward = Reward.objects.get(id=reward)
    error_messages = ""
    
    if current_user.cur_points >= reward.worth:
        post_content_update(current_user, current_user.username + " bought reward: " + reward.description + " for " + str(reward.worth) + " points!")
        
        current_user.cur_points -= reward.worth
        newTransaction = RewardTransaction(reward_id=reward)
        current_user.save()
        newTransaction.save()
        
        if not reward.multiples:
            reward.retired = True
            reward.save()
    else:
        error_messages = "You don't have enough points!"
        # , kwargs={'error_message' : error_message} TODO: look into optional kwargs
    return HttpResponseRedirect(reverse('core.views.rewards'))
  
def retire_reward(request, reward):
    reward = Reward.objects.get(id=reward)
    
    reward.retired = True
    reward.save()
  
    return HttpResponseRedirect(reverse('core.views.rewards'))
      
""" FORMS """
class MyRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')        

    def save(self, commit=True):   
        newuser = super(MyRegistrationForm, self).save(commit=False)
        if commit:
            newuser.save()
            newlyfeuser = LyfeUser(username=newuser.username, user_id=newuser.pk)
            newlyfeuser.save()
        
        return newuser

from django.db import models
from django.contrib.auth.models import User

# https://docs.djangoproject.com/en/1.7/ref/models/fields/
# Django adds primary key for each table automatically, the id field
# http://www.tangowithdjango.com/book/chapters/models.html
# id = models.AutoField(primary_key=True)

# null=True, blank=True, max_length=#, primary_key=True, unique = True

"""
example of an enum:

class Student(models.Model):
    FRESHMAN = 'FR'
    SOPHOMORE = 'SO'
    JUNIOR = 'JR'
    SENIOR = 'SR'
    YEAR_IN_SCHOOL_CHOICES = (
        (FRESHMAN, 'Freshman'),
        (SOPHOMORE, 'Sophomore'),
        (JUNIOR, 'Junior'),
        (SENIOR, 'Senior'),
    )
    year_in_school = models.CharField(max_length=2,
                                      choices=YEAR_IN_SCHOOL_CHOICES,
                                      default=FRESHMAN)

    def is_upperclass(self):
        return self.year_in_school in (self.JUNIOR, self.SENIOR)
        
"""
class LyfeUser(models.Model):
    # default primary key id = lyfeuserID
    username = models.CharField(max_length=30, primary_key = True)
    cur_points = models.IntegerField(default = '0')
    total_points = models.IntegerField(default = '0')
    account_creation_date = models.DateField(auto_now_add = True)
    last_active_date = models.DateField(auto_now=True)
    last_fp_given = models.DateTimeField(null=True, blank=True)
    avatar = models.FileField(default='./default.jpg')
    user = models.ForeignKey(User, unique=True)
    
    class Meta:
        # Without being set, the default table name will start with the app
        # name followed by '_'; we just want the simple table names here:
        db_table = u'LyfeUser'
    def __unicode__(self):
        # Allow objects to be shown using primary key, e.g., 'The Edge'
        # instead of 'Bar Object':
        #return self.pk
        return self.username

class GoalGroup(models.Model):
    # default primary key id = goalgroupID
    ownerid = models.ForeignKey(LyfeUser)
    name = models.CharField(max_length=30)
    
    PRIVATE = 0
    PUBLIC = 1
    FRIENDS = 2
    DIFF_CHOICES = (
        (PRIVATE, 'private'),
        (PUBLIC, 'public'),
        (FRIENDS, 'friends')
    )
    sharee = models.IntegerField(choices=DIFF_CHOICES, default=PUBLIC)
    
    class Meta:
        db_table = u'GoalGroup'
    def __unicode__(self):
        return self.name

class Goal(models.Model):
    goalgroup_id = models.ForeignKey(GoalGroup)
    order_num = models.IntegerField(default = '0') # 0 to multiple
    base_points = models.IntegerField()
    friend_points = models.IntegerField(default = '0')
    time_points = models.IntegerField(default = '0')
    name = models.CharField(max_length=100)
    
    ACTIVE = 0
    FUTURE = -1
    COMPLETED = 1
    STATUS_CHOICES = (
        (ACTIVE, 'active'),
        (FUTURE, 'future'),
        (COMPLETED, 'completed')
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=ACTIVE)
    
    EASY = 0
    MODERATE = 1
    HARD = 2
    DIFF_CHOICES = (
        (EASY, 'easy'),
        (MODERATE, 'moderate'),
        (HARD, 'hard')
    )
    difficulty = models.IntegerField(choices=DIFF_CHOICES, default=EASY)
    est_date = models.DateField(auto_now_add = True)
    start_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null = True, blank=True)
    
    class Meta:
        unique_together = ('goalgroup_id', 'order_num')
        db_table = u'Goal'
    def __unicode__(self):
        return self.name
        
class Group(models.Model):
    # default group id
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    creator_id = models.ForeignKey(LyfeUser)
    logo = models.FileField(default='./default-logo.jpg')
    
    class Meta:
        db_table = u'Group'
    def __unicode__(self):
        return self.name
        
class Membership(models.Model):
    group_id = models.ForeignKey(Group)
    user_id = models.ForeignKey(LyfeUser)
    accepted = models.BooleanField(default = True)
    
    class Meta:
        unique_together = ('group_id', 'user_id')
        db_table = u'Membership'
    def __unicode__(self):
        return self.user_id.username + " in " + self.group_id.name
        
class ShareSetting(models.Model):
    # should probably be named goalgroup_id, however everything will break if I change this again
    goalgroup_id = models.ForeignKey(GoalGroup) 
    group_id = models.ForeignKey(Group)
    
    class Meta:
        unique_together = ('goalgroup_id', 'group_id')
        db_table = u'ShareSetting'
    def __unicode__(self):
        return self.goalgroup_id.name + " with " + self.group_id.name
        
class Reward(models.Model):
    # default reward id
    user_id = models.ForeignKey(LyfeUser)
    description = models.CharField(max_length=50)
    worth = models.IntegerField()
    multiples = models.BooleanField(default = True)
    retired = models.BooleanField(default = False)
    
    class Meta:
        db_table = u'Reward'
    def __unicode__(self):
        return self.description
  
class RewardTransaction(models.Model):
    reward_id = models.ForeignKey(Reward)
    timestamp = models.DateTimeField(auto_now_add = True)

    class Meta:
        db_table = u'RewardTransaction'
    def __unicode__(self):
        return self.reward_id.description
  
class Friend(models.Model):
    # unfriend removes entries
    # inverse row entered after acceptance
    requester_id = models.ForeignKey(LyfeUser, related_name='requester_id')
    recipient_id = models.ForeignKey(LyfeUser, related_name='recipient_id')
    is_approved = models.BooleanField(default = False)
    request_time = models.DateTimeField(auto_now_add = True)
    approval_time = models.DateTimeField(null = True, blank = True)
    
    class Meta:
        unique_together = ('requester_id', 'recipient_id')
        db_table = u'Friend'
    def __unicode__(self):
        return self.requester_id.pk + "|" + self.recipient_id.pk
        
class Update(models.Model):
    # default update id
    user_id = models.ForeignKey(LyfeUser) # helpful for filtering updates
    goal_id = models.ForeignKey(Goal, null = True, blank = True)
    timestamp = models.DateTimeField(auto_now_add = True)
    content = models.CharField(max_length=500) #file ref or something?
    completion = models.BooleanField(default = False)
    public = models.BooleanField(default = True)
    
    class Meta:
        db_table = u'Update'
    def __unicode__(self):
        return self.content
        
class Comment(models.Model):
    creator_uid = models.ForeignKey(LyfeUser)
    update_id = models.ForeignKey(Update)
    timestamp = models.DateTimeField(auto_now_add = True)
    content = models.CharField(max_length=500) #file ref or something?
    
    class Meta:
        unique_together = ('creator_uid', 'update_id', 'timestamp')
        db_table = u'Comment'
    def __unicode__(self):
        return self.content
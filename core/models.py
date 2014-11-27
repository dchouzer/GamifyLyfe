from django.db import models

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
    #default primary key id = lyfeuserID
    username = models.CharField(max_length=20, primary_key = True)
    cur_points = models.IntegerField()
    total_points = models.IntegerField()
    account_creation_date = models.DateField(auto_now_add = True)
    last_active_date = models.DateField(auto_now=True)
    last_fp_given = models.DateField(null=True, blank=True)
    avatar = models.FileField(default='settings.MEDIA_ROOT/files/default.jpg')
   
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
    #default primary key id = goalgroupID
    ownerid = models.ForeignKey(LyfeUser)
    name = models.CharField(max_length=30)
    
    class Meta:
        db_table = u'GoalGroup'
    def __unicode__(self):
        return self.name

class Goal(models.Model):
    goal_id = models.ForeignKey(GoalGroup)
    order_num = models.IntegerField() # 0 to multiple
    base_points = models.IntegerField()
    friend_points = models.IntegerField(default = '0')
    time_points = models.IntegerField(default = '0')
    name = models.CharField(max_length=30)
    
    ACTIVE = 0
    FUTURE = -1
    COMPLETED = 1
    STATUS_CHOICES = (
        (ACTIVE, 'active'),
        (FUTURE, 'future'),
        (COMPLETED, 'completed')
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=FUTURE)
    
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
        unique_together = ('id', 'order_num')
        db_table = u'Goal'
    def __unicode__(self):
        return self.name
        
class Group(models.Model):
    #default primary key id
    name = models.CharField(max_length=20)
    creator_id = models.ForeignKey(LyfeUser)
    
    class Meta:
        db_table = u'Group'
    def __unicode__(self):
        return str(self.pk)
        
class Membership(models.Model):
    group_id = models.ForeignKey(Group)
    user_id = models.ForeignKey(LyfeUser)
    
    class Meta:
        unique_together = ('group_id', 'user_id')
        db_table = u'Membership'
    def __unicode__(self):
        return str(self.pk)
        
class ShareSetting(models.Model):
    goal_id = models.ForeignKey(GoalGroup)
    sharee = models.CharField(max_length=20, default = "public") 
    # public, private, friends, or a groupid, maxlength should be gid length or 7
    
    class Meta:
        unique_together = ('goal_id', 'sharee')
        db_table = u'ShareSetting'
    def __unicode__(self):
        return str(self.pk)
        
class Reward(models.Model):
    # default reward_id
    user_id = models.ForeignKey(LyfeUser)
    description = models.CharField(max_length=50)
    worth = models.IntegerField()
    
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
        return self.description
  
class Friend(models.Model):
    # unfriend removes entries
    requester_id = models.ForeignKey(LyfeUser, related_name='requester_id')
    recipient_id = models.ForeignKey(LyfeUser, related_name='recipient_id')
    is_approved = models.BooleanField(default = False)
    request_time = models.DateTimeField(auto_now_add = True)
    approval_time = models.DateTimeField(null = True, blank = True)
    
    # inverse row entered after acceptance
    class Meta:
        unique_together = ('requester_id', 'recipient_id')
        db_table = u'Friend'
    def __unicode__(self):
        return self.requester_id.pk + "|" + self.recipient_id.pk
        
class Update(models.Model):
    # default update ID
    user_id = models.ForeignKey(LyfeUser)
    goal_id = models.ForeignKey(GoalGroup)
    timestamp = models.DateTimeField(auto_now_add = True)
    content = models.CharField(max_length=50) #file ref or something?
    
    class Meta:
        db_table = u'Update'
    def __unicode__(self):
        return self.content
        
class Comment(models.Model):
    creator_uid = models.ForeignKey(LyfeUser)
    update_id = models.ForeignKey(Update)
    timestamp = models.DateTimeField(auto_now_add = True)
    content = models.CharField(max_length=50) #file ref or something?
    
    class Meta:
        unique_together = ('creator_uid', 'update_id', 'timestamp')
        db_table = u'Comment'
    def __unicode__(self):
        return self.content

#form model to store to media/files/CURRENTMONTH/CURRENTDATE
class Document(models.Model):
    docfile = models.FileField(upload_to='files/%Y/%m/%d')
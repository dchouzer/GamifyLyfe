from django.db import models

# https://docs.djangoproject.com/en/dev/ref/models/fields/
# Django adds primary key for each table automatically, the id field
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
   name = models.CharField(max_length=20)
   cur_points = models.IntegerField()
   total_points = models.IntegerField()
   account_creation_date = models.DateField(auto_now_add = True)
   last_active_date = models.DateField(auto_now=True)
   last_fp_given = models.DateField()
   avatar = models.ImageField()
   
   class Meta:
     # Without being set, the default table name will start with the app
     # name followed by '_'; we just want the simple table names here:
     db_table = u'LyfeUser'
   def __unicode__(self):
     # Allow objects to be shown using primary key, e.g., 'The Edge'
     # instead of 'Bar Object':
     return self.pk

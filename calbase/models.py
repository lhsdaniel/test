from django.db import models
from django.forms import ModelForm
from haystack.forms import SearchForm
from django.urls import reverse
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, timedelta, date 
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Field, Submit, ButtonHolder, MultiWidgetField, HTML
from field_history.tracker import FieldHistoryTracker
from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField
from dal import autocomplete
from crispy_forms.bootstrap import InlineField
from multiupload.fields import MultiFileField
# from crispy_forms.bootstrap import (
#     PrependedText, PrependedAppendedText, FormActions)

# Create your models here.




CONDITION_CHOCIES = (('new','new'), ('used','used'), ('lease/rental','lease/rental'))
LOCATION_CHOCIES = (('Cali','Cali'), ('MD','MD'), ('Out','Out'))
PICTURE_TAKEN_CHOICES = (('front','front'), ('back','back'))
DEPARTMENT_CHOICES = (('Battery','Battery'), ('EMC','EMC'), ('SAR/HAC','SAR/HAC'), ('Wireless','Wireless'))
CHECK_CHOICES = (('Yes','Yes'), ('Wavier List','Wavier List'))
FILE_DIRECTORY = "H:\Internal PCTEST Applications\intranet\LAB (testing)\Cal"




class Tests(models.Model):
	description = models.CharField(max_length=300)
	def __str__(self):
		return self.description

class Department(models.Model):
	name = models.CharField(max_length=300)
	def __str__(self):
		return self.name

class Manufacturer(models.Model):
	name = models.CharField(max_length=300)
	def __str__(self):
		return self.name

class Description(models.Model):
	name = models.CharField(max_length=300)
	def __str__(self):
		return self.name

class Equipment(models.Model):
	asset_number = models.CharField(max_length = 200, null=True, unique = True)
	serial_number = models.CharField(max_length = 200, null=True)
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
	manufacturer = models.ManyToManyField(Manufacturer)
	model = models.CharField(max_length = 200, null=True)
	description = models.ManyToManyField(Description)
	cal_interval = models.IntegerField(null=True, verbose_name = 'calibration interval (year)')
	initial_condition = models.CharField(max_length = 20, choices = CONDITION_CHOCIES, null=True)
	#cal_cert_location = models.FilePathField(path=FILE_DIRECTORY, match=".*\.(pdf)$", recursive=False, max_length = 300, null=True)
	manual_location = models.FileField(upload_to = 'manual/', null=True, blank = True)
	#picture = models.ImageField(upload_to = 'picture/%Y/%m/%d', null=True, blank=True)
	#picture_taken = models.CharField(max_length = 10, choices = PICTURE_TAKEN_CHOICES, null=True)
	initial_accessories_included = models.CharField(max_length = 200, null=True)
	placed_in_service_date = models.DateField(null=True)
	#is_in_service = models.BooleanField(default=False)
	used_for_test = models.ManyToManyField(Tests)
	location = models.CharField(max_length = 20, choices = LOCATION_CHOCIES, null=True)
	latest_calibration_date = models.DateField(null = True, blank = True)
	cal_due_date = models.DateField(null = True, blank = True, verbose_name = 'calibration due date')
	department = models.ManyToManyField(Department)
	is_flagged = models.CharField(max_length = 100, editable = False, blank = True, default = '')
	history = AuditlogHistoryField()
	
	

	def __str__(self):
		return self.asset_number
	def get_absolute_url(self):
		#return reverse('calbase:default_detail', args=[str(post.id,)])
		return "/calbase/equipment/%s/" % self.id

	
	#def latest_calibration_date(self):
	#	return self._latest_calibration_dat

	#@property
	#def cal_due_date(self):
	#	return self._cal_due_date

	def save(self, *args, **kwargs):
		super(Equipment, self).save(*args, **kwargs)
		if Equipment.objects.filter(id = self.id, flag__isnull = False).exists():
			Equipment.objects.filter(id = self.id).update(is_flagged = 'flag')
		else:
			Equipment.objects.filter(id = self.id).update(is_flagged = '')
	#def latest_calibration_date(self):
	#	return self._latest_calibration_date


class Attachment(models.Model):
    equip = models.ForeignKey(Equipment, on_delete = models.CASCADE)
    file = models.ImageField(upload_to = 'picture/%Y/%m/%d', null=True, blank=True)

class Calibration(models.Model):
	cal_asset = models.ForeignKey(Equipment, on_delete = models.CASCADE)
	cal_by = models.CharField(max_length = 200, null=True)
	cal_17025_check = models.CharField(max_length = 20, choices = CHECK_CHOICES, null=True)
	cal_date = models.DateField(null=True)
	mesure_uncertainty_included = models.BooleanField(default=False)
	a2la_Cal = models.BooleanField(default=False)
	qc_test_by = models.CharField(max_length = 200, null=True, blank = True)
	qc_test_date = models.DateField(null=True , blank = True)
	location = models.CharField(max_length = 20, choices = LOCATION_CHOCIES, null=True)
	cal_cert_location = models.FileField(upload_to = 'cal_cert/', null=True, blank = True)
	notes = models.CharField(max_length = 200, null=True)

	def is_overdue(self):
		return self.cal_date >= timezone.now() - datetime.timedelta(years = self.cal_asset.cal_interval)

	def calculate_due_date(self):
		d = self.cal_date
		try:
			return d.replace(year = d.year + self.cal_asset.cal_interval)
		except ValueError:
			return d + (date(d.year + self.cal_asset.cal_interval, 1, 1) - date(d.year, 1, 1))

	def save(self, *args, **kwargs):
		super(Calibration, self).save(*args, **kwargs)
		Equipment.objects.filter(id = self.cal_asset.id, calibration__isnull = 	False).distinct().update(latest_calibration_date = self.cal_date)
		Equipment.objects.filter(id = self.cal_asset.id, calibration__isnull = 	False).distinct().update(cal_due_date = self.calculate_due_date())
		Equipment.objects.filter(id = self.cal_asset.id).update(location = self.location)
		if not self.qc_test_by or not self.qc_test_date:
			equip = Equipment.objects.get(id = self.cal_asset.id)
			flag = Flag.objects.create(flag_asset = equip, flag_type = "qc", flag_content = "qc information for " + self.cal_date.strftime('%m/%d/%Y') + " calibration is not complete")
			flag.save()

class Flag(models.Model):
	flag_asset = models.ForeignKey(Equipment, on_delete = models.CASCADE)
	flag_type = models.CharField(max_length = 200, null=True)
	flag_content = models.CharField(max_length = 200, null=True)
	
	def __str__(self):
		return self.flag_type	

	def save(self, *args, **kwargs):
		super(Flag, self).save(*args, **kwargs)
		if Equipment.objects.filter(id = self.flag_asset.id, flag__isnull = False).exists():
			Equipment.objects.filter(id = self.flag_asset.id).update(is_flagged = 'flag')
		else:
			Equipment.objects.filter(id = self.flag_asset.id).update(is_flagged = '')

	def delete(self, *args, **kwargs):
		super(Flag, self).delete(*args, **kwargs)
		if Equipment.objects.filter(id = self.flag_asset.id, flag__isnull = False).exists():
			Equipment.objects.filter(id = self.flag_asset.id).update(is_flagged = 'flag')
		else:
			Equipment.objects.filter(id = self.flag_asset.id).update(is_flagged = '')


   
	

class EquipmentForm(ModelForm):
    placed_in_service_date=forms.DateField(widget=forms.SelectDateWidget)
    files = MultiFileField(min_num=1, max_num=10, max_file_size=1024*1024*5)
    used_for_test = forms.ModelMultipleChoiceField(
        queryset=Tests.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url='calbase:tests'),
    )
    manufacturer = forms.ModelChoiceField(
        queryset=Manufacturer.objects.all(),
        widget=autocomplete.ModelSelect2(url='calbase:manufacturer')
    )
    description = forms.ModelChoiceField(
        queryset=Description.objects.all(),
        widget=autocomplete.ModelSelect2(url='calbase:description')
    )
    department = forms.ModelMultipleChoiceField(
        queryset=Department.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url='calbase:department')
    )
    helper = FormHelper()
    helper.layout = Layout(
        Div(
            Div('asset_number',
                'serial_number', 
            	'manufacturer', 
            	'model',
            	'description',
		 		'cal_interval',
		  		'initial_condition',
		  		'location',
		   		'department',
		  	  	'manual_location',
		  	  	MultiWidgetField('placed_in_service_date', attrs=({'style': 'width: 25%; display: inline-block;'})),
		     	css_class='col-sm-4'),
            Div(
 
            	'initial_accessories_included', 
		  		'used_for_test',
		  		'files',

		   ButtonHolder(
    
    Submit('save', 'Save')
), css_class='col-sm-4'),  
        css_class='row-fluid'), 
    )

    class Meta:
        model = Equipment
        fields = ['asset_number', 'serial_number', 'manufacturer', 'model', 'description',
        'cal_interval', 'initial_condition',
        'initial_accessories_included', 'placed_in_service_date',
        'used_for_test','location', 'department', 'manual_location','files']

    def save(self, commit=True):
        instance = super(EquipmentForm, self).save(commit)
        for each in self.cleaned_data['files']:
            Attachment.objects.create(file=each, equip=instance)

        return instance


		
class EquipmentFormReadOnly(ModelForm):            
	placed_in_service_date=forms.DateField(widget=forms.SelectDateWidget)
	helper = FormHelper()
	helper.form_read_only = True
	helper.layout = Layout(
        Div(
            Div(
		  		Field('asset_number', readonly=True),
		  		Field('serial_number',  readonly=True),
		  		Field('manufacturer', readonly=True),
		  		Field('model', readonly=True),
		  		Field('description', readonly=True),
		  		Field('cal_interval', readonly=True),
		  		Field('initial_condition', readonly=True),
		  		Field('location', readonly=True),
 				MultiWidgetField('placed_in_service_date', readonly=True, attrs=({'style': 'width: 32%; display: inline-block;', 'readonly':'readonly'})),
		  	  
		  	  	
		     	css_class='col-md-4'),
            Div(
 				Field('initial_accessories_included', readonly=True),
 				Field('used_for_test', readonly=True),
 				
		  		Field('latest_calibration_date', readonly=True),
		   		Field('cal_due_date', readonly=True),
		   		Field('department', readonly=True),
		   		
		   	
		   	 css_class='col-md-4'),  
        css_class='row-fluid'), 
    )
	class Meta:
		model = Equipment
		fields = ['asset_number', 'serial_number', 'manufacturer', 'model', 'description',
		 'cal_interval', 'initial_condition',
		'initial_accessories_included', 'placed_in_service_date',
		   'used_for_test','location', 'department',
		   		'latest_calibration_date','cal_due_date',]


class CalibrationFormReadOnly(ModelForm):
    helper = FormHelper()
    helper.form_tag = False
    helper.layout = Layout(
        Div(
            Div(
		  		Field('cal_by', readonly=True),
		  		Field('cal_17025_check', readonly=True),
		  		Field('cal_date', readonly=True),
		  		Field('qc_test_by', readonly=True),
		  		Field('qc_test_date', readonly=True),
		  		Field('location', readonly=True),
		  		Field('notes', readonly=True), 
        	), 
        )
    )

    class Meta:
        model =Calibration
        fields = ['cal_by', 'cal_17025_check', 'cal_date', 'qc_test_by', 'qc_test_date', 'location', 'notes',]

class CalibrationForm(ModelForm):
    helper = FormHelper()
    helper.form_tag = False
    helper.layout = Layout(
        Div(
            Div(
		  		Field('cal_by'),
		  		Field('cal_17025_check'),
		  		Field('cal_date'),
		  		Field('mesure_uncertainty_included'),
		  		Field('a2la_Cal'),
		  		
		  		Field('qc_test_by'),
		  		Field('qc_test_date'),
		  		Field('location'),
		  		Field('notes'), 
		  		Field('cal_cert_location'), 
		  		
        	), 
        )
    )

    class Meta:
        model =Calibration
        fields = ['cal_by', 'cal_17025_check', 'cal_date', 'qc_test_by', 'qc_test_date', 'location', 'notes', 'cal_cert_location', 'a2la_Cal', 'mesure_uncertainty_included']

class FlagForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
            Div('flag_type',
                'flag_content', 
          
        css_class='col-sm-5'),  
        css_class='row-fluid'), 
)
        super(FlagForm, self).__init__(*args, **kwargs)
    class Meta:
        model =Flag
        fields = ['flag_type','flag_content']


auditlog.register(Equipment)
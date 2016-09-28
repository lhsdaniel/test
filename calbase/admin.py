from django.contrib import admin
from .models import Equipment, Calibration, Flag, Tests, Department, Manufacturer, Description, EquipmentForm, Attachment
from django.contrib.admin import AdminSite
from django.shortcuts import render, get_object_or_404, render_to_response
from django.contrib import admin
from django.conf.urls import url,include
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
import django_excel as excel
from carton.cart import Cart

class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url
            file_name = str(value)
            output.append(u' <a href="%s" target="_blank"><img src="%s" alt="%s" /></a> %s ' % \
                          (image_url, image_url, file_name, _('Change:')))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))


class ImageWidgetAdmin(admin.ModelAdmin):
    image_fields = []

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in self.image_fields:
            request = kwargs.pop("request", None)
            kwargs['widget'] = AdminImageWidget
            return db_field.formfield(**kwargs)
        return super(ImageWidgetAdmin, self).formfield_for_dbfield(db_field, **kwargs)


class MyAdminSite(AdminSite):
	admin.site.site_header = "Equipment Calibration Database"
	admin.site.site_title = "Equipment Calibration Database"
	admin.site.index_title = "Equipment Calibration Database"


# Register your models here.
admin_site = MyAdminSite(name = 'myadmin')

def default (request):
	equipment_list = Equipment.objects.all()
	context = {'equipment_list' : equipment_list}
	return render(request, 'calbase/default.html', context)
admin.site.register_view('default', view = default)

class CalibrationInlineAdmin(admin.TabularInline):
		model = Calibration

class FlagInlineAdmin(admin.TabularInline):
		model = Flag

def export_to_excel(modeladmin, request, query):
	column_names = ['manufacturer', 'model', 'description', 'cal_interval', 'serial_number']
	return excel.make_response_from_query_sets(query, column_names, 'xls', file_name="sheet")

def add_to_cart(modeladmin, request, query):
    cart = Cart(request.session)
    for equipment in query:
    	cart.add(equipment)    

def remove_from_cart(modeladmin, request, query):
    cart = Cart(request.session)
    for equipment in query:
    	cart.remove(equipment)  

class EquipmentAdmin(admin.ModelAdmin):
        inlines = [CalibrationInlineAdmin, FlagInlineAdmin]
        list_display = ['model', 'cal_interval', 'serial_number','timestamp']
        ordering = ['timestamp']
        actions = [export_to_excel, add_to_cart, remove_from_cart]
 
fields = ( 'image_tag', )
readonly_fields = ('image_tag',)



admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(Calibration)
admin.site.register(Flag)
admin.site.register(Tests)
admin.site.register(Department)
admin.site.register(Manufacturer)
admin.site.register(Description)
admin.site.register(Attachment)

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, render_to_response
from .models import EquipmentForm,CalibrationForm, FlagForm
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views import generic
from django.urls import reverse
from .models import Equipment,Calibration,Flag, Tests, Description, Department, Manufacturer, Capabilities
from django.http import HttpResponse, HttpResponseRedirect
from django.forms.models import inlineformset_factory
from .models import EquipmentFormReadOnly, CalibrationFormReadOnly
from haystack.query import SearchQuerySet
from django.http import HttpResponse
from carton.cart import Cart
import django_excel as excel
from django.db.models import Q
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, permission_required
from field_history.models import FieldHistory
import pyexcel
from dal import autocomplete
from django.template.loader import render_to_string


def default(request):
    # today = timezone.now().date()
    cart = Cart(request.session)
    form = EquipmentForm(request.POST or None, request.FILES or None)
    cal_form = CalibrationForm(request.POST or None, request.FILES or None)
    flag_form = FlagForm(request.POST or None, request.FILES or None)
    queryset_list = Equipment.objects.all().order_by("-timestamp")
    if request.user.is_staff or request.user.is_superuser:
        queryset_list = Equipment.objects.all().order_by("-timestamp")

    if request.method == "GET":
        if 'search_form' in request.GET:
            query = request.GET.get("q")
            if query:
                if query == "flag" or query == "flagged":
                    queryset_list =   queryset_list.filter(flag__isnull = False)

                elif query == "expire" or query == "due":
                    ueryset_list =   queryset_list.filter(cal_due_date__gte = timezone.now())
                else:
                    queryset_list = queryset_list.filter(
                        Q(asset_number__icontains=query)|
                        Q(serial_number__icontains=query)|
                        Q(manufacturer__icontains=query) |
                        Q(model__icontains=query) |
                        Q(department__icontains=query) |
                        Q(description__icontains=query) |
                        Q(used_for_test__description = query) |
                        Q(flag__flag_type = query)
                        ).distinct()
        elif 'formlist' in request.GET:
            cart_list = request.GET.getlist('formlist')
            carted_equipments = Equipment.objects.filter(id__in = cart_list)
            for equip in carted_equipments:
                cart = Cart(request.session)
                cart.remove(equip)
        else:
            cart_list = request.GET.getlist('check_list')
            carted_equipments = Equipment.objects.filter(id__in = cart_list)
            for equip in carted_equipments:
                cart = Cart(request.session)
                cart.add(equip)
    
    if request.method == "POST":
        if 'equipform' in request.POST:
            if form.is_valid():
                post = form.save()
                messages.success(request, "Created")
                return HttpResponseRedirect("/calbase/")

        elif 'calform' in request.POST:
             if cal_form.is_valid():
                cal_by = cal_form.cleaned_data['cal_by']
                cal_17025_check = cal_form.cleaned_data['cal_17025_check']
                cal_date = cal_form.cleaned_data['cal_date']
                mesure_uncertainty_included = cal_form.cleaned_data['mesure_uncertainty_included']
                a2la_Cal = cal_form.cleaned_data['a2la_Cal']
                qc_test_by = cal_form.cleaned_data['qc_test_by']
                qc_test_date = cal_form.cleaned_data['qc_test_date']
                location = cal_form.cleaned_data['location']
                notes = cal_form.cleaned_data['notes']
                cal_cert_location = cal_form.cleaned_data['cal_cert_location']

                cart_representation = cart.session[cart.session_key]
                ids_in_cart = cart_representation.keys()
                equipments_queryset = cart.get_queryset().filter(pk__in=ids_in_cart)

                for equip in equipments_queryset:
                    cal = Calibration.objects.create(cal_asset = equip, cal_by = cal_by, cal_17025_check = cal_17025_check,
                     cal_date = cal_date, mesure_uncertainty_included = mesure_uncertainty_included, 
                     a2la_Cal = a2la_Cal, qc_test_by = qc_test_by, qc_test_date = qc_test_date, 
                     location = location, notes = notes, cal_cert_location = cal_cert_location)
                    cal.save()
                messages.success(request, "Sucessfully Add Calibrations to Group " )
                return HttpResponseRedirect(reverse('calbase:default_overview'))

        elif 'flagform' in request.POST:
            if flag_form.is_valid():
                flag_type = flag_form.cleaned_data['flag_type']
                flag_content = flag_form.cleaned_data['flag_content']
                cart_representation = cart.session[cart.session_key]
                ids_in_cart = cart_representation.keys()
                equipments_queryset = cart.get_queryset().filter(pk__in=ids_in_cart)
                for equip in equipments_queryset:
                    flag = Flag.objects.create(flag_asset = equip, flag_type = flag_type, flag_content = flag_content)
                    flag.save()
                messages.success(request, "Sucessfully Flagged Group " )
                return HttpResponseRedirect(reverse('calbase:default_overview'))
                        


    paginator = Paginator(queryset_list, 8) # Show 25 contacts per page
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)




    context = {
        "equipment_list": queryset, 
        "title": "List",
        "page_request_var": page_request_var,
        "form" : form,
        "flag_form" : flag_form,
        "cal_form"  : cal_form,
        # "today": today,
    }
    return render(request, "new/list.html", context)

# def default (request):
#   equipment_list = Equipment.objects.all()
#   context = {'equipment_list' : equipment_list}
#   return render(request, 'calbase/default_overview.html', context)

@login_required
@permission_required('calbase.add_equipment')
def default_new (request):
    if request.method == "POST":
        form = EquipmentForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save()
            messages.success(request, "Created")
            return HttpResponseRedirect("/calbase/")
    else:
        form = EquipmentForm()
    return render(request, 'calbase/default_add.html', {'form':form})

@login_required
def default_detail (request, equipment_id):
    equipment = Equipment.objects.get(id = equipment_id)
    form = EquipmentFormReadOnly(instance=equipment)
    equipments =  Equipment.objects.all()
    cal_form = CalibrationForm()
    flag_form = FlagForm()
    context = {'equipment' : equipment, "form":form, 'equipments': equipments, 'cal_form': cal_form,
              'flag_form': flag_form,}
    return render(request, 'new/detail.html', context)

@login_required
@permission_required('calbase.change_equipment')
def post_update(request, equipment_id):
    equipment = get_object_or_404(Equipment, id = equipment_id)
    form = EquipmentForm(request.POST or None, request.FILES or None, instance=equipment)
    if form.is_valid():
        post = form.save()
        messages.success(request, "Sucessfully Saved " )
        #messages.success(request, "<a href='#'>Item</a> Saved", extra_tags='html_safe')
        return HttpResponseRedirect(post.get_absolute_url())

    context = {
        "equipment": equipment,
        "form":form,
    }
    return render(request, 'calbase/default_edit.html', context)

@login_required
@permission_required('calbase.change_equipment')
def default_update_cal (request, equipment_id, calibration_id):
    equipment = get_object_or_404(Equipment, id = equipment_id)
    calibration = get_object_or_404(Calibration, id = calibration_id)
    form = EquipmentFormReadOnly(request.POST or None, request.FILES or None, instance=equipment)
    cal_form = CalibrationForm(request.POST or None, request.FILES or None, instance=calibration)
    
    if request.method == "POST":

        if cal_form.is_valid():
            if 'calibration' in request.POST:
                cal_form.save()
                messages.success(request, "Sucessfully Updated Calibrations " )
                return HttpResponseRedirect(reverse('calbase:default_detail', args=(equipment_id,)))
    context = {
        "cal_form" : cal_form,
        "equipment" : equipment,
        "form" : form,
    }
    return render(request, 'calbase/default_detail_cal.html', context)

@login_required
@permission_required('calbase.change_equipment')
def default_add_cal (request, equipment_id):
    equipment = get_object_or_404(Equipment, id = equipment_id)
    form = EquipmentFormReadOnly(request.POST or None, request.FILES or None, instance=equipment)
    cal_form = CalibrationForm(request.POST or None, request.FILES or None)
    
    if request.method == "POST":

        if cal_form.is_valid():
            if 'calibration' in request.POST:
                cal_by = cal_form.cleaned_data['cal_by']
                cal_17025_check = cal_form.cleaned_data['cal_17025_check']
                cal_date = cal_form.cleaned_data['cal_date']
                mesure_uncertainty_included = cal_form.cleaned_data['mesure_uncertainty_included']
                a2la_Cal = cal_form.cleaned_data['a2la_Cal']
                qc_test_by = cal_form.cleaned_data['qc_test_by']
                qc_test_date = cal_form.cleaned_data['qc_test_date']
                location = cal_form.cleaned_data['location']
                notes = cal_form.cleaned_data['notes']
                cal_cert_location = cal_form.cleaned_data['cal_cert_location']
                cal = Calibration.objects.create(cal_asset = equipment, cal_by = cal_by, cal_17025_check = cal_17025_check,
                     cal_date = cal_date, mesure_uncertainty_included = mesure_uncertainty_included, 
                     a2la_Cal = a2la_Cal, qc_test_by = qc_test_by, qc_test_date = qc_test_date, 
                     location = location, notes = notes, cal_cert_location = cal_cert_location)
                cal.save()
                messages.success(request, "Sucessfully Created New Calibration" )
                return HttpResponseRedirect(reverse('calbase:default_detail', args=(equipment_id,)))
    context = {
        "cal_form" : cal_form,
        "equipment" : equipment,
        "form" : form,
    }
    return render(request, 'calbase/default_detail_cal_new.html', context)

@login_required
@permission_required('calbase.change_equipment')
def default_add_flag (request, equipment_id):
    equipment = get_object_or_404(Equipment, id = equipment_id)
    form = EquipmentFormReadOnly(request.POST or None, request.FILES or None, instance=equipment)
    EquipmentInlineFormSet = inlineformset_factory(Equipment, Flag, form = FlagForm, extra = 1, can_delete=True )
    
    if request.method == "POST":
        formset = EquipmentInlineFormSet(request.POST, request.FILES, instance=equipment)
        if formset.is_valid():
            if 'flag' in request.POST:
                formset.save()
                messages.success(request, "Sucessfully Updated Flags " )
                return HttpResponseRedirect(reverse('calbase:default_detail', args=(equipment_id,)))
    else:
        formset = EquipmentInlineFormSet(instance=equipment)
    context = {
        "formset" : formset,
        "equipment" : equipment,
        "form" : form,
    }
    return render(request, 'calbase/default_detail_flag.html', context)


def add(request, equipment_id):
    cart = Cart(request.session)
    equipment = get_object_or_404(Equipment, id = equipment_id)
    cart.add(equipment)
    return HttpResponseRedirect(reverse('calbase:default_detail', args=(equipment_id,)))

def show(request):
    return render(request, 'calbase/show_cart.html')

def remove(request):
    cart = Cart(request.session)
    equipment = Equipment.objects.get(id=request.GET.get('equipment_id'))
    cart.remove(equipment)
    return HttpResponse("Removed")

def export_data(request, atype):
    if atype == "sheet":
        return excel.make_response_from_a_table(Question, 'xls', file_name="sheet")
    elif atype == "book":
        return excel.make_response_from_tables([Question, Choice], 'xls', file_name="book")

def download(request, file_type):
    sheet = excel.pe.Sheet(data)
    return excel.make_response(sheet, file_type)


def download_as_attachment(request, file_type, file_name):
    return excel.make_response_from_array(
        data, file_type, file_name=file_name)


def export_data(request, atype):
    cart = Cart(request.session)
    if atype == "sheet":
        #query_sets = Equipment.objects.all()
        query_record = Equipment.objects.all().values('manuf', 'model', 'desc', 
            'cal_interval', 'serial_number', 'latest_calibration_date', 'cal_due_date')
        #sheet = get_sheet(query_sets=query_record, column_names=["manufacturer"])

        #column_names = ['manufacturer', 'model', 'description', 'latest_calibration_date', 'cal_interval', 'cal_due_date', 'serial_number']
        return excel.make_response_from_records(
            query_record, 'xls', file_name="sheet")
    elif atype == "book":
        return excel.make_response_from_tables(
            [Equipment, Calibration], 'xls', file_name="book")
    elif atype == "custom":
        column_names = ['asset_number','manuf', 'model', 'desc', 
            'cal_interval', 'serial_number', 'latest_calibration_date', 'cal_due_date']
        cart_representation = cart.session[cart.session_key]
        ids_in_cart = cart_representation.keys()
        equipments_queryset = cart.get_queryset().filter(pk__in=ids_in_cart)
        return excel.make_response_from_query_sets(
            equipments_queryset,
            column_names,
            'xls',
            file_name="custom"
        )
    else:
        return HttpResponseBadRequest(
            "Bad request. please put one of these " +
            "in your url suffix: sheet, book or custom")

@login_required
@permission_required('calbase.change_equipment')
def cart_add_cal(request):
    cal_form = CalibrationForm(request.POST or None, request.FILES or None)
    cart = Cart(request.session)
    if request.method == "POST":

        if cal_form.is_valid():
            if 'cal' in request.POST:
                cal_by = cal_form.cleaned_data['cal_by']
                cal_17025_check = cal_form.cleaned_data['cal_17025_check']
                cal_date = cal_form.cleaned_data['cal_date']
                mesure_uncertainty_included = cal_form.cleaned_data['mesure_uncertainty_included']
                a2la_Cal = cal_form.cleaned_data['a2la_Cal']
                qc_test_by = cal_form.cleaned_data['qc_test_by']
                qc_test_date = cal_form.cleaned_data['qc_test_date']
                location = cal_form.cleaned_data['location']
                notes = cal_form.cleaned_data['notes']
                cal_cert_location = cal_form.cleaned_data['cal_cert_location']

                cart_representation = cart.session[cart.session_key]
                ids_in_cart = cart_representation.keys()
                equipments_queryset = cart.get_queryset().filter(pk__in=ids_in_cart)

                for equip in equipments_queryset:
                    cal = Calibration.objects.create(cal_asset = equip, cal_by = cal_by, cal_17025_check = cal_17025_check,
                     cal_date = cal_date, mesure_uncertainty_included = mesure_uncertainty_included, 
                     a2la_Cal = a2la_Cal, qc_test_by = qc_test_by, qc_test_date = qc_test_date, 
                     location = location, notes = notes, cal_cert_location = cal_cert_location)
                    cal.save()
                messages.success(request, "Sucessfully Add Calibrations to Group " )
                return HttpResponseRedirect(reverse('calbase:default_overview'))
    context = {
        "cal_form" : cal_form,
    }
    return render(request, 'calbase/cart_add_cal.html', context)

@login_required
@permission_required('calbase.change_equipment')
def cart_add_flag(request):
    flag_form = FlagForm(request.POST or None, request.FILES or None)
    cart = Cart(request.session)
    if request.method == "POST":

        if flag_form.is_valid():
            if 'flag' in request.POST:
                flag_type = flag_form.cleaned_data['flag_type']
                flag_content = flag_form.cleaned_data['flag_content']
                cart_representation = cart.session[cart.session_key]
                ids_in_cart = cart_representation.keys()
                equipments_queryset = cart.get_queryset().filter(pk__in=ids_in_cart)
                for equip in equipments_queryset:
                    flag = Flag.objects.create(flag_asset = equip, flag_type = flag_type, flag_content = flag_content)
                    flag.save()
                messages.success(request, "Sucessfully Flagged Group " )
                return HttpResponseRedirect(reverse('calbase:default_overview'))
    context = {
        "flag_form" : flag_form,
    }
    return render(request, 'calbase/cart_add_flag.html', context)

class TestsAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Tests.objects.none()

        qs = Tests.objects.all()

        if self.q:
            qs = qs.filter(description__istartswith=self.q)

        return qs

class DepartmentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Department.objects.none()

        qs = Department.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs

class DescriptionAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Description.objects.none()

        qs = Description.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs

class ManufacturerAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Manufacturer.objects.none()

        qs = Manufacturer.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs

class CapabilitiesAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Capabilities.objects.none()

        qs = Capabilities.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs
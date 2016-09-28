
from django.conf.urls import url,include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .views import TestsAutocomplete, DepartmentAutocomplete, DescriptionAutocomplete, ManufacturerAutocomplete


urlpatterns = [
    url(r'^$', views.default, name = 'default_overview'),
    url(r'^equipment/(?P<equipment_id>[0-9]+)/update/$', views.post_update, name = 'default_update'),
    url(r'^equipment/(?P<equipment_id>[0-9]+)/$', views.default_detail, name = 'default_detail'),
    url(r'^equipment/new/$', views.default_new, name = 'default_new'),
    url(r'^equipment/(?P<equipment_id>[0-9]+)/cal/(?P<calibration_id>[0-9]+)/$', views.default_update_cal, name = 'default_update_cal'),
    url(r'^equipment/(?P<equipment_id>[0-9]+)/cal/new/$', views.default_add_cal, name = 'default_add_cal'),
    url(r'^equipment/(?P<equipment_id>[0-9]+)/flag/$', views.default_add_flag, name = 'default_add_flag'),
    url(r'^search/', include('haystack.urls')),
    url(r'^export/(.*)', views.export_data, name="export"),
    url(r'^add/(?P<equipment_id>[0-9]+)/$', views.add, name='shopping-cart-add'),
    url(r'^remove/', views.remove, name='shopping-cart-remove'),
    url(r'^show/', views.show, name='shopping-cart-show'),
    url(r'^download/(.*)', views.download, name="download"),
    url(r'^download_attachment/(.*)/(.*)', views.download_as_attachment,name="download_attachment"),
    url(r'^export/(.*)', views.export_data, name="export"),
    url(r'^equipment/(?P<equipment_id>[0-9]+)/edit/$', views.post_update, name = "post_update"),

    url(r'^login/$', auth_views.login, name = "login"),
    url(r'^logout/$', auth_views.logout, name = "logout"),
    url(r'^password_change/$', auth_views.password_change, {'post_change_redirect': 'calbase:password_change_done'}, name = "password_change"),
    url(r'^password_change/done/$', auth_views.password_change_done, name = "password_change_done"),
    url(r'^password_reset$', auth_views.password_reset, {'post_reset_redirect' : 'calbase:password_reset_done'}, name = "password_reset"),
    url(r'^password_reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, {'post_reset_redirect' : 'calbase:password_reset_done'}, name = "password_reset_confirm"),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name = "password_reset_done"),
    url(r'^password_reset/compelete/$', auth_views.password_reset_complete, name = "password_reset_compelete"),
    url(r'^cart/add_flag', views.cart_add_flag, name='cart_add_flag'),
    url(r'^cart/add_cal', views.cart_add_cal, name='cart_add_cal'),
    url(r'^tests-autocomplete/$', TestsAutocomplete.as_view(create_field='description'), name='tests',),
    url(r'^department-autocomplete/$', DepartmentAutocomplete.as_view(create_field='name'), name='department',),
    url(r'^description-autocomplete/$', DescriptionAutocomplete.as_view(create_field='name'), name='description',),
    url(r'^manufacturer-autocomplete/$', ManufacturerAutocomplete.as_view(create_field='name'), name='manufacturer',),

]

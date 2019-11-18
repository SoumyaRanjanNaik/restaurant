from django.contrib import admin
from django.urls import path, include
from sale import views
admin.site.site_header = 'Chotte Nawab'
admin.site.site_title = 'Chotte Nawab'
admin.site.index_title = 'Chotte Nawab'

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('sale/', include('sale.urls'), name="sale"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('stock/', include('stock.urls'), name='stock'),
    path('ledger/', include('ledger.urls'), name='ledger'),
]

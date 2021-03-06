from django.conf.urls import url, include
from . import views

# urls for profile pages
profile_urls = [
    url(r'^domain/$', views.domain_view, name='domain'),
    url(r'^personal/$', views.personal_view, name='personal'),
    url(r'^favorites/$', views.favorites_view, name='favorites'),
    # url(r'^tree/$', views.tree, name='dept_tree'),
    url(r'^search_domain_tree/$', views.search_domain_tree_view, name='search_domain_tree'),
]

urlpatterns = [
    url(r'', include('registration.backends.default.urls')),
    # url(r'', include('django.contrib.auth.urls')),

    url(r'', include(profile_urls, namespace='authentication')),
]

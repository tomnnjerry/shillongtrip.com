from django.urls import path

from . import views as v

urlpatterns = [
    path('', v.home, name='home'),
    path('packages/', v.packages_index, name='packages'),
    path('packages/<slug:slug>/', v.package_detail, name='package'),
    path('styles/<slug:key>/', v.style_detail, name='style'),
    path('places/', v.places_index, name='places'),
    path('places/<slug:slug>/', v.place_detail, name='place'),
    path('states/<slug:key>/', v.state_detail, name='state'),
    path('guides/', v.guides_index, name='guides'),
    path('guides/<slug:slug>/', v.guide_detail, name='guide'),
    path('trip-tools/', v.tools, name='tools'),
    path('contact/', v.contact, name='contact'),
    path('about/', v.about, name='about'),
    path('faq/', v.faq, name='faq'),
    path('photo-credits/', v.credits, name='credits'),
    path('privacy/', v.legal_view, {'key': 'privacy'}, name='privacy'),
    path('terms/', v.legal_view, {'key': 'terms'}, name='terms'),
    path('cookie-policy/', v.legal_view, {'key': 'cookies'}, name='cookies'),
    path('cancellation-refund-policy/', v.legal_view, {'key': 'refund'}, name='refund'),
    path('disclaimer/', v.legal_view, {'key': 'disclaimer'}, name='disclaimer'),
    path('sitemap/', v.sitemap_page, name='sitemap_page'),
    path('sitemap.xml', v.sitemap_xml, name='sitemap_xml'),
    path('robots.txt', v.robots_txt),
    path('ads.txt', v.ads_txt),
    path('llms.txt', v.llms_txt),
    path('search.json', v.search_json),
    path('site.webmanifest', v.webmanifest),
    path('api/enquiry/', v.enquiry, name='enquiry'),
]

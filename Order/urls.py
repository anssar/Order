"""
Definition of urls for Order.
"""

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import RedirectView

from Order.order import views


admin.autodiscover()

urlpatterns = [
    url(r'^$', views.mainPage),
    url(r'^nizhnevartovsk$', views.nizhnevartovsk),
    url(r'^ekaterinburg$', views.ekaterinburg),
    url(r'^langepas$', views.langepas),
    url(r'^magnitogorsk$', views.magnitogorsk),
    url(r'^chelyabinsk$', views.chelyabinsk),
    url(r'^sochi$', views.sochi),
    url(r'^bilimbay$', views.bilimbay),
    url(r'^khanty-mansiysk$', views.khanty_mansiysk),
    url(r'^pervouralsk$', views.pervouralsk),
    url(r'^uralmash$', views.uralmash),
    url(r'^paycard$', views.paycard),
    url(r'^telegram$', views.telegram),
    url(r'^img/logo\.png$', RedirectView.as_view(url='/static/img/logo.png')),
    url(r'^check-correct$', views.checkCorrect),
    url(r'^confirm-form$', views.confirmForm),
    url(r'^current-form$', views.currentForm),
    url(r'^new-order-form$', views.newOrderForm),
    url(r'^new-order-form/$', views.newOrderForm),
    url(r'^find-car-form$', views.findCarForm),
    url(r'^parse-address$', views.parseAddress),
    url(r'^check-code$', views.checkCode),
    url(r'^resend-sms$', views.resendSMS),
    url(r'^route-analysis$', views.routeAnalysis),
    url(r'^get-coords-from-cookie$', views.getCoordsFromCookie),
    url(r'^get-step$', views.getStep),
    url(r'^set-city$', views.setCity),
    url(r'^get-city$', views.getCity),
    url(r'^abort-order$', views.abortOrder),
    url(r'^check-order-state-change$', views.checkOrderStateChange),
    url(r'^get-car-coords$', views.getCarCoords),
    url(r'^fail-notify$', views.failNotify),
    url(r'^success-notify$', views.successNotify),
    url(r'^drivers$', views.drivers),
    url(r'^driver$', views.driver),
    url(r'^operator$', views.operator),
    url(r'^new-driver$', views.new_driver),
    url(r'^feedback$', views.feedback),
    url(r'^send-feedback$', views.send_feedback),
    url(r'^to-full-version$', views.toFullVersion),
    url(r'^to-mobile-version$', views.toMobileVersion),
    url(r'^driver\.apk$', RedirectView.as_view(url='/static/driver.apk')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin', include(admin.site.urls)),
]

handler404 = views.nopage

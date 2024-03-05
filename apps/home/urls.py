# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # Main routes
    path('', views.index, name='home'),
    path('partners', views.partners_page, name='partners_page'),
    path('add_new_partner', views.add_new_partner, name="add_new_partner"),
    path('partners/<partner_name>/details', views.partner_details, name='partner_details'),

    # Front & Back routes
    path('partners/<partner_name>/<model_name>/<year>/<month_id>', views.front_back_requests, name = "front_back_requests"),
    path('partners/<partner_name>/<model_name>/download', views.download_all_front_back_requests, name="download_all_front_back_requests"),
    path('partners/<partner_name>/<model_name>/<year>/<month>/download', views.download_front_back_requests_by_month, name="download_front_back_requests_by_month"),

    # Verification routes
    path('partnerss/<partner_name>/verification/<year>/<month_id>', views.verification_requests, name = "verification_requests"),
    path('partnerss/<partner_name>/verification/download', views.download_all_verification_requests, name="download_all_verification_requests"),
    path('partnerss/<partner_name>/verification/<year>/<month>/download', views.download_verification_requests_by_month, name="download_verification_requests_by_month"),


    # Matches any html file
    # re_path(r'^.*\.*', views.pages, name='pages'),

]

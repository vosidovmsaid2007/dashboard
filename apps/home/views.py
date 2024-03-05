
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
import requests
import datetime
from datetime import datetime, date
import pandas as pd
import os
from django.shortcuts import render, redirect


# Functions
def filter_requests_by_date(data, year, month):
  filtered_data = []
  for row in data:
    # if row[2] != model:
    #   continue

    try:
      date_str = row[-1]
      date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
      continue

    if date.year != year or date.month != month:
      continue

    filtered_data.append(row)
  return filtered_data


def list2xlsx(list_data, columns, output):
    columns = columns

    #['id', 'counter', 'model', 'img_size', 'weight_img', 'format_img', 'special_id', 'find_pass', 'pass_num', 'time', 'date']

    df = pd.DataFrame(list_data, columns=columns)

    df.to_excel(output, index=False)


# Main page
@login_required(login_url="/login/")
def index(request):

    partners_info = requests.get("https://fastapitest008.azurewebsites.net/partners_info").json()
    
    partners_amount = partners_info["partners_amount"]


    context = {'segment': 'index', 'partners_amount': partners_amount}

    

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


# Partners page
@login_required(login_url="/login/")
def partners_page(request):
    partners_info = requests.get("https://fastapitest008.azurewebsites.net/partners_info").json()
    partners_info = partners_info["partner_data"]

    today = date.today()
    current_year = today.year
    current_month = today.month

    data = {
        'partners_info': partners_info,
        'current_year': current_year,
        'current_month': current_month
    }

    html_template = loader.get_template('home/partners_page.html')
    return HttpResponse(html_template.render(data, request))


# Add Partner Button
@login_required(login_url="/login/")
def add_new_partner(request):
    if request.method == 'POST':
        partner_name = request.POST.get('partner_name')
        status = request.POST.get('partner_status')

        try:
            response = requests.post(
                "https://fastapitest008.azurewebsites.net/register_partner",
                json={"name": partner_name, "status": status}
            )

            result = response.json()

            return render(request, 'home/add_partner.html', context={
                          'message':result['message'],'message_success': f"Partner {partner_name} successfully registered",
                                                                     "message_error": f"Partner {partner_name} is already registered"})

        except requests.exceptions.RequestException as e:
            return render(request, 'home/add_partner.html', context={'message': str(e)})
    else:
        data = {
            "error": "Use POST method!"
        }
        return render(request, 'home/add_partner.html')


# Partner details
@login_required(login_url="/login/")
def partner_details(request, partner_name):
    return render(request, 'home/partner_details.html')


# Front & Back
@login_required(login_url="/login/")
def front_back_requests(request, partner_name, model_name, year, month_id):


    month_names = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]

    partners_info = requests.get(f"https://fastapitest008.azurewebsites.net/{year}/{month_id}/{partner_name}/{model_name}/100").json()

    
    page_month = month_names[int(month_id)-1]

    today = date.today()
    current_year = today.year

    data = {
        "partner_name": partner_name,
        "front_back_info_filtered": partners_info,
        "months_names": month_names,
        "page_month": page_month,
        "page_month_id": month_id,
        "current_year": current_year,
        "model_name": model_name,
        "page_year": year,
    }
    html_template = loader.get_template('home/front_back_requests.html')
    return HttpResponse(html_template.render(data, request))




@login_required(login_url="/login/")
def download_all_front_back_requests(request, partner_name, model_name):
    columns = ['id', 'counter', 'model', 'img_size', 'weight_img', 'format_img', 'special_id', 'find_pass', 'pass_num', 'time', 'date']

    
    get_front_back_requests_all = requests.get(f"https://fastapitest008.azurewebsites.net/all_requests/{partner_name}/{model_name}").json()
    list2xlsx(get_front_back_requests_all, columns, f'{os.getcwd()}\download_requests\All {model_name} requests-{partner_name}.xlsx')


    month_names = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]

    path_all_requests = f'{os.getcwd()}\download_requests\All {model_name} requests-{partner_name}.xlsx'
    # path_requests_by_month = f'{os.getcwd()}\django\download_requests\{partner_name}-{model_name}-{year}-{month_names[int(month_id)-1]}.xlsx'

    with open(path_all_requests, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=All {model_name} requests-{partner_name}.xlsx'

    return response


@login_required(login_url="/login/")
def download_front_back_requests_by_month(request, partner_name, model_name, year, month):
    columns = ['id', 'counter', 'model', 'img_size', 'weight_img', 'format_img', 'special_id', 'find_pass', 'pass_num', 'time', 'date']

    
    month_names = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    month_id = month_names.index(month)+1

    get_front_back_requests_by_month = requests.get(f"https://fastapitest008.azurewebsites.net/{year}/{month_id}/{partner_name}/{model_name}/all").json()
    list2xlsx(get_front_back_requests_by_month, columns, f'{os.getcwd()}\download_requests\{model_name}-{partner_name}-{year}-{month_names[int(month_id)-1]}.xlsx')

    

    path_requests_by_month = f'{os.getcwd()}\download_requests\{model_name}-{partner_name}-{year}-{month_names[int(month_id)-1]}.xlsx'

    with open(path_requests_by_month, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={model_name}-{partner_name}-{year}-{month_names[int(month_id)-1]}.xlsx'

    return response




# Verification
@login_required(login_url="/login/")
def verification_requests(request, partner_name, year, month_id):

    month_names = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]

    partners_info = requests.get(f"https://fastapitest008.azurewebsites.net/{year}/{month_id}/{partner_name}/verification/100").json()

    page_month = month_names[int(month_id)-1]

    today = date.today()
    current_year = today.year

    data = {
        "partner_name": partner_name,
        "verification_info_filtered": partners_info,
        "months_names": month_names,
        "page_month": page_month,
        "page_month_id": month_id,
        "current_year": current_year,
        "page_year": year,
    }
    html_template = loader.get_template('home/verification_requests.html')

    return HttpResponse(html_template.render(data, request))


@login_required(login_url="/login/")
def download_all_verification_requests(request, partner_name):
    columns = ['id', 'counter', 'front_img_size', 'selfi_img_size', 'format_front', 'format_selfi', 'weight_front_img', 'weight_selfi_img', 'front_findPass', 'selfi_findPass', 'front_passNum', 'selfi_passNum', 'front_original', 'selfi_original', 'front_len_passnum', 'selfi_len_passnum', 'front_special_id', 'selfi_special_id', 'pass_match', 'face_match', 'distance', 'explanation_of_reject', 'is_fake', 'time', 'date']
    
    get_front_back_requests_all = requests.get(f"https://fastapitest008.azurewebsites.net/all_requests/{partner_name}/verification").json()
    list2xlsx(get_front_back_requests_all, columns, f'{os.getcwd()}\download_requests\All verification requests-{partner_name}.xlsx')

    month_names = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]

    path_all_requests = f'{os.getcwd()}\download_requests\All verification requests-{partner_name}.xlsx'
    # path_requests_by_month = f'{os.getcwd()}\django\download_requests\{partner_name}-{model_name}-{year}-{month_names[int(month_id)-1]}.xlsx'

    with open(path_all_requests, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=All verification requests-{partner_name}.xlsx'

    return response


@login_required(login_url="/login/")
def download_verification_requests_by_month(request, partner_name, year, month):
    columns = ['id', 'counter', 'front_img_size', 'selfi_img_size', 'format_front', 'format_selfi', 'weight_front_img', 'weight_selfi_img', 'front_findPass', 'selfi_findPass', 'front_passNum', 'selfi_passNum', 'front_original', 'selfi_original', 'front_len_passnum', 'selfi_len_passnum', 'front_special_id', 'selfi_special_id', 'pass_match', 'face_match', 'distance', 'explanation_of_reject', 'is_fake', 'time', 'date']
    
    month_names = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    month_id = month_names.index(month)+1

    get_front_back_requests_by_month = requests.get(f"https://fastapitest008.azurewebsites.net/{year}/{month_id}/{partner_name}/verification/all").json()
    list2xlsx(get_front_back_requests_by_month, columns, f'{os.getcwd()}\download_requests\Verification-{partner_name}-{year}-{month_names[int(month_id)-1]}.xlsx')


    path_requests_by_month = f'{os.getcwd()}\download_requests\Verification-{partner_name}-{year}-{month_names[int(month_id)-1]}.xlsx'

    with open(path_requests_by_month, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=Verification-{partner_name}-{year}-{month_names[int(month_id)-1]}.xlsx'

    return response
#
# @login_required(login_url="/login/")
# def pages(request):
#     context = {}
#     # All resource paths end in .html.
#     # Pick out the html file name from the url. And load that template.
#     try:
#
#         load_template = request.path.split('/')[-1]
#
#         if load_template == 'admin':
#             return HttpResponseRedirect(reverse('admin:index'))
#         context['segment'] = load_template
#
#         html_template = loader.get_template('home/' + load_template)
#         return HttpResponse(html_template.render(context, request))
#
#     except template.TemplateDoesNotExist:
#
#         html_template = loader.get_template('home/page-404.html')
#         return HttpResponse(html_template.render(context, request))
#
#     except:
#         html_template = loader.get_template('home/page-500.html')
#         return HttpResponse(html_template.render(context, request))

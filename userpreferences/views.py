from django.shortcuts import render
from django.views import View
import os,json
from django.conf import settings
from .models import UserPreferences
from django.contrib import messages
# Create your views here.

# class PreferencesProcessingView(View):
#     def get(self,request):
#         return render(request, 'preferences/index.html')
def index(request):
    currency_data =[]
    file_path = os.path.join(settings.BASE_DIR,'currencies.json')
        # take time to look at the file we are loading using pdb
        # import pdb
        # pdb.set_trace()
    with open(file_path,'r') as json_file: #the context manager syntax does not require us to close the file
        data = json.load(json_file)

        for k, v in data.items():
            currency_data.append({'name':k, 'value': v})

    exists_check = UserPreferences.objects.filter(user=request.user).exists()
    if exists_check:
        user_preferences = UserPreferences.objects.get(user=request.user)
    else:
        user_preferences=None

    if request.method=="GET":
        
        # import pdb
        # pdb.set_trace()  #Check what we have added in our object/ dictionary for now
        return render(request, 'preferences/index.html',{'currencies':currency_data,'user_preferences':user_preferences})
    else:
        currency=request.POST['currency']
        if exists_check:
            user_preferences.currency=currency
            user_preferences.save()
        else:
            UserPreferences.objects.create(user=request.user, currency=currency)
        messages.success(request,'User Settings Saved Successfully')
        return render(request, 'preferences/index.html',{'currencies':currency_data,'user_preferences':user_preferences})




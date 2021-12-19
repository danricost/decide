from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED,
        HTTP_400_BAD_REQUEST,
        HTTP_401_UNAUTHORIZED
)
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render
from django.core.exceptions import ObjectDoesNotExist

from .serializers import UserSerializer

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
UserModel = get_user_model()
from django.core.mail import send_mail
from .forms import RegisterUserForm

from .models import Profile




def register(request):
    if request.user.is_authenticated:
        print('Already authenticated')
        return HttpResponseRedirect(reverse('rxWod:index'))
    else:
        if request.method == 'POST':
            form = RegisterUserForm(request.POST)
            # RegisterUserForm is created from User model, all model field restrictions are checked to considerate it a valid form
            if form.is_valid():
                print('Valid form')
                # Save user to database but with is_active = False
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                
                sex = request.POST.get('sex', 'DK/NA')
                location = request.POST.get('location', 'Sin especificar')
                birth_date = request.POST.get('birth_date', 'None')
                # print('sex: '+sex+'\nlocation: '+location+'\nbirth: '+birth_date)

                profile = Profile.objects.get(user=user)
                profile.sex = sex
                profile.location = location
                profile.birth_date = birth_date
                # print(profile.sex, profile.location, profile.birth_date, profile.user)

                profile.save()

                # Send confirmation email
                current_site = get_current_site(request)
                subject = 'Activate Your ' + current_site.domain + ' Account'
                message = render_to_string('usersAuth/email_confirmation.html',
                    {
                        "domain": current_site.domain,
                        "user": user,
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                        "token": default_token_generator.make_token(user),
                    },
                )
                to_email = form.cleaned_data.get('email')
                send_mail(subject, message, 'decide.veleta.g4@gmail.com', [to_email])

                # Redirect user to login
                messages.success(request, 'Please Confirm your email to complete registration before Login.')
                return HttpResponseRedirect(reverse('login'))
            else:
                #print('Invalid form: %s' % form.errors.as_data())
                #print(type(form.errors.as_data()))
                if form.errors:
                    #messages.info(request, 'Input field errors:')
                    for key, values in form.errors.as_data().items():
                        #print("Bad value: %s - %s" % (key, values))
                        if key == 'username':
                            messages.info(request, 'Error input fields')
                            break
                        else:
                            for error_value in values:
                                print(error_value)
                                #print(type(error_value))
                                messages.info(request, '%s' % (error_value.message))

                return HttpResponseRedirect(reverse('registerUser'))
        else:
            form = RegisterUserForm()

            context = {
                'form': form
            }
            return render(request, 'usersAuth/register.html', context)
            
            
            
            
def activate(request, uidb64, token):

    # uid = urlsafe_base64_decode(uidb64.encode('utf-8').strip()).encode('utf-8').strip().decode('cp1252')
    # user = UserModel._default_manager.get(pk=uid)

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel._default_manager.get(pk=uid)

    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        # Redirect user to login
        messages.success(request, 'Successful email confirmation, you can proceed to login.')
        return HttpResponseRedirect(reverse('login'))
    else:
        return HttpResponse('Activation link is invalid!')
            
            
            

def home(request):
	count = User.objects.count()	
	return render(request, 'home.html', {'count': count})


class GetUserView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        return Response(UserSerializer(tk.user, many=False).data)


class LogoutView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        try:
            tk = Token.objects.get(key=key)
            tk.delete()
        except ObjectDoesNotExist:
            pass

        return Response({})


class RegisterView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        if not tk.user.is_superuser:
            return Response({}, status=HTTP_401_UNAUTHORIZED)

        username = request.data.get('username', '')
        pwd = request.data.get('password', '')
        if not username or not pwd:
            return Response({}, status=HTTP_400_BAD_REQUEST)

        try:
            user = User(username=username)
            user.set_password(pwd)
            user.save()
            token, _ = Token.objects.get_or_create(user=user)
        except IntegrityError:
            return Response({}, status=HTTP_400_BAD_REQUEST)
        return Response({'user_pk': user.pk, 'token': token.key}, HTTP_201_CREATED)

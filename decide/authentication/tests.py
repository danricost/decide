from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from base import mods

import os

from .forms import RegisterUserForm

from django.test import Client
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text, force_str




class AuthTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        mods.mock_query(self.client)
        u = User(username='voter1')
        u.set_password('123')
        u.save()

        u2 = User(username='admin')
        u2.set_password('admin')
        u2.is_superuser = True
        u2.save()

    def tearDown(self):
        self.client = None

    def test_login(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)

        token = response.json()
        self.assertTrue(token.get('token'))

    def test_login_fail(self):
        data = {'username': 'voter1', 'password': '321'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_getuser(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 200)

        user = response.json()
        # self.assertEqual(user['id'], 1)
        self.assertEqual(user['username'], 'voter1')

    def test_getuser_invented_token(self):
        token = {'token': 'invented'}
        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 404)

    def test_getuser_invalid_token(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 1)

        token = response.json()
        self.assertTrue(token.get('token'))

        response = self.client.post('/authentication/logout/', token, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 404)

    def test_logout(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 1)

        token = response.json()
        self.assertTrue(token.get('token'))

        response = self.client.post('/authentication/logout/', token, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 0)

    def test_register_bad_permissions(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1'})
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 401)

    def test_register_bad_request(self):
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1'})
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 400)

    def test_register_user_already_exist(self):
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update(data)
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 400)

    def test_register(self):
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1', 'password': 'pwd1'})
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            sorted(list(response.json().keys())),
            ['token', 'user_pk']
        )




class RegisterTestCase(TestCase):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()


    def test_nuevo_usuario_OK(self):
        os.environ['NORECAPTCHA_TESTING'] = 'True'  # desactivamos el captcha

        data = {'email': 'new1@mail.com',
                'first_name': 'new',
                'last_name': 'new',
                'birth_date':'2000-01-01',
                'password1': 'Practica1',
                'password2': 'Practica1',
                'location': 'Sevilla',
                'sex': 'DK/NA',
                'g-recaptcha-response': 'PASSED',
                'username': 'new1'}

        response = self.client.post("/authentication/registerUser/", data=data, format="json", follow=True)
        self.assertEqual(response.status_code, 200)

        form = RegisterUserForm(data)
        self.assertTrue(form)
        self.assertTrue(form.is_valid())
        user1=form.save()
        self.assertTrue(user1.id>0)     # el usuario existe y se ha guardado



    def test_nuevo_usuario_email_mal_FAIL(self):
        os.environ['NORECAPTCHA_TESTING'] = 'True'

        data = {'email': 'new1.mail.com',   # email no valido
                'first_name': 'new',
                'last_name': 'new',
                'birth_date':'2000-01-01',
                'password1': 'Practica1',
                'password2': 'Practica1',
                'location': 'Sevilla',
                'sex': 'DK/NA',
                'g-recaptcha-response': 'PASSED',
                'username': 'new1'}

        response = self.client.post("/authentication/registerUser/", data=data, format="json", follow=True)
        self.assertEqual(response.status_code, 200)

        form = RegisterUserForm(data)
        self.assertTrue(form)
        self.assertTrue(form.is_valid()==False)



    def test_nuevo_usuario_ya_existe_FAIL(self):
        os.environ['NORECAPTCHA_TESTING'] = 'True'

        data = {'email': 'new1@mail.com',
                'first_name': 'new',
                'last_name': 'new',
                'birth_date':'2000-01-01',
                'password1': 'Practica1',
                'password2': 'Practica1',
                'location': 'Sevilla',
                'sex': 'DK/NA',
                'g-recaptcha-response': 'PASSED',
                'username': 'new1'}

        # creamos el usuario
        response = self.client.post("/authentication/registerUser/", data=data, format="json", follow=True)
        self.assertEqual(response.status_code, 200)
        form = RegisterUserForm(data)
        self.assertTrue(form)
        self.assertTrue(form.is_valid())
        form.save()

        # intentamos crearlo de nuevo
        response = self.client.post("/authentication/registerUser/", data=data, format="json", follow=True)
        self.assertEqual(response.status_code, 200)
        form = RegisterUserForm(data)
        self.assertTrue(form)
        self.assertTrue(form.is_valid()==False) # email ya registrado




class ActivateTestCase(TestCase):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()


    def test_activation_link_OK(self):

        user1 = User(username='voter2')
        user1.set_password('123')
        user1.is_active = False
        user1.save()

        self.assertTrue(user1.is_active==False)
        
        token = default_token_generator.make_token(user1)
        uid = urlsafe_base64_encode(force_bytes(user1.pk)).decode()

        response = self.client.post("/authentication/activate/" + uid + "/" + token + "/", follow=True)
        self.assertEqual(response.status_code, 200)

        user2 = User.objects.get(username='voter2')
        self.assertTrue(user2.is_active)

    def test_activation_link_FAIL(self):

        random_token = '5wo-d4563ab1f1e95847929f'
        random_uid = 'MTUw'

        response = self.client.post("/authentication/activate/" + random_uid + "/" + random_token + "/", follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.content, b'Activation link is invalid!')

        

class HomeTestCase(TestCase):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()


    def test_get_home(self):

        response = self.client.post("/authentication/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        
        


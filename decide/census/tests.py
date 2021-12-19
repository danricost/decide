import random
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.testcases import TransactionTestCase
from authentication.models import Profile

from rest_framework.test import APIClient
from django.core.serializers import json
from .forms import CensusForm
from .models import Census
from base import mods
from base.tests import BaseTestCase
from voting.models import Question, Voting
from datetime import date

#Use TransactionTestCase instead of BaseTestCase
class CensusTestCase(TransactionTestCase):
    reset_sequences = True
    def setUp(self):
        super().setUp()
        question1 = Question.objects.create(desc='Question 1')
        voting1 = Voting.objects.create(id=10, name='Voting', question = question1)
        voting1.save()

        self.census = Census(voting_id=10, voter_id=1)
        self.census.save()
    
    def tearDown(self):
        super().tearDown()
        self.voting1 = None
        self.admin = None
        self.user1 = None
        self.user2 = None
        self.census = None
    
    def test_add_voter_custom_post(self):
        admin = User(username='admin2', password='qwerty')
        admin.is_staff = True
        admin.save()

        self.client.force_login(admin)
        response = self.client.post('/census/addCustom/', 
        data={'voting': ['10'], 'voter_ids': [admin.pk]})
        census = Census.objects.all()
        
        print('----------------------------------------------------------------------\n')
        print('Census: ', census)
        print(response)
        print('\n----------------------------------------------------------------------\n')
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(census), 1)
    
    def test_add_voter_custom_get(self):

        admin = User(username='admin2', password='qwerty')
        admin.is_staff = True
        admin.save()
        self.client.force_login(admin)
        response = self.client.get('/census/addCustom/')
        self.assertEqual(response.status_code, 200)
    
    def test_add_filters_post_sex(self):
        admin = User(username='admin2', password='qwerty')
        admin.is_staff = True
        admin.save()
        admin.profile.sex = 'Man'
        admin.profile.location = 'Sevilla'
        admin.profile.birth_date = date(year=2000, month=1, day=1)

        user1 = User(username='user1', password='qwerty')
        user1.save()
        user1.profile.sex = 'Man'
        user1.profile.location = 'Sevilla'
        user1.profile.birth_date = date(year=2000, month=1, day=1)

        user2 = User(username='user2', password='qwerty')
        user2.save()
        user2.profile.sex = 'Woman'
        user2.profile.location = 'Sevilla'
        user2.profile.birth_date = date(year=2000, month=1, day=1)

        self.client.force_login(user2)
        self.client.force_login(user1)
        self.client.force_login(admin)
        response = self.client.post('http://localhost:8000/admin/census/addFilters/', 
        data={'voting': ['10'], 'sex': ['Man'], 'city': [''], 'init_age': [''], 'fin_age': ['']})
        census = Census.objects.all()
      
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(census), 2)

    def test_add_filters_post_location(self):
        admin = User(username='admin2', password='qwerty')
        admin.is_staff = True
        admin.save()
        admin.profile.sex = 'Man'
        admin.profile.location = 'Sevilla'
        admin.profile.birth_date = date(year=2000, month=1, day=1)

        user1 = User(username='user1', password='qwerty')
        user1.save()
        user1.profile.sex = 'Man'
        user1.profile.location = 'Sevilla'
        user1.profile.birth_date = date(year=2000, month=1, day=1)

        user2 = User(username='user2', password='qwerty')
        user2.save()
        user2.profile.sex = 'Woman'
        user2.profile.location = 'Madrid'
        user2.profile.birth_date = date(year=2000, month=1, day=1)

        self.client.force_login(user2)
        self.client.force_login(user1)
        self.client.force_login(admin)
        response = self.client.post('http://localhost:8000/admin/census/addFilters/', 
        data={'voting': ['10'], 'location': ['Sevilla'], 'init_age': [''], 'fin_age': ['']})
        census = Census.objects.all()
        print('----------------------------------------------------------------------\n')
        print('Census: ', census)
        print(response)
        print('\n----------------------------------------------------------------------\n')
      
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(census), 2)

    def test_add_filters_post_birth_date(self):
        admin = User(username='admin2', password='qwerty')
        admin.is_staff = True
        admin.save()
        admin.profile.sex = 'Man'
        admin.profile.location = 'Sevilla'
        admin.profile.birth_date = date(year=1999, month=1, day=1)

        user1 = User(username='user1', password='qwerty')
        user1.save()
        user1.profile.sex = 'Man'
        user1.profile.location = 'Sevilla'
        user1.profile.birth_date = date(year=1999, month=1, day=1)

        user2 = User(username='user2', password='qwerty')
        user2.save()
        user2.profile.sex = 'Woman'
        user2.profile.location = 'Madrid'
        user2.profile.birth_date = date(year=2000, month=1, day=1)

        self.client.force_login(user2)
        self.client.force_login(user1)
        self.client.force_login(admin)
        response = self.client.post('http://localhost:8000/admin/census/addFilters/', 
        data={'voting': ['10'], 'location': [''], 'init_age': ['01/01/1998'], 'fin_age': ['12/12/1999']})
        census = Census.objects.all()
        print('----------------------------------------------------------------------\n')
        print('Census: ', census)
        print(response)
        print('\n----------------------------------------------------------------------\n')
      
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(census), 2)

    
    def test_add_filters_post_all(self):
        admin = User(username='admin2', password='qwerty')
        admin.is_staff = True
        admin.save()
        admin.profile.sex = 'Man'
        admin.profile.location = 'Sevilla'
        admin.profile.birth_date = date(year=1999, month=1, day=1)

        user1 = User(username='user1', password='qwerty')
        user1.save()
        user1.profile.sex = 'Man'
        user1.profile.location = 'Sevilla'
        user1.profile.birth_date = date(year=1999, month=1, day=1)

        user2 = User(username='user2', password='qwerty')
        user2.save()
        user2.profile.sex = 'Woman'
        user2.profile.location = 'Madrid'
        user2.profile.birth_date = date(year=2000, month=1, day=1)

        self.client.force_login(user2)
        self.client.force_login(user1)
        self.client.force_login(admin)
        response = self.client.post('http://localhost:8000/admin/census/addFilters/', 
        data={'voting': ['10']})
        census = Census.objects.all()
        print('----------------------------------------------------------------------\n')
        print('Census: ', census)
        print(response)
        print('\n----------------------------------------------------------------------\n')
      
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(census), 3)
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render

from .models import Census
from . import forms
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED as ST_201,
        HTTP_204_NO_CONTENT as ST_204,
        HTTP_400_BAD_REQUEST as ST_400,
        HTTP_401_UNAUTHORIZED as ST_401,
        HTTP_409_CONFLICT as ST_409
)

from base.perms import UserIsStaff
from django.contrib.auth.models import User
from http import HTTPStatus
from voting.models import Voting
from django.contrib import messages
from authentication.models import Profile

#has_voting_started = lambda v: v.start_date == None or v[0].start_date > timezone.now()


def validate_census_form(request, voting_id, voter_id):
    return True
    print('hola validate')
    voting = Voting.objects.filter(id = voting_id)
    voter = User.objects.filter(id=voter_id)
    
    logic_checks = [[request.user.is_staff, 'Access denied'],
            [voting, 'Voting with id '+str(voting_id)+' does not exist'],
            [voter, 'The user with id '+str(voter_id)+' does not exist']
            ]
    
    for check in logic_checks:
        if not check[0]:
            messages.add_message(request, messages.ERROR, check[1])
            print(check[1])
            return False
    
    census = Census.objects.filter(voting_id=voting_id, voter_id=voter_id)

    if census:
        messages.add_message(request, messages.ERROR, 'That census already exists!')
        return False
    elif voting.values()[0].get('end_date'):
        messages.add_message(request, messages.ERROR, 'Voting already closed!')
        return False    
    else:
        return True


def add_to_census(request, voting_id, voter_id):    
    if validate_census_form(request, voting_id, voter_id):
        try:
            census = Census(voting_id=voting_id, voter_id=voter_id)
            print('hola census')
            census.save()
        except:
            return HttpResponseRedirect('/admin')
    

def add_filtered(request):
    if request.method == 'POST':
        print('HOLA POST') 
        form = forms.FilteredCensusForm(request.POST)
        print(request.POST)
        print(form.errors)
        if form.is_valid():
            print('HOLA FORM')
            voting_id = form.cleaned_data['voting'].__getattribute__('pk')
            selected_sex = form.cleaned_data['sex']
            selected_city = form.cleaned_data['city']
            selected_init_age = form.cleaned_data['init_age']
            selected_fin_age = form.cleaned_data['fin_age']
            voters = Profile.objects.all()
            #Filter by sex
            voters = voters.filter(sex__in=selected_sex) if len(selected_sex) != 0 else voters
            #Filter by city
            voters = voters.filter(city__iexact=selected_city) if len(selected_city) != 0 else voters
            #Filter by age
            voters = voters.filter(birthdate__gte=selected_init_age) if selected_init_age is not None else voters
            voters = voters.filter(birthdate__lte=selected_fin_age) if selected_fin_age is not None else voters
            print(voters)

            if voters:
                for voter in voters:
                    print('Hola add')
                    add_to_census(request, voting_id, voter.id)
            
            return HttpResponseRedirect('/admin/census')
            
    else:
        form = forms.FilteredCensusForm()
    return render(request, 'create_census_filters.html', {'form':form})


class CensusCreate(generics.ListCreateAPIView):
    permission_classes = (UserIsStaff,)

    def create(self, request, *args, **kwargs):
        voting_id = request.data.get('voting_id')
        voters = request.data.get('voters')
        try:
            for voter in voters:
                census = Census(voting_id=voting_id, voter_id=voter)
                census.save()
        except IntegrityError:
            return Response('Error try to create census', status=ST_409)
        return Response('Census created', status=ST_201)

    def list(self, request, *args, **kwargs):
        voting_id = request.GET.get('voting_id')
        voters = Census.objects.filter(voting_id=voting_id).values_list('voter_id', flat=True)
        return Response({'voters': voters})


class CensusDetail(generics.RetrieveDestroyAPIView):

    def destroy(self, request, voting_id, *args, **kwargs):
        voters = request.data.get('voters')
        census = Census.objects.filter(voting_id=voting_id, voter_id__in=voters)
        census.delete()
        return Response('Voters deleted from census', status=ST_204)

    def retrieve(self, request, voting_id, *args, **kwargs):
        voter = request.GET.get('voter_id')
        try:
            Census.objects.get(voting_id=voting_id, voter_id=voter)
        except ObjectDoesNotExist:
            return Response('Invalid voter', status=ST_401)
        return Response('Valid voter')

def create_census(request):
    if request.method == 'POST':
        form = forms.CensusForm(request.POST)
        print(request.POST)
        print(form.errors)
        if form.is_valid():
            voting_id = form.cleaned_data['voting'].pk
            voter_ids = form.cleaned_data['voter_ids']
            for voter_id in voter_ids:
                print("Hola FORM2")
                add_to_census(request, voting_id, voter_id)
            return HttpResponseRedirect('/admin/census')
    else:
        form = forms.CensusForm()
        print("Hola")
    return render(request, 'create_census.html', {'form':form}, status=HTTPStatus.OK)
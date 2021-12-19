from django import forms
from django.contrib.auth.models import User
from django.forms import widgets
from voting.models import Voting

class CensusForm(forms.Form):

    t_ids1 = tuple((u.get('id'), "Id: "+str(u.get('id'))+" Nombre: "+str(u.get('first_name'))) for u in User.objects.values())
    t_ids2 = tuple((v.get('id'), str(v.get('name'))) for v in Voting.objects.all().filter(end_date__isnull=True).values())

    '''voting_id = forms.ChoiceField(label='Open votings', choices=t_ids2, required=True,
    widget=forms.Select(attrs={'style': 'width: 300px;','class': 'form-control'}))'''

    voting = forms.ModelChoiceField(label='Open votings', empty_label="-", queryset=Voting.objects.all().filter(end_date__isnull=True), required=True,
    widget=forms.Select(attrs={'style': 'width: 300px;','class': 'form-control'}))
    
    voter_ids = forms.MultipleChoiceField(choices=t_ids1, required=True, widget=forms.CheckboxSelectMultiple(), label='Select No')
class FilteredCensusForm(forms.Form):
    voting = forms.ModelChoiceField(label='Open votings', empty_label="-", queryset=Voting.objects.all().filter(end_date__isnull=True), required=True,
    widget=forms.Select(attrs={'style': 'width: 300px;','class': 'form-control'}))

    SEX_OPTIONS = (('Man', 'Man'), ('Woman', 'Woman'), ('DK/NA', 'DK/NA'))
    sex = forms.MultipleChoiceField(label='Sex',choices=SEX_OPTIONS,required=False,
    widget=forms.SelectMultiple(attrs={'style': 'width: 110px;','class': 'form-control'}))

    location = forms.CharField(label='Location', required=False,
    widget=forms.TextInput(attrs={'style': 'width: 150px;','class': 'form-control'}))

    init_age = forms.DateField(label='Initial age', widget=forms.TextInput(attrs={'placeholder': 'Format: dd/mm/yyyy', 'style': 'width: 200px;','class': 'form-control'}), 
    input_formats=['%d/%m/%Y'], required=False)

    fin_age = forms.DateField(label='Final age', widget=forms.TextInput(attrs={'placeholder': 'Format: dd/mm/yyyy','style': 'width: 200px;','class': 'form-control'}),
    input_formats=['%d/%m/%Y'],required=False)
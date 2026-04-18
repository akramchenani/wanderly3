from django import forms

class FlightSearchForm(forms.Form):
    origin = forms.CharField(max_length=100, label='From')
    destination = forms.CharField(max_length=100, label='To')
    departure_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    return_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    flight_type = forms.ChoiceField(choices=[('one_way', 'One Way'), ('round_trip', 'Round Trip')])
    passengers = forms.IntegerField(min_value=1, max_value=9, initial=1)

from django import forms


class Search(forms.Form):
    n = forms.IntegerField(help_text="number of items to show")
    max_date = forms.DateTimeField(help_text="max date, default=NOW", required=False, widget=forms.DateInput(attrs={'class':'datetimepickerfield'}))
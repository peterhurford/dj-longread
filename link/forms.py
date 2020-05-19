from django import forms

class LinkForm(forms.Form):
    url = forms.CharField(label='url', max_length=2000)
    title = forms.CharField(label='title', max_length=2000)
    summary = forms.CharField(label='summary', max_length=10000)
    category = forms.CharField(label='category', max_length=2000)
    aggregator = forms.CharField(label='aggregator', max_length=2000)
    liked = forms.IntegerField(label='liked')

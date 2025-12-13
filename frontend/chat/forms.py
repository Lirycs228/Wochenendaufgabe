from django import forms


class AskForm(forms.Form):
    ask = forms.CharField(label="ask", max_length=1000)
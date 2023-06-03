from django import forms

class UploadFileForm(forms.Form):
    name = forms.CharField(max_length=255, required=True)
    file = forms.ImageField()

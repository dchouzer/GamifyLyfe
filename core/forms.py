from django import forms

class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file to upload',
        help_text='max size is 42 MB'
    )
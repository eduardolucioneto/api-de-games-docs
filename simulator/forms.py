from django import forms


class DiagramUploadForm(forms.Form):
    diagram = forms.FileField(
        label='Diagrama unifilar em PDF',
        help_text='Envie o esquema elétrico da subestação.',
        widget=forms.ClearableFileInput(attrs={'accept': 'application/pdf'})
    )

    def clean_diagram(self):
        uploaded = self.cleaned_data['diagram']
        if uploaded.content_type not in ['application/pdf', 'application/octet-stream']:
            raise forms.ValidationError('Envie um arquivo em PDF.')
        return uploaded

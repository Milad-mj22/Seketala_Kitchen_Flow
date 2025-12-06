from django import forms

from utils.models import TicketMessage,Ticket


class CSVUploadForm(forms.Form):
    file = forms.FileField(label='آپلود فایل CSV')



class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'message', 'category']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }
        labels = {
            'title': 'عنوان',
            'message': 'پیام',
            'category': 'دسته‌بندی'
        }

class TicketMessageForm(forms.ModelForm):
    class Meta:
        model = TicketMessage
        fields = ['message', 'attachment']
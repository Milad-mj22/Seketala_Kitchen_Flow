# forms.py
from django import forms
from django.contrib.auth.models import User
from .models import AttributeGroup, Cutting_factory, Driver, CarModel,Step





PERSIAN_LETTERS = [
    ('الف', 'الف'), ('ب', 'ب'), ('پ', 'پ'), ('ت', 'ت'),
    ('ث', 'ث'), ('ج', 'ج'), ('چ', 'چ'), ('د', 'د'),
    ('ر', 'ر'), ('ز', 'ز'), ('س', 'س'), ('ص', 'ص'),
    ('ط', 'ط'), ('ق', 'ق'), ('ک', 'ک'), ('گ', 'گ'),
    ('ل', 'ل'), ('م', 'م'), ('ن', 'ن'), ('و', 'و'),
    ('ه', 'ه'), ('ی', 'ی'),
]

class LicensePlateWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = [
            forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'دو رقم اول', 'maxlength': '2'}),
            forms.Select(choices=PERSIAN_LETTERS, attrs={'class': 'form-select'}),
            forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'سه رقم وسط', 'maxlength': '3'}),
            forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'دو رقم آخر', 'maxlength': '2'}),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            parts = value.split('-')
            if len(parts) == 4:
                return parts
        return ['', '', '', '']
    

class LicensePlateField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = [
            forms.CharField(max_length=2),
            forms.ChoiceField(choices=PERSIAN_LETTERS),
            forms.CharField(max_length=3),
            forms.CharField(max_length=2),
        ]
        super().__init__(fields=fields, widget=LicensePlateWidget(), *args, **kwargs)



    def compress(self, data_list):
        if data_list:
            return f"{data_list[0]}-{data_list[1]}-{data_list[2]}-{data_list[3]}"
        return ''


class DriverRegisterForm(forms.ModelForm):
    username = forms.CharField(
        label='نام کاربری',  # ✅ برچسب فارسی
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام کاربری'})
    )
    password = forms.CharField(
        label='رمز عبور',  # ✅ برچسب فارسی
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'رمز عبور'})
    )
    first_name = forms.CharField(
        label='نام',  # ✅ برچسب فارسی
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام'})
    )
    last_name = forms.CharField(
        label='نام خانوادگی',  # ✅ برچسب فارسی
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام خانوادگی'})
    )

    license_plate = LicensePlateField(
        label="پلاک خودرو",
        required=True
    )

    class Meta:
        model = Driver
        fields = ['username', 'first_name', 'last_name', 'password', 'national_code', 'car_model', 'car_code', 'license_plate']
        widgets = {
            'national_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'کد ملی'}),
            'car_model': forms.Select(attrs={'class': 'form-control'}),
            'car_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'کد خودرو'}),
        }
        labels = {
            'national_code': 'کد ملی',
            'car_model': 'مدل خودرو',
            'car_code': 'کد خودرو',
            'license_plate': 'پلاک خودرو',
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        # اگر instance موجود است (در حالت ویرایش) و نام کاربری عوض نشده، مشکلی نیست
        if self.instance.pk:
            user_qs = User.objects.filter(username=username).exclude(pk=self.instance.user.pk)
        else:
            user_qs = User.objects.filter(username=username)

        if user_qs.exists():
            raise forms.ValidationError("این نام کاربری قبلاً استفاده شده است.")
        return username


from .models import CoopAttribute




class CoopAttributeForm(forms.ModelForm):
    class Meta:
        model = CoopAttribute
        fields = ['label', 'field_type', 'required', 'default_value', 'step', 'select_options']
        labels = {
            'label': 'عنوان فیلد',
            'field_type': 'نوع فیلد',
            'required': 'الزامی است؟',
            'default_value': 'مقدار پیش‌فرض',
            'step': 'مرحله نمایش',
            'select_options': 'گزینه‌های منوی کشویی',
        }
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control'}),
            'field_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_field_type'}),
            'required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'default_value': forms.TextInput(attrs={'class': 'form-control'}),
            'step': forms.Select(attrs={'class': 'form-select'}),  # 👈 همین فیلد از STEP_CHOICES می‌خونه
            'select_options': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثلاً: کوچک,متوسط,بزرگ'}),
        }




    def clean(self):
        cleaned_data = super().clean()
        field_type = cleaned_data.get('field_type')
        select_options = cleaned_data.get('select_options')

        if field_type == 'select' and not select_options:
            self.add_error('select_options', 'برای منوی کشویی باید گزینه‌ها را وارد کنید.')


class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ['title', 'order', 'url_name']
        labels = {
            'title': 'عنوان مرحله',
            'order': 'ترتیب نمایش',
            'url_name': 'نام در URL (انگلیسی)'
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'url_name': forms.TextInput(attrs={'class': 'form-control'}),
        }





class AttributeGroupForm(forms.ModelForm):
    class Meta:
        model = AttributeGroup
        fields = ['name', 'attributes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'attributes': forms.SelectMultiple(attrs={'class': 'form-select multi-select', 'multiple': 'multiple'})
        }
        labels = {
            'name': 'نام گزارش',
            'attributes': 'ویژگی‌های انتخابی'
        }
    

class CuttingFactoryForm(forms.ModelForm):
    class Meta:
        model = Cutting_factory
        fields = ['name', 'city']
        labels = {
            'name': 'نام',
            'city': 'شهر',

        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
        }
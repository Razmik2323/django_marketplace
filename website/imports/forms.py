from django import forms

class ImportProductsForm(forms.Form):
    """Форма для загрузки JSON файла с продуктами."""
    json_file = forms.FileField(label='Выберите JSON файл')
    email = forms.EmailField(label='Введите ваш адрес электронной почты', required=True)
import json

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ImportProductsForm
from catalog.models import Category, Product
import os

from .utils import send_import_notification

def import_products_view(request):
    """View для импорта продуктов из JSON файла."""
    if request.method == 'POST':
        form = ImportProductsForm(request.POST, request.FILES)
        if form.is_valid():
            json_file = request.FILES['json_file']
            recipient_email = form.cleaned_data['email']

            # Определяем пути для хранения импортированных файлов
            success_dir = os.path.join('media', 'imported', 'success')
            failure_dir = os.path.join('media', 'imported', 'failure')

            # Создаем директории, если они не существуют
            os.makedirs(success_dir, exist_ok=True)
            os.makedirs(failure_dir, exist_ok=True)

            try:
                data = json.load(json_file)
                success_count = 0
                failure_count = 0

                for item in data:
                    try:
                        category, _ = Category.objects.get_or_create(name=item['category'])
                        product = Product(
                            name=item['name'],
                            description=item['description'],
                            manufacture=item['manufacture'],
                            category=category,
                            archived=item.get('archived', False),
                            limited_edition=item.get('limited_edition', False),
                        )
                        product.save()
                        success_count += 1

                    except Exception as e:
                        # Записываем информацию о неуспешном импорте в файл
                        with open(os.path.join(failure_dir, 'failed_imports.txt'), 'a', encoding='utf-8') as fail_file:
                            fail_file.write(f'Failed to import {item["name"]}: {str(e)}\n')
                        failure_count += 1

                # Перемещаем файл в директорию успешного импорта
                with open(os.path.join(success_dir, json_file.name), 'wb+') as destination:
                    for chunk in json_file.chunks():
                        destination.write(chunk)

                # Отправка уведомления по электронной почте
                send_import_notification(recipient_email, success_count, failure_count)

                messages.success(request,
                                 f'Импорт завершен! Успешно импортировано: {success_count}, Неуспешно: {failure_count}')
                return redirect('../../admin/')

            except Exception as e:
                messages.error(request, f'Ошибка при импорте: {str(e)}')
    else:
        form = ImportProductsForm()

    return render(request, 'admin/import_products.html', {'form': form})

import os
import json
from django.conf import settings
from celery import shared_task
from catalog.models import Category, Product
from .utils import send_import_notification


@shared_task(bind=True)
def import_products(self, file_path: str) -> None:
    """Импортирует товары из указанного файла."""

    log_file_path = os.path.join(settings.MEDIA_ROOT, 'logs', f'import_log_{os.path.basename(file_path)}.txt')
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                category, _ = Category.objects.get_or_create(name=item['category'])
                product = Product(
                    name=item['name'],
                    description=item['description'],
                    manufacture=item['manufacture'],
                    category=category,
                    archived=item.get('archived', False),
                    limited_edition=item.get('limited_edition', False),
                    view=item.get('view', False),
                )
                product.save()

                with open(log_file_path, 'a', encoding='utf-8') as log_file:
                    log_file.write(f'Successfully imported: {product.name}\n')

        return f'Successfully imported from {file_path}'

    except Exception as e:
        with open(log_file_path, 'a', encoding='utf-8') as log_file:
            log_file.write(f'Error importing from {file_path}: {str(e)}\n')
        self.retry(exc=e)


@shared_task
def notify_import_result(recipient_email, success_count, failure_count):
    """Задача для отправки уведомления о результате импорта."""
    send_import_notification(recipient_email, success_count, failure_count)
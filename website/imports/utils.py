from django.core.mail import send_mail

def send_import_notification(recipient_email, success_count, failure_count):
    """Отправляет уведомление о результате импорта продуктов."""
    subject = "Результат импорта продуктов"
    message = f"Импорт завершен! Успешно импортировано: {success_count}, Неуспешно: {failure_count}."
    from_email = 'aa@gmail.com'  # Ваш адрес электронной почты

    send_mail(subject, message, from_email, [recipient_email])


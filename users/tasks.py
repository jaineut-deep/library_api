from celery import shared_task
from collections import defaultdict
from config.settings import DEFAULT_FROM_EMAIL
from datetime import timedelta
from django.core.mail import send_mail
from django.utils import timezone
from typing import Any
from .models import LendingBook


@shared_task
def send_update_lending_mail(member_email: str, is_created: bool, procedure: str, book: str) -> None:
    if DEFAULT_FROM_EMAIL is None:
        raise RuntimeError("DEFAULT_FROM_EMAIL не настроен")
    if is_created:
        subject_text = "Поступление запроса на выдачу книги"
        message_text = f"Уважаемый регистратор, поступил заказ на выдачу книги {book} от читателя {member_email}"
        users_emails = [DEFAULT_FROM_EMAIL]
        send_mail(
            subject=subject_text,
            message=message_text,
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=users_emails,
        )
    elif not is_created:
        subject_text = ""
        message_text = ""
        users_emails = [member_email]
        if procedure == "permit":
            subject_text = "Продление выдачи книги по абонементу"
            message_text = f"Уважаемый читатель, по вашему запросу, вам продлена выдача книги {book} по абонементу"
        elif procedure == "deny":
            subject_text = "Продление выдачи книги по абонементу"
            message_text = (f"Уважаемый читатель, к сожалению, на данный момент, "
                            f"в продлении выдачи книги {book} вам отказано")
        elif procedure == "renewal":
            subject_text = "Поступление запроса на продление выдачи книги"
            message_text = (f"Уважаемый регистратор, поступил заказ на продление выдачи книги "
                            f"{book} от читателя {member_email}")
            users_emails = [DEFAULT_FROM_EMAIL]
        send_mail(
            subject=subject_text,
            message=message_text,
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=users_emails,
        )


@shared_task
def suspend_lending_member() -> None:
    week_date = timezone.now() - timedelta(days=7)
    query_set = LendingBook.objects.filter(status=True, updated_at__lt=week_date)

    if query_set:
        query_set.update(status=False)
        lendings = LendingBook.objects.filter(status=False).select_related("member", "publication__book")
        books_by_email: defaultdict[Any, dict] = defaultdict(dict)
        for lending in lendings:
            book = lending.publication.book
            books_by_email[lending.member.email][book.pk] = book
        result = {email: [book.title for book in books.values()] for email, books in books_by_email.items()}
        for member_email, books_title in result.items():
            if member_email is None:
                continue

            users_emails = [member_email]
            subject_text = "Выдача книги по абонементу"
            message_text = (f"Уважаемый читатель, срок выдачи книг {books_title} по абонементу истек."
                            f"Пожалуйста, продлите.")
            send_mail(
                subject=subject_text,
                message=message_text,
                from_email=DEFAULT_FROM_EMAIL,
                recipient_list=users_emails,
            )

from project.celery import app


@app.task()
def main_docs_emails_send():
    from main.services.email_notification import EmailNotificationService
    EmailNotificationService.make_instance_and_send_emails()

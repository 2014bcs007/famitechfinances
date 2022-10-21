from django.core.mail import send_mail,EmailMessage
import threading


def send_email(subject='',body='',mail_from=None, mail_to=[],cc=[],bcc=[],attachments=None):
    # mail_from=mail_from if mail_from is not None else 
    mail=EmailMessage(
        subject,         #Subject
        body, #Message
        mail_from,     #From
        mail_to,     #To
        headers={'Message-ID':'Random'},
        cc=cc,
        bcc=bcc
    )
    if attachments:
        for f in attachments:
            mail.attach(f.name, f.read(), f.content_type)
    
    mail.send(fail_silently=False)
    # EmailThread(mail).start()


class EmailThread(threading.Thread):
    def __init__(self,email):
        self.email=email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=True,)

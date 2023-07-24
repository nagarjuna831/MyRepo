import os
from django.core.mail import send_mail
from sendgrid import SendGridAPIClient 
from sendgrid.helpers.mail import Mail 
from sendgrid.helpers.mail import Mail, Email, To, Content


sg=SendGridAPIClient('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')
from_email = Email("eform@epsumlabs.in")  # Change to your verified sender

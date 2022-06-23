"""
Helper functions for gworkspace-ifts18-helper package.
"""
import base64
import csv
from email.message import EmailMessage
import json
import string
import secrets

import typer
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from faker import Faker

from .constants import (
    INSCRIPTIONS_EMAIL,
    STUDENTS_ORGUNIT_PATH,
    STUDENTS_DOMAIN,
    DEFAULT_PASSWORD_LENGTH,
    DEFAULT_PASSWORD_NUMBER_DIGITS,
    SCOPES,
    GWORKSPACE_OWNER,
    INSCRIPTIONS_EMAIL_HEADER,
    NO_REPLY_EMAIL,
    )


def generate_password(
    length=DEFAULT_PASSWORD_LENGTH,
    digits=DEFAULT_PASSWORD_NUMBER_DIGITS,
):
    """Generate a ten-character alphanumeric password with at least one lowercase character, at least one uppercase character, and at least three digits.
    
    Example from Python Docs: https://docs.python.org/3/library/secrets.html
    """
    alphabet = string.ascii_letters + string.digits
    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and sum(c.isdigit() for c in password) >= digits):
            break
    return password


def create_student_body_payload(
    student_firstname,
    student_lastname,
    student_email,
    password=None,
    email_domain=STUDENTS_DOMAIN,
    orgUnitPath=STUDENTS_ORGUNIT_PATH,
    **kwargs,
):
    """Create the body of the request to create a student account."""
    if password is None:
        # TODO: read kwargs and modify generate_password accordingly
        generated_password = generate_password()
    else:
        generated_password = password

    table = str.maketrans("áéíóúñ", "aeioun")

    user = {
        "emails": [
            {
                "address": student_email,
                "primary": True,
            },
        ], 
        "name": {
            "familyName": student_lastname.strip(),
            "givenName": student_firstname.strip(),
            "fullName": f"{student_firstname} {student_lastname.strip()}", 
        },
        "changePasswordAtNextLogin": True,
        "primaryEmail": f"{student_firstname.split()[0].lower().strip().translate(table)}.{student_lastname.split()[0].strip().lower().translate(table)}@{email_domain}",
        "password": generated_password,
        "orgUnitPath": orgUnitPath,
    }
    return user


def read_students_csv(filename):
    "Reads Students CSV and returns a list of dicts with the students data"
    students = []
    with open(filename) as csvfile:
        studentreader = csv.DictReader(csvfile)
        for student in studentreader:
            students.append(student)
    return students


def create_email_message(
    to_address,
    from_address,
    no_reply_address,
    subject,
    body,
    dry_run=False
):
    """Create an email message."""
    message = EmailMessage()

    message.set_content(body)

    # email headers
    message['To'] = to_address
    message['From'] = from_address
    message['Reply-To'] = no_reply_address
    message['Subject'] = subject
    
    if dry_run:
        typer.echo(f"Message: {message}")
    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {
        'raw': encoded_message,
    }
    return create_message, message


def create_admin_service(credentials_path, scopes=SCOPES, subject=GWORKSPACE_OWNER):
    """Create a Google Admin Service."""

    service_account_info = json.load(open(credentials_path))

    credentials = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=scopes)

    delegated_creds = credentials.with_subject(subject)

    admin_service = build('admin', 'directory_v1', credentials=delegated_creds)

    return admin_service


def create_gmail_service(credentials_path, scopes=SCOPES, subject=INSCRIPTIONS_EMAIL):
    """Create a Google Gmail Service."""
    service_account_info = json.load(open(credentials_path))
    
    credentials = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=scopes)
    
    delegated_creds = credentials.with_subject(subject)

    gmail_service = build('gmail', 'v1', credentials=delegated_creds)

    return gmail_service


def _create_accounts_and_send_mails_dry_run(
    students,
    dry_run=False,
):
    """Create accounts and send emails to students. Returns a student list with status."""

    for student in students:
        typer.echo(f"Preparing account for {student['NOMBRE']} {student['APELLIDO']}")

        user = create_student_body_payload(
            student['NOMBRE'],
            student['APELLIDO'],
            student['MAIL']
        )

        encoded_message, message = create_email_message(
            to_address=f"{user['name']['fullName']} <{user['emails'][0]['address']}>",
            from_address=INSCRIPTIONS_EMAIL_HEADER,
            no_reply_address=NO_REPLY_EMAIL,
            subject=f"[NO RESPONDER] Tu nueva cuenta del IFTS18 ha sido creada!",
            body=f"""Hola {user['name']['fullName']}!

Tu nueva cuenta {user['primaryEmail']}. Podés acceder a ella desde el siguiente link:
https://mail.google.com con la clave {user['password']}.
Se te va a pedir que cambies esta clave por una tuya al momento del primer ingreso.

Cualquier duda, contactate con el admin de tu dominio {GWORKSPACE_OWNER}.
""",
        )

        if dry_run:
            typer.echo(f"Message: {message}")

        student["message"] = message.as_string()
        student["encoded_message"] = encoded_message
        student["user"] = user
        student["account"] = "DRY-RUN"
        student["notification"] = "DRY-RUN"
        student["status"] = "SUCCESS"

    return students


def create_accounts_and_send_mails(
    students,
    admin_service,
    gmail_service,
    dry_run=False,
):
    """Create accounts and send emails to students. Returns a student list with status."""
    students = _create_accounts_and_send_mails_dry_run(
        students=students, dry_run=dry_run)

    if dry_run:
        return students

    account = None
    for student in students:
        typer.echo(f"Creating account for {student['NOMBRE']} {student['APELLIDO']}")

        try:
            account = admin_service.users().insert(body=student["user"]).execute()
            student["account"] = account 
            student["status"] = "ACCOUNT_SUCCESS"
        except HttpError as error:
            student["account"] = str(error)
            student["status"] = "ACCOUNT_ERROR"

        try:
            if account:
                mail = gmail_service.users().messages().send(
                    userId='me', body=student["encoded_message"]).execute()
                student["notification"] = mail
                student["status"] = "SUCCESS"
        except HttpError as error:
            student["notification"] = str(error)
            student["status"] = "NOTIFICATION_ERROR"

    return students

def create_example_CSV(filename_path="assets/example.csv", examples=10):
    fake = Faker('es')
    students = []

    for i in range(examples):
        students.append(
            {
                "N°": i + 1,
                "APELLIDO": fake.last_name(),
                "NOMBRE": fake.first_name(),
                "DNI": fake.ssn(),
                "MAIL": fake.email(),
            }
        )

    with open(filename_path, "w") as fd:
        studentwriter = csv.DictWriter(fd, fieldnames=students[0].keys())
        for student in students:
            studentwriter.writerow(student)

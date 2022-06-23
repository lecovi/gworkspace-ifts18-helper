"""
Main file for the gworkspace-ifts18-helper package.
"""
import json

import typer

from .helpers import (
    read_students_csv,
    create_admin_service,
    create_gmail_service,
    create_accounts_and_send_mails,
    create_example_CSV,
)
from .constants import ACCOUNTS_LOGFILE


app = typer.Typer()


@app.command()
def create_accounts(
    csv: str = typer.Option(..., help="Path to the CSV file with the students data"),
    credentials: str = typer.Option(..., help="Path to the credentials file"),
    dry_run: bool = typer.Option(False, help="Run without creating accounts."),
    log: bool = typer.Option(False, help="Run with logs."),
):
    """Create accounts for students. Reads CSV, create admin and gmail service. Create accounts and send mails."""

    students = read_students_csv(csv)
    total_students = len(students)
    typer.echo(f"Read {total_students} students")

    admin_service = create_admin_service(credentials_path=credentials)
    gmail_service = create_gmail_service(credentials_path=credentials)

    accounts = create_accounts_and_send_mails(
        students=students,
        admin_service=admin_service,
        gmail_service=gmail_service,
        dry_run=dry_run,
    )

    total_success_accounts = len([
        account for account in accounts if account['status'] == "SUCCESS"
    ])
    typer.echo(f"SUCCESS {total_success_accounts}")
    typer.echo(f"ACCOUNT_SUCCESS: {len([account for account in accounts if account['status'] == 'ACCOUNT_SUCCESS'])}")
    typer.echo(f"ACCOUNT_ERROR: {len([account for account in accounts if account['status'] == 'ACCOUNT_ERROR'])}")
    typer.echo(f"NOTIFICATION_ERROR: {len([account for account in accounts if account['status'] == 'NOTIFICATION_ERROR'])}")

    if total_students != total_success_accounts or log:
        typer.echo(f"ERRORS detected. Check the logs.")
        with (open(ACCOUNTS_LOGFILE, "w")) as f:
            json.dump(accounts, f, indent=2)

@app.command()
def version():
    typer.echo("Version 0.1.0")


@app.command()
def create_example_csv(
    csv: str = typer.Option(
            "assets/example.csv", 
            help="Path to the CSV file with the students data"
            ),
    examples: int = typer.Option(10, help="How many examples you want. Default: 10"),
):
    create_example_CSV(filename_path=csv, examples=examples)
    

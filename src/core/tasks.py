"""
Celery tasks for account setup.

This task is used to setup the account for a new user after they have verified their email.
"""

from celery import shared_task

from core.service.account_setup_service import AccountSetupService


@shared_task
def setup_account(user_id: int):
    AccountSetupService.setup_account(user_id)

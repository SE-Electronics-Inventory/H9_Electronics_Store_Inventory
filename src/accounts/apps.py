from django.apps import AppConfig
from django.db.models.signals import post_migrate


class AccountsConfig(AppConfig):
    name = "accounts"

    def ready(self):
        # FR-14: create Admin / Staff / Manager groups after every migrate
        post_migrate.connect(_create_roles, sender=self, dispatch_uid="accounts_setup_roles")


def _create_roles(sender, **kwargs):
    from .roles import setup_roles

    setup_roles()

"""App configuration for the demo project."""

from django.apps import AppConfig, apps
from django.db.models.signals import post_migrate


def name_the_site(sender, **kwargs):
    """Name the example site after the project, for the shell's page titles."""
    from django.conf import settings
    from django.contrib.sites.models import Site

    Site.objects.update_or_create(
        pk=settings.SITE_ID,
        defaults={"domain": "localhost:8022", "name": "django-mvp-accounts"},
    )


class DemoConfig(AppConfig):
    """Demo app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "demo"
    verbose_name = "Demo"

    def ready(self):
        """Register the sidebar entries and the site-naming hook."""
        from demo import menus  # noqa: F401

        # Hung off the sites app so its table exists, and connected before
        # SiteConfig.ready() so the packaged example.com row is never created.
        post_migrate.connect(name_the_site, sender=apps.get_app_config("sites"))

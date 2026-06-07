"""Enable the self-host feature flags so the full upload UI is available.

The app uses django-waffle feature flags to gate several upload-page features.
A fresh database has no flag rows, and waffle treats an undefined flag as
*inactive* — which hides the advanced options (max gaussians / training steps),
background removal, and the filter picker. This command creates those flags as
active-for-everyone.

It's idempotent and safe to run on every startup (including on an
already-initialized database): it uses ``get_or_create``, so it only creates
flags that are missing and leaves any flag an operator has since toggled in the
Django admin untouched.

Reconstruction-method selection and billing/promo flags are intentionally left
off.
"""

from django.core.management.base import BaseCommand

# Feature flags turned on by default in the self-host build.
DEFAULT_ON_FLAGS = [
    "enable_advanced_options",   # max gaussians + training steps
    "enable_remove_background",  # background removal
    "enable_pilgram_filters",    # Instagram-style filters
]


class Command(BaseCommand):
    help = "Enable self-host feature flags (idempotent; respects later admin changes)."

    def handle(self, *args, **options):
        from waffle.models import Flag

        created = existing = 0
        for name in DEFAULT_ON_FLAGS:
            _, was_created = Flag.objects.get_or_create(
                name=name, defaults={"everyone": True}
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"  enabled flag '{name}'"))
            else:
                existing += 1

        self.stdout.write(
            f"Feature flags: {created} created, {existing} already present."
        )

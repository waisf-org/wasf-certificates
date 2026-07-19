from django.core.files import File
from django.core.management.base import BaseCommand

from issuer.models import Issuer

# Repo-relative path to the real WASF logo (W-ribbon mark + wordmark), also
# used for wasf-website's own branding — see apps/mainsite/static/images/Logo-Wasf.png.
LOGO_PATH = "apps/mainsite/static/images/Logo-Wasf.png"

WASF_INFO = dict(
    name="World AI Sports Federation (WASF)",
    description=(
        "World AI Sports Federation (WASF) is a New York not-for-profit corporation building "
        "international standards, certification, and rankings for AI-assisted sports. Its "
        "501(c)(3) tax-exempt status application is currently pending IRS approval."
    ),
    url="https://waisf.org",
    email="admin@waisf.org",
    country="United States",
    state="NY",
    city="Flushing",
    zip="11354",
    street="Union St, Apt 7D",
    streetnumber="38-08",
)


class Command(BaseCommand):
    help = (
        "Fix the WASF issuer record's public-facing info (name/description/url/email/address/"
        "logo) to real values instead of whatever placeholder was entered when it was first "
        "created through the normal signup+issuer-create UI flow. Does NOT create a new Issuer — "
        "an Issuer needs a real created_by user/owner, which this command can't safely fabricate. "
        "If no WASF issuer exists yet, create one via the normal UI flow first, then re-run this."
    )

    def handle(self, *args, **options):
        issuer = Issuer.objects.filter(name__icontains="WASF").first()
        if not issuer:
            self.stdout.write(self.style.WARNING(
                "No issuer with 'WASF' in its name found — nothing to fix. Create the WASF "
                "issuer via the normal signup + /issuer/create flow first, then re-run this "
                "command to correct its info."
            ))
            return

        for field, value in WASF_INFO.items():
            setattr(issuer, field, value)

        try:
            with open(LOGO_PATH, "rb") as f:
                issuer.image.save("wasf_issuer_logo.png", File(f), save=False)
        except FileNotFoundError:
            self.stdout.write(self.style.WARNING(f"Logo file not found at {LOGO_PATH} — leaving existing image untouched."))

        issuer.save()
        self.stdout.write(self.style.SUCCESS(f"Updated issuer {issuer.pk}: {issuer.name}"))

"""GEO Service page type: model, public page, Service + FAQPage JSON-LD, sitemap."""

import json
import re

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.content.models import Service, Status

User = get_user_model()
pytestmark = pytest.mark.django_db

LD_BLOCK = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL)


def _ld_nodes(html: str) -> list[dict]:
    return [json.loads(m) for m in LD_BLOCK.findall(html)]


@pytest.fixture
def author():
    return User.objects.create_user(username="writer")


@pytest.fixture
def service(author):
    return Service.objects.create(
        title="SEO Audits",
        summary="We audit websites for technical SEO and GEO readiness.",
        description="<p>Full audit.</p><script>evil()</script>",
        price="From $499",
        area_served="Worldwide",
        faq="Q: How long does it take?\nA: About two weeks.\nQ: Do you offer refunds?\nA: Yes.",
        author=author,
        status=Status.PUBLISHED,
    )


# --------------------------------------------------------------------------- #
# Model
# --------------------------------------------------------------------------- #
def test_service_slug_sanitize_and_faq_parse(service):
    assert service.slug == "seo-audits"
    assert "<script>" not in service.description  # sanitized
    assert service.faq_items() == [
        ("How long does it take?", "About two weeks."),
        ("Do you offer refunds?", "Yes."),
    ]


def test_service_seo_description_prefers_summary(service):
    assert service.seo_description() == "We audit websites for technical SEO and GEO readiness."


def test_service_is_translatable(service):
    service.set_current_language("de")
    service.title = "SEO-Audits"
    service.summary = "Wir prüfen Websites."
    service.save()
    assert Service.objects.language("de").get(pk=service.pk).title == "SEO-Audits"
    assert Service.objects.language("en").get(pk=service.pk).title == "SEO Audits"


# --------------------------------------------------------------------------- #
# Public page + JSON-LD
# --------------------------------------------------------------------------- #
def test_service_detail_renders_citable_content(client, service):
    html = client.get(service.get_absolute_url()).content.decode()
    assert "We audit websites" in html  # summary lead sentence
    assert "From $499" in html
    assert "Worldwide" in html
    assert "How long does it take?" in html
    assert "About two weeks." in html


def test_service_emits_service_and_faqpage_jsonld(client, service):
    nodes = _ld_nodes(client.get(service.get_absolute_url()).content.decode())
    types = {n.get("@type") for n in nodes}
    assert {"Service", "FAQPage", "BreadcrumbList", "Organization", "WebSite"} <= types

    svc = next(n for n in nodes if n["@type"] == "Service")
    assert svc["name"] == "SEO Audits"
    assert svc["areaServed"] == "Worldwide"
    assert svc["provider"]["@type"] == "Organization"
    # Freeform price is not emitted as a schema.org Offer (would be invalid).
    assert "offers" not in svc

    faq = next(n for n in nodes if n["@type"] == "FAQPage")
    assert len(faq["mainEntity"]) == 2
    q0 = faq["mainEntity"][0]
    assert q0["@type"] == "Question"
    assert q0["acceptedAnswer"]["text"] == "About two weeks."


def test_draft_service_hidden_from_anonymous(client, author):
    draft = Service.objects.create(title="Secret Service", author=author)
    assert client.get(draft.get_absolute_url()).status_code == 404


def test_service_in_sitemap_and_llms(client, service):
    xml = client.get("/sitemap.xml").content.decode()
    assert f"/services/{service.slug}/" in xml
    llms = client.get("/llms.txt").content.decode()
    assert "## Services" in llms
    assert "SEO Audits" in llms


# --------------------------------------------------------------------------- #
# Dashboard CRUD
# --------------------------------------------------------------------------- #
def test_editor_creates_and_translates_service(client, django_user_model):
    from django.contrib.auth.models import Group

    editor = django_user_model.objects.create_user(username="ed", password="pw")
    editor.groups.add(Group.objects.get(name="Editor"))
    client.force_login(editor)

    resp = client.post(
        reverse("dashboard:service_create"),
        {
            "title": "Consulting",
            "summary": "Expert help.",
            "description": "<p>Details.</p>",
            "price": "€90/hour",
            "area_served": "EU",
            "faq": "Q: Remote?\nA: Yes.",
            "status": "published",
        },
    )
    assert resp.status_code == 302
    svc = Service.objects.get(slug="consulting")
    assert svc.price == "€90/hour"

    # Add a German translation via ?language=de.
    edit = reverse("dashboard:service_edit", args=[svc.pk]) + "?language=de"
    client.post(
        edit,
        {
            "title": "Beratung",
            "summary": "Hilfe.",
            "description": "<p>x</p>",
            "status": "published",
        },
    )
    assert Service.objects.language("de").get(pk=svc.pk).title == "Beratung"

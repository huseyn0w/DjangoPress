from __future__ import annotations

from django import forms
from django.conf import settings
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3

from .models import Comment, CommentStatus


def recaptcha_enabled() -> bool:
    """True only when both reCAPTCHA keys are configured.

    Read live from settings (not cached at import) so tests and per-environment
    config toggle it; when False the captcha field is omitted entirely and the
    comment flow stays frictionless.
    """
    return bool(
        getattr(settings, "RECAPTCHA_PUBLIC_KEY", "")
        and getattr(settings, "RECAPTCHA_PRIVATE_KEY", "")
    )


class CommentForm(forms.ModelForm):
    # Threading: the post template sets this from a "Reply" affordance. The queryset
    # is scoped per-request (see __init__) so a parent must be an APPROVED comment on
    # the SAME post — that enforces both checks at validation time.
    parent = forms.ModelChoiceField(
        queryset=Comment.objects.none(), required=False, widget=forms.HiddenInput
    )

    class Meta:
        model = Comment
        fields = ["name", "email", "body", "parent"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 4, "placeholder": "Join the discussion…"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        # Only approved comments on this post are valid reply targets. When the form
        # has no post yet (unbound render) the queryset stays empty, which is safe.
        post = getattr(self.instance, "post", None)
        if post is not None and post.pk:
            self.fields["parent"].queryset = Comment.objects.filter(
                post=post, status=CommentStatus.APPROVED
            )
        if user is not None and user.is_authenticated:
            # Identity comes from the account; don't ask for name/email.
            self.fields.pop("name")
            self.fields.pop("email")
        if recaptcha_enabled():
            # v3 is invisible: it scores the request in the background, no checkbox.
            self.fields["captcha"] = ReCaptchaField(widget=ReCaptchaV3())

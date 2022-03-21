from django.apps import apps

from admin.templates.utils import MODELS
from admin.sequences.forms import PendingAdminTaskForm, PendingSlackMessageForm, PendingTextMessageForm, PendingEmailMessageForm, AccountProvisionForm

# These are models specific to sequences. They don't have templates.
SEQUENCE_MODELS = [
    {"app": "sequences", "model": "PendingTextMessage", "form": PendingTextMessageForm},
    {"app": "sequences", "model": "PendingEmailMessage", "form": PendingEmailMessageForm},
    {"app": "sequences", "model": "PendingSlackMessage", "form": PendingSlackMessageForm},
    {"app": "sequences", "model": "PendingAdminTask", "form": PendingAdminTaskForm},
    {"app": "sequences", "model": "AccountProvision", "form": AccountProvisionForm},
]

SEQUENCE_MODELS += MODELS

def template_model_exists(template_slug):
    return any([x["model"].lower() == template_slug.lower() for x in SEQUENCE_MODELS])


def get_sequence_templates_model(template_slug):
    if template_model_exists(template_slug):
        model_item = next(
            (x for x in SEQUENCE_MODELS if x["model"].lower() == template_slug.lower()), None
        )
        return apps.get_model(model_item["app"], model_item["model"])


def get_user_field(template_slug):
    if template_model_exists(template_slug):
        return next(
            (
                x["user_field"]
                for x in SEQUENCE_MODELS
                if x["model"].lower() == template_slug.lower()
            ),
            None,
        )


def get_model_item(template_slug):
    model_item = None
    if template_model_exists(template_slug):
        model_item = next(
            (x for x in SEQUENCE_MODELS if x["model"].lower() == template_slug.lower()), None
        )
    return model_item


def get_sequence_model_form(template_slug):
    model = get_model_item(template_slug)

    if model is None:
        return None

    return get_model_item(template_slug)["form"]

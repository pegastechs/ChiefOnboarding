import json

import requests
from crispy_forms.helper import FormHelper
from django import forms
from django.core.exceptions import ValidationError

from .models import Integration
from .serializers import ManifestSerializer


class IntegrationConfigForm(forms.ModelForm):
    def _get_result(self, notation, value):
        # if we don't need to go into props, then just return the value
        if notation == "":
            return value

        notations = notation.split(".")
        for notation in notations:
            value = value[notation]
        return value

    def _expected_example(self, form_item):
        def _add_items(form_item):
            items = []
            # Add two example items
            for item in range(2):
                items.append(
                    {
                        form_item.get("choice_value", "id"): item,
                        form_item.get("choice_name", "name"): f"name {item}",
                    }
                )
            return items

        inner = form_item.get("data_from", "")
        if inner == "":
            return _add_items(form_item)

        # This is pretty ugly, but we are building a json string first
        # and then convert it to a real json object to avoid nested loops
        notations = inner.split(".")
        stringified_json = "{"
        for idx, notation in enumerate(notations):
            if idx + 1 == len(notations):
                stringified_json += f'"{notation}":'
                stringified_json += json.dumps(_add_items(form_item))
                stringified_json += "}" * len(notations)

        return json.loads(stringified_json)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        integration = Integration.objects.get(id=self.instance.id)
        form = self.instance.manifest["form"]
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.error = None
        for item in form:
            if item["type"] == "input":
                self.fields[item["id"]] = forms.TextField(
                    label=item["name"],
                    required=False,
                )

            if item["type"] in ["choice", "multiple_choice"]:

                # If there is a url to fetch the items from then do so
                if "url" in item:
                    try:
                        option_data = requests.get(
                            integration._replace_vars(item["url"]),
                            headers=integration._headers,
                        ).json()
                    except Exception as e:
                        self.error = (
                            f"The request to ({item['url']}) of the requests could "
                            "not be completed. Here is the full error: <br/> " + str(e)
                        )
                        break
                else:
                    # No url, so get the static items
                    option_data = item["items"]

                # Can we select one or multiple?
                if item["type"] == "choice":
                    field = forms.ChoiceField
                else:
                    field = forms.MultipleChoiceField

                try:
                    self.fields[item["id"]] = field(
                        label=item["name"],
                        widget=forms.CheckboxSelectMultiple
                        if item["type"] == "multiple_choice"
                        else forms.Select,
                        choices=[
                            (
                                self._get_result(item.get("choice_value", "id"), x),
                                self._get_result(item.get("choice_name", "name"), x),
                            )
                            for x in self._get_result(
                                item.get("data_from", ""), option_data
                            )
                        ],
                        required=False,
                    )
                except Exception:
                    expected = self._expected_example(item)

                    self.error = (
                        f"Form item ({item['name']}) could not be rendered. Format "
                        "was different than expected.<br><h2>Expected format:"
                        f"</h2><pre>{json.dumps(expected, indent=4)}</pre><br><h2>"
                        "Got from server:</h2><pre>"
                        f"{json.dumps(option_data, indent=4)}</pre>"
                    )
                    break

    class Meta:
        model = Integration
        fields = ()


# Credits: https://stackoverflow.com/a/72256767
# Removed the sort options
class PrettyJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, indent, **kwargs):
        super().__init__(*args, indent=4, **kwargs)


class IntegrationForm(forms.ModelForm):
    manifest = forms.JSONField(encoder=PrettyJSONEncoder)

    class Meta:
        model = Integration
        fields = ("name", "manifest")

    def clean_manifest(self):
        manifest = self.cleaned_data["manifest"]
        manifest_serializer = ManifestSerializer(data=manifest)
        if not manifest_serializer.is_valid():
            raise ValidationError(json.dumps(manifest_serializer.errors))
        return manifest


class IntegrationExtraArgsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial_data = self.instance.extra_args
        for item in self.instance.manifest["initial_data_form"]:
            self.fields[item["id"]] = forms.CharField(
                label=item["name"], help_text=item["description"]
            )
            # Check if item was already saved - load data back in form
            if item["id"] in initial_data:
                self.fields[item["id"]].initial = initial_data[item["id"]]
            # If field is secret field, then hide it - values are generated on the fly
            if "type" in item and item["type"] == "generated":
                self.fields[item["id"]].widget = forms.HiddenInput()

    def save(self):
        integration = self.instance
        integration.extra_args = self.cleaned_data
        integration.save()
        return integration

    class Meta:
        model = Integration
        fields = ()

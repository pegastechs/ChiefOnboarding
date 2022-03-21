from django import forms
from django.utils.translation import gettext_lazy as _

from users.models import User

from .models import AdminTask, AdminTaskComment


class AdminTaskCommentForm(forms.ModelForm):
    class Meta:
        model = AdminTaskComment
        fields = [
            "content",
        ]


class AdminTaskUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, "instance", None)
        if instance is not None and instance.completed:
            for field in self.fields:
                self.fields[field].widget.attrs["disabled"] = True

    class Meta:
        model = AdminTask
        fields = ["name", "assigned_to", "date", "priority"]


class AdminTaskCreateForm(forms.ModelForm):
    comment = forms.CharField(max_length=12500)
    new_hire = forms.ModelChoiceField(queryset=User.new_hires.all())
    assigned_to = forms.ModelChoiceField(queryset=User.admins.all())
    slack_user = forms.ModelChoiceField(
        queryset=User.objects.exclude(slack_user_id=""), to_field_name="slack_user_id"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["option"].initial = 0
        self.fields["slack_user"].required = False

    class Meta:
        model = AdminTask
        fields = [
            "name",
            "new_hire",
            "assigned_to",
            "date",
            "priority",
            "comment",
            "option",
            "slack_user",
            "email",
        ]

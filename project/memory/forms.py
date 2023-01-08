from django.forms import ModelForm, HiddenInput, CharField
from .models import Memory

default_location = "[56.838095,60.603567]"


class MemoryForm(ModelForm):
    """
    Form model for Memory model.
    Include all fields.

    Overrides widgets of user and location fields to HiddenInput
    """
    class Meta:
        model = Memory
        fields = "__all__"
        widgets = {
            "user": HiddenInput,
            "location": HiddenInput(attrs={
                "value": default_location
            })
        }

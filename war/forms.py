from django import forms
from .models import Riddle, Survivor, RiddleSolution, War, asm_max, bin_max
from django.utils.translation import gettext_lazy as _

class SurvivorSubmissionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        amount_of_survivors = kwargs.pop('war').amount_of_survivors
        super(SurvivorSubmissionForm, self).__init__(*args, **kwargs)

        for i in range(1, amount_of_survivors + 1):
            self.fields[f'asm_{i}'] = forms.FileField(
                label=_("Assembly source file: "), validators=[asm_max])
            self.fields[f'asm_{i}'].group = i
            self.fields[f'bin_{i}'] = forms.FileField(
                label=_("Binary file: "), validators=[bin_max])
            self.fields[f'bin_{i}'].group = i


class RiddleSubmissionForm(forms.ModelForm):
    class Meta:
        model = RiddleSolution
        fields = ('riddle_solution', )

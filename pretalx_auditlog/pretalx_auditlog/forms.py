from django import forms


class Search(forms.Form):
    def __init__(self, *args, model_names=[], **kwargs):
        self.model_names = [("All", "All")] + [
            (x, x.removesuffix("ProxyEvent").removeprefix("pretalx_auditlog."))
            for x in model_names
        ]
        super().__init__(*args, **kwargs)
        print(self.model_names)
        self.fields["model"].widget = forms.Select(choices=self.model_names)

    n = forms.IntegerField(help_text="number of items to show")
    max_date = forms.DateTimeField(
        help_text="max date, default=NOW",
        required=False,
        widget=forms.DateInput(attrs={"class": "datetimepickerfield"}),
    )
    model = forms.CharField(help_text="model")

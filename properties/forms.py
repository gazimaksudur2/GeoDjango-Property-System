import re
from django import forms


class PropertySearchForm(forms.Form):
    location = forms.CharField(
        required=False,
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "id": "location-search",
                "autocomplete": "off",
                "placeholder": "Search location or vibe e.g."
                + " Gulshan, luxury apartment",
                "class": "w-full border rounded-lg px-4 py-3"
                + " focus:ring-2 focus:ring-blue-400",
            }
        ),
    )
    radius = forms.FloatField(
        required=False,
        initial=10.0,
        min_value=0.5,
        max_value=100.0,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Radius (km)",
                "step": "0.5",
                "class": "w-full md:w-36 border rounded-lg px-4 py-3"
                + " focus:ring-2 focus:ring-blue-400",
            }
        ),
    )
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        max_digits=14,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Min Price",
                "class": "w-full border rounded-lg px-4 py-2 focus:ring-2"
                + " focus:ring-blue-400",
            }
        ),
    )
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        max_digits=14,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Max Price",
                "class": "w-full border rounded-lg px-4 py-2 focus:ring-2"
                + " focus:ring-blue-400",
            }
        ),
    )
    bedrooms = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=20,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Min Beds",
                "class": "w-full border rounded-lg px-4 py-2"
                + " focus:ring-2 focus:ring-blue-400",
            }
        ),
    )

    def clean_location(self):
        location = self.cleaned_data.get("location", "")
        if location:
            location = location.strip()
            if len(location) < 2:
                raise forms.ValidationError(
                    "Location query must be at least 2 characters long."
                )
            if not re.match(r"^[a-zA-Z0-9\s,\-\.]+$", location):
                raise forms.ValidationError(
                    "Location contains invalid special characters."
                )
        return location

    def clean_radius(self):
        radius = self.cleaned_data.get("radius")
        if radius is None:
            return 10.0
        if radius <= 0 or radius > 100:
            raise forms.ValidationError(
                "Search radius must be between 0.5 km and 100 km."
            )
        return radius

    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get("min_price")
        max_price = cleaned_data.get("max_price")

        if min_price is not None and max_price is not None:
            if min_price > max_price:
                raise forms.ValidationError(
                    "Minimum price cannot be greater than maximum price."
                )
        return cleaned_data
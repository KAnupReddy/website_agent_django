from django import forms

from .models import Business

BUSINESS_TYPES = [
    'Restaurant / Cafe',
    'Hotel / Hospitality',
    'Medical / Healthcare',
    'Legal / Law Firm',
    'Salon / Spa & Beauty',
    'Gym / Fitness Studio',
    'Real Estate Agency',
    'Retail / Shop',
    'Education / Training',
    'Consulting / Agency',
    'Other',
]


class BusinessForm(forms.ModelForm):
    """Manual onboarding form (same rules as the CI4 `Dashboard::store` validation)."""

    business_type = forms.ChoiceField(choices=[(t, t) for t in BUSINESS_TYPES])
    review_count = forms.IntegerField(min_value=0, required=False)
    rating = forms.DecimalField(min_value=0, max_value=5, max_digits=3, decimal_places=1, required=False)

    class Meta:
        model = Business
        fields = [
            'name', 'business_type', 'category', 'website_status', 'website_url',
            'location', 'address', 'phone', 'email', 'rating', 'review_count',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].min_length = 2
        self.fields['location'].min_length = 2
        self.fields['website_status'].initial = Business.WebsiteStatus.NO_WEBSITE
        self.fields['website_status'].required = False

    def clean_name(self):
        return self._min2('name')

    def clean_location(self):
        return self._min2('location')

    def _min2(self, field):
        value = (self.cleaned_data.get(field) or '').strip()
        if len(value) < 2:
            raise forms.ValidationError('Must be at least 2 characters.')
        return value

    def clean_website_status(self):
        return self.cleaned_data.get('website_status') or Business.WebsiteStatus.NO_WEBSITE

    def clean_review_count(self):
        return self.cleaned_data.get('review_count') or 0

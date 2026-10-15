# properties/tests.py
from django.contrib.gis.geos import Point
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .forms import PropertySearchForm
from .models import Location, Property


class GeoPropertySystemTests(TestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.dummy_vector = [0.01] * 384

        self.location = Location.objects.create(
            name="Gulshan",
            slug="gulshan",
            country="Bangladesh",
            state="Dhaka",
            city="Dhaka",
            point=Point(90.4125, 23.7925, srid=4326),
            embedding=self.dummy_vector,
            is_active=True,
        )

        self.property = Property.objects.create(
            location=self.location,
            title="Luxury Gulshan Apartment",
            slug="luxury-gulshan-apartment",
            description="Spacious modern apartment with rooftop garden.",
            property_type="Apartment",
            status="For Rent",
            price=85000.00,
            bedrooms=3,
            bathrooms=3,
            area_sqft=2200.00,
            point=Point(90.4150, 23.7940, srid=4326),
            embedding=self.dummy_vector,
            is_active=True,
        )

    def test_search_form_validation(self):
        invalid_form = PropertySearchForm(
            data={
                "search_type": "location",
                "location": "a",
                "min_price": 1000,
                "max_price": 500,
            }
        )
        self.assertFalse(invalid_form.is_valid())
        self.assertIn("location", invalid_form.errors)

    def test_nearby_api_endpoint(self):
        url = reverse("property-nearby")
        response = self.client_api.get(
            url, {"lng": 90.4125, "lat": 23.7925, "radius": 5}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_location_autocomplete_api_endpoint(self):
        url = reverse("location-autocomplete")
        response = self.client_api.get(url, {"q": "Gul"})
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Gulshan")

    def test_property_autocomplete_api_endpoint(self):
        url = reverse("property-autocomplete")
        response = self.client_api.get(url, {"q": "Luxury"})
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Luxury Gulshan Apartment")

    def test_property_list_view_location_mode(self):
        url = reverse("property_list")
        response = self.client.get(
            url,
            {"search_type": "location", "location": "Gulshan", "radius": 10},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["search_type"], "location")
        self.assertEqual(response.context["matched_location"], self.location)
        self.assertIn(self.property, list(response.context["page_obj"]))

    def test_property_list_view_property_mode(self):
        url = reverse("property_list")
        response = self.client.get(
            url,
            {
                "search_type": "property",
                "location": "Luxury Gulshan",
                "target_id": self.property.id,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["search_type"], "property")
        self.assertIn(self.property, list(response.context["page_obj"]))
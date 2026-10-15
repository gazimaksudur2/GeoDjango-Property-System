import pandas as pd

from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.db import transaction

from properties.models import Location


class Command(BaseCommand):

    help = "Import locations from CSV"

    def clean(self, value):
        """
        Convert pandas NaN to empty string
        """
        if pd.isna(value):
            return ""

        return value

    @transaction.atomic
    def handle(self, *args, **kwargs):

        self.stdout.write(
            "Starting location import..."
        )

        locations = pd.read_csv(
            "data/locations.csv"
        )

        created = 0
        updated = 0

        for _, row in locations.iterrows():
            location, is_created = Location.objects.update_or_create(
                id=int(row["location_id"]),
                defaults={
                    "slug": self.clean(row["slug"]),
                    "name": self.clean(row["name"]),
                    "country": self.clean(row["country"]),
                    "state": self.clean(row["state"]),
                    "city": self.clean(row["city"]),
                    "address": self.clean(row["address"]),
                    "point": Point(
                        float(row["longitude"]),
                        float(row["latitude"]),
                        srid=4326,
                    ),
                    "is_active": bool(row["is_active"]),
                },
            )
            
        self.stdout.write(
            self.style.SUCCESS(
                f"""
Locations import completed.

Created: {created}
Updated: {updated}
"""
            )
        )

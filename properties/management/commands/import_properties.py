import pandas as pd

from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.db import transaction

from properties.models import (
    Location,
    Property,
)


class Command(BaseCommand):

    help = "Import properties from CSV"

    def clean(self, value):

        if pd.isna(value):
            return ""

        return value

    @transaction.atomic
    def handle(self, *args, **kwargs):

        self.stdout.write(
            "Starting property import..."
        )
        properties = pd.read_csv(
            "data/properties.csv"
        )
        created = 0
        updated = 0
        for _, row in properties.iterrows():
            location = Location.objects.get(
                id=row["location_id"]
            )
            property_obj, is_created = Property.objects.update_or_create(
                id=row["property_id"],
                defaults={
                    "location": location,
                    "title": self.clean(
                        row["title"]
                    ),
                    "slug": self.clean(
                        row["slug"]
                    ),
                    "description": self.clean(
                        row["description"]
                    ),
                    "property_type": self.clean(
                        row["property_type"]
                    ),
                    "status": self.clean(
                        row["status"]
                    ),
                    "price": row["price"],
                    "bedrooms": row["bedrooms"],
                    "bathrooms": row["bathrooms"],
                    "area_sqft": row["area_sqft"],
                    "address": self.clean(
                        row["address"]
                    ),
                    "point": Point(

                        float(
                            row["longitude"]
                        ),

                        float(
                            row["latitude"]
                        ),

                        srid=4326

                    ),
                    "is_featured": bool(
                        row["is_featured"]
                    ),
                    "is_active": bool(
                        row["is_active"]
                    ),

                }
            )

            if is_created:
                created += 1
            else:
                updated += 1

            self.stdout.write(f"Imported property: {property_obj.title}")

        self.stdout.write(
            self.style.SUCCESS(
                "Properties import completed. Created"
                + f": {created}, Updated: {updated}"
            )
        )

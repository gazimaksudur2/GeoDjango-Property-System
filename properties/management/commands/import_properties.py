import pandas as pd

from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point

from properties.models import (
    Location,
    Property,
    PropertyImage,
)


class Command(BaseCommand):

    help = "Import property data from CSV files"

    def handle(self, *args, **kwargs):

        self.stdout.write("Starting import...")
        locations = pd.read_csv(
            "data/locations.csv"
        )

        for _, row in locations.iterrows():

            Location.objects.update_or_create(
                id=row["location_id"],
                defaults={
                    "name": row["name"],
                    "slug": row["slug"],
                    "country": row["country"],
                    "state": row["state"],
                    "city": row["city"],
                    "address": row["address"],

                    "point": Point(
                        row["longitude"],
                        row["latitude"],
                        srid=4326
                    ),

                    "is_active": row["is_active"],
                }
            )

        self.stdout.write(
            "Locations imported successfully"
        )

        properties = pd.read_csv(
            "data/properties.csv"
        )

        for _, row in properties.iterrows():

            location = Location.objects.get(
                id=row["location_id"]
            )

            Property.objects.update_or_create(
                id=row["property_id"],
                defaults={

                    "location": location,

                    "title": row["title"],

                    "slug": row["slug"],

                    "description": row["description"],

                    "property_type": row["property_type"],

                    "status": row["status"],

                    "price": row["price"],

                    "bedrooms": row["bedrooms"],

                    "bathrooms": row["bathrooms"],

                    "area_sqft": row["area_sqft"],

                    "address": row["address"],

                    "point": Point(
                        row["longitude"],
                        row["latitude"],
                        srid=4326
                    ),

                    "is_featured": row["is_featured"],

                    "is_active": row["is_active"],
                }
            )

        self.stdout.write(
            "Properties imported successfully"
        )

        images = pd.read_csv(
            "data/property_images.csv"
        )

        for _, row in images.iterrows():

            property_obj = Property.objects.get(
                id=row["property_id"]
            )

            PropertyImage.objects.update_or_create(
                id=row["image_id"],
                defaults={

                    "property": property_obj,

                    "image": row["image_path"],

                    "alt_text": row["alt_text"],

                    "caption": row["caption"],

                    "is_primary": row["is_primary"],

                    "sort_order": row["sort_order"],
                }
            )

        self.stdout.write(
            self.style.SUCCESS(
                "All data imported successfully!"
            )
        )
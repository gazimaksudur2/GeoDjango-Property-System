import urllib.request
from pathlib import Path

import pandas as pd
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from properties.models import Property, PropertyImage


UNSPLASH_PROPERTY_IMAGES = [
    "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1613490493576-7fde63acd811?auto=format&fit=crop&w=1000&q=80",
]


class Command(BaseCommand):
    help = "Import property images from CSV using Unsplash photos"

    def clean(self, value, default=""):
        if pd.isna(value):
            return default
        return value

    def fetch_image_bytes(self, url, cache):
        if url not in cache:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                cache[url] = response.read()
        return cache[url]

    @transaction.atomic
    def handle(self, *args, **kwargs):
        csv_path = Path("data/property_images.csv")
        if not csv_path.exists():
            self.stderr.write(
                self.style.ERROR("data/property_images.csv not found.")
            )
            return

        self.stdout.write("Starting property image import...")
        df = pd.read_csv(csv_path)

        if "property_id" not in df.columns:
            self.stderr.write(
                self.style.ERROR("Column 'property_id' not found in CSV.")
            )
            return

        df = df.dropna(subset=["property_id"])
        image_cache = {}
        created_count = 0

        for idx, row in df.iterrows():
            property_id = int(row["property_id"])
            property_obj = Property.objects.filter(id=property_id).first()

            if not property_obj:
                self.stdout.write(
                    f"Property with ID {property_id} not found in database. Skipping."
                )
                continue

            image_url = UNSPLASH_PROPERTY_IMAGES[
                idx % len(UNSPLASH_PROPERTY_IMAGES)
            ]

            try:
                image_bytes = self.fetch_image_bytes(image_url, image_cache)
            except Exception as exc:
                self.stderr.write(
                    f"Failed to download image for property {property_id}: {exc}"
                )
                continue

            sort_order = int(self.clean(row.get("sort_order", idx % 3), idx % 3))
            is_primary_val = row.get("is_primary", sort_order == 1)
            if isinstance(is_primary_val, str):
                is_primary = is_primary_val.strip().lower() == "true"
            else:
                is_primary = bool(is_primary_val)

            alt_text = str(
                self.clean(
                    row.get("alt_text", property_obj.title),
                    property_obj.title,
                )
            )
            caption = str(self.clean(row.get("caption", ""), ""))

            image_record, _ = PropertyImage.objects.update_or_create(
                property=property_obj,
                sort_order=sort_order,
                defaults={
                    "alt_text": alt_text,
                    "caption": caption,
                    "is_primary": is_primary,
                },
            )

            filename = f"property_{property_obj.id}_{sort_order}.jpg"
            image_record.image.save(
                filename,
                ContentFile(image_bytes),
                save=True,
            )

            created_count += 1
            self.stdout.write(
                f"Saved image for Property #{property_obj.id}: {property_obj.title}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Property images import completed. Total processed: {created_count}"
            )
        )
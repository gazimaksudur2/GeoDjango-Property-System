from django.core.management.base import BaseCommand
from properties.models import Location
from properties.utils.embeddings import generate_embedding


class Command(BaseCommand):
    help = "Generate embeddings for location names"

    def handle(self, *args, **kwargs):
        locations = Location.objects.all()

        for location in locations:
            text = (
                f"{location.name}, "
                f"{location.city}, "
                f"{location.state}, "
                f"{location.country}"
            )

            location.embedding = generate_embedding(
                text
            )

            location.save(
                update_fields=[
                    "embedding"
                ]
            )

            self.stdout.write(
                f"Updated location {location.id}: {location.name}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Location embeddings generated successfully"
            )
        )

from django.core.management.base import BaseCommand
from properties.models import Location
from properties.utils.embeddings import generate_embedding


class Command(BaseCommand):
    help = "Generate embeddings for location names"

    def handle(self, *args, **kwargs):
        locations = Location.objects.filter(
            embedding__isnull=True
        )

        for location in locations:
            text = f"""
                Location Name:
                {location.name}

                Address:
                {location.address}

                City:
                {location.city}

                State:
                {location.state}

                Country:
                {location.country}

                Geographic Area:
                {location.name} is a neighborhood located in {location.city}, 
                {location.state}, {location.country}.

                Real Estate Profile:
                {location.name} is a real estate area containing residential
                apartments, luxury homes, commercial properties, offices,
                shopping areas, restaurants,
                schools, and nearby community facilities.

                Property Search Context:
                People looking for properties near {location.name},
                apartments in {location.name},
                houses for sale in {location.city},
                homes for rent in {location.city},
                and real estate opportunities in {location.city}
                may find properties in this area relevant.

                Location Keywords:
                {location.name},
                {location.city} properties,
                {location.city} real estate,
                residential area,
                commercial area,
                property investment,
                housing neighborhood
                """
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

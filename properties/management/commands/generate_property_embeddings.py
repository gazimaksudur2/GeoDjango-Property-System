from django.core.management.base import BaseCommand
from properties.models import Property
from properties.utils.embeddings import generate_embedding


class Command(BaseCommand):
    help = "Generate property embeddings"

    def handle(self, *args, **kwargs):
        properties = Property.objects.filter(
            embedding__isnull=True
        )

        for property_obj in properties:

            text = f"""
                Property:
                {property_obj.title}

                Description:
                {property_obj.description}

                Property Type:
                {property_obj.property_type}

                Status:
                {property_obj.status}

                Bedrooms:
                {property_obj.bedrooms}

                Bathrooms:
                {property_obj.bathrooms}

                Area:
                {property_obj.area_sqft} sqft

                Address:
                {property_obj.address}

                Location:
                {property_obj.location.name},
                {property_obj.location.city},
                {property_obj.location.state},
                {property_obj.location.country}

                Nearby Area:
                {property_obj.location.name} residential 
                and commercial real estate area
                """
            property_obj.embedding = generate_embedding(
                text
            )

            property_obj.save(
                update_fields=[
                    "embedding"
                ]
            )

            self.stdout.write(
                f"Updated {property_obj.id}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Embeddings generated"
            )
        )

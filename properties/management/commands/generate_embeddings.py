from django.core.management.base import BaseCommand
from properties.models import Property
from properties.utils.embeddings import generate_embedding


class Command(BaseCommand):
    help = "Generate property embeddings"

    def handle(self, *args, **kwargs):
        properties = Property.objects.all()
        for property_obj in properties:

            text = f"""
            {property_obj.title}

            {property_obj.description}

            Type:
            {property_obj.property_type}

            Location:
            {property_obj.address}
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

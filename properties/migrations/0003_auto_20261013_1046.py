from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("properties", "0002_alter_location_address_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE properties_property
                ALTER COLUMN embedding TYPE vector(384);

                ALTER TABLE properties_location
                ALTER COLUMN embedding TYPE vector(384);
            """,
            reverse_sql="""
                ALTER TABLE properties_property
                ALTER COLUMN embedding TYPE vector(1536);

                ALTER TABLE properties_location
                ALTER COLUMN embedding TYPE vector(1536);
            """
        ),
    ]
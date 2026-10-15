from django.db import migrations, models
import pgvector.django.indexes


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='address',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddIndex(
            model_name='location',
            index=pgvector.django.indexes.HnswIndex(ef_construction=64, fields=['embedding'], m=16, name='location_embedding_idx', opclasses=['vector_cosine_ops']),
        ),
        migrations.AddIndex(
            model_name='property',
            index=pgvector.django.indexes.HnswIndex(ef_construction=64, fields=['embedding'], m=16, name='property_embedding_idx', opclasses=['vector_cosine_ops']),
        ),
        migrations.AddIndex(
            model_name='propertyimage',
            index=pgvector.django.indexes.HnswIndex(ef_construction=64, fields=['embedding'], m=16, name='image_embedding_idx', opclasses=['vector_cosine_ops']),
        ),
    ]

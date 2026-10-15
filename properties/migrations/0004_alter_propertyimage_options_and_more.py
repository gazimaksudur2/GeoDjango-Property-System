from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0003_auto_20261013_1046'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='propertyimage',
            options={'ordering': ['sort_order', 'created_at']},
        ),
        migrations.RemoveIndex(
            model_name='propertyimage',
            name='image_embedding_idx',
        ),
        migrations.RemoveField(
            model_name='propertyimage',
            name='embedding',
        ),
    ]

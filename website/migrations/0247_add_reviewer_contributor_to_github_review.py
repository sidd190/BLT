# Generated migration for adding reviewer_contributor field to GitHubReview

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0246_add_user_progress_models"),
    ]

    operations = [
        # Make reviewer nullable
        migrations.AlterField(
            model_name="githubreview",
            name="reviewer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reviews_made",
                to="website.userprofile",
            ),
        ),
        # Add reviewer_contributor field
        migrations.AddField(
            model_name="githubreview",
            name="reviewer_contributor",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reviews_made",
                to="website.contributor",
            ),
        ),
    ]

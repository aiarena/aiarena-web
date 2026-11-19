import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0088_awardset_competition_awards_given_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="competition",
            name="scheduling_weight",
            field=models.PositiveIntegerField(
                blank=True,
                default=100,
                help_text=(
                    "New ladder matches are shared between competitions in proportion to active participants times "
                    "this weight, so 100 is normal and 50 halves this competition's share. Weights count matches, "
                    "not how long they take."
                ),
                null=True,
                validators=[django.core.validators.MinValueValidator(1)],
            ),
        ),
    ]

from django.core.validators import MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0088_awardset_competition_awards_given_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="competition",
            name="arena_client_limit",
            field=models.PositiveIntegerField(
                blank=True,
                help_text=(
                    "Blank means every eligible client. A number is how many clients are preferred, in "
                    "first-claim order, while they have other matches to play. A client with nothing else to "
                    "play may still take a match."
                ),
                null=True,
                validators=[MinValueValidator(1)],
            ),
        ),
    ]

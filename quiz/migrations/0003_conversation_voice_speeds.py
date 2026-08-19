from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("quiz", "0002_rename_actors")]

    operations = [
        migrations.AddField(
            model_name="conversation",
            name="man_speed",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("1.00"),
                help_text="1.00 = normal; nilai lebih besar membuat suara lebih cepat.",
                max_digits=3,
                validators=[
                    MinValueValidator(Decimal("0.75")),
                    MaxValueValidator(Decimal("1.40")),
                ],
            ),
        ),
        migrations.AddField(
            model_name="conversation",
            name="woman_speed",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("1.10"),
                help_text="1.00 = normal; nilai lebih besar membuat suara lebih cepat.",
                max_digits=3,
                validators=[
                    MinValueValidator(Decimal("0.75")),
                    MaxValueValidator(Decimal("1.40")),
                ],
            ),
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='appointment',
            constraint=models.CheckConstraint(
                condition=models.Q(("duration_minutes__gt", 0)),
                name="agenda_positive_duration",
            ),
        ),
    ]

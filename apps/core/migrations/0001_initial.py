from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="RequestCounter",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("prefix", models.CharField(max_length=16, unique=True)),
                ("last_value", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Счетчик номеров заявок",
                "verbose_name_plural": "Счетчики номеров заявок",
            },
        ),
    ]

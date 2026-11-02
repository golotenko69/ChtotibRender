from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.RenameIndex(
            model_name="product",
            new_name="products_pr_is_acti_2fee29_idx",
            old_name="products_pr_is_acti_2f0a4e_idx",
        ),
    ]

# Generated migration for dietary plans
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DietaryPlan',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('dietary_type', models.CharField(choices=[
                    ('ulcer', 'Ulcer Diet'),
                    ('diabetic', 'Diabetic Diet'),
                    ('vegetarian', 'Vegetarian'),
                    ('vegan', 'Vegan'),
                    ('halal', 'Halal'),
                    ('gluten_free', 'Gluten Free'),
                    ('low_sodium', 'Low Sodium'),
                    ('renal', 'Renal Diet'),
                    ('heart_healthy', 'Heart Healthy'),
                    ('pregnancy', 'Pregnancy Diet'),
                    ('other', 'Other Special Diet'),
                ], max_length=30)),
                ('description', models.TextField(blank=True, null=True)),
                ('foods_to_avoid', models.TextField(blank=True, help_text='List of foods to avoid (comma separated)', null=True)),
                ('recommended_foods', models.TextField(blank=True, help_text='List of recommended foods (comma separated)', null=True)),
                ('additional_price', models.DecimalField(decimal_places=2, default=0, help_text='Additional cost per month for this dietary plan', max_digits=10)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'dietary_plans',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='subscription',
            name='dietary_plan',
            field=models.ForeignKey(blank=True, help_text='Special dietary requirements for this subscription', null=True, on_delete=models.SET_NULL, related_name='subscriptions', to='subscriptions.dietaryplan'),
        ),
    ]

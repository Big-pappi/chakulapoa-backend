"""
Management command to set up initial data for Chakula Poa.
Creates super admin, restaurants (all location types), and subscription plans.

This platform serves ALL populated areas in Tanzania:
- Universities
- Markets
- Offices/Workplaces
- Hospitals
- Industrial areas
- General restaurants
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import User
from restaurants.models import Restaurant, LocationType
from universities.models import University
from subscriptions.models import SubscriptionPlan, DietaryPlan


class Command(BaseCommand):
    help = 'Set up initial data for Chakula Poa - Multi-location meal subscription platform'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data for Chakula Poa...\n')
        self.stdout.write('=' * 60 + '\n')
        
        with transaction.atomic():
            # Create Super Admin
            self.create_super_admin()
            
            # Create Restaurants (all location types)
            self.create_restaurants()
            
            # Create Legacy Universities (for backwards compatibility)
            self.create_universities()
            
            # Create Dietary Plans
            self.create_dietary_plans()
            
            # Create Subscription Plans
            self.create_subscription_plans()
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('\nInitial setup completed successfully!'))
        self.stdout.write('\nYou can now:')
        self.stdout.write('  1. Run the server: python manage.py runserver')
        self.stdout.write('  2. Access admin: http://127.0.0.1:8000/admin/')
        self.stdout.write('  3. API endpoints: http://127.0.0.1:8000/api/')

    def create_super_admin(self):
        """Create the super admin user."""
        self.stdout.write('\n[1/4] Creating Super Admin...')
        
        email = 'chedybreezy@gmail.com'
        phone_number = '0712000001'
        
        if User.objects.filter(email=email).exists():
            self.stdout.write(f'  Super admin with email {email} already exists.')
            return
        
        if User.objects.filter(phone_number=phone_number).exists():
            phone_number = '0700000001'
        
        user = User.objects.create_superuser(
            phone_number=phone_number,
            password='Amaruwebster093@',
            full_name='Chedy',
            email=email,
            role='super_admin'
        )
        
        self.stdout.write(self.style.SUCCESS(
            f'  Created super admin:\n'
            f'    Name: {user.full_name}\n'
            f'    Email: {user.email}\n'
            f'    Phone: {user.phone_number}\n'
            f'    CPS Number: {user.cps_number}\n'
            f'    Password: Amaruwebster093@'
        ))

    def create_restaurants(self):
        """Create sample restaurants for all location types across Tanzania."""
        self.stdout.write('\n[2/4] Creating Restaurants (All Location Types)...')
        
        restaurants_data = [
            # Universities
            {
                'name': 'University of Dar es Salaam',
                'code': 'UDSM',
                'location_type': LocationType.UNIVERSITY,
                'region': 'dar_es_salaam',
                'area': 'Mlimani',
                'city': 'Dar es Salaam',
                'contact_email': 'canteen@udsm.ac.tz',
                'capacity': 5000,
            },
            {
                'name': 'Sokoine University of Agriculture',
                'code': 'SUA',
                'location_type': LocationType.UNIVERSITY,
                'region': 'morogoro',
                'area': 'Mazimbu',
                'city': 'Morogoro',
                'contact_email': 'canteen@sua.ac.tz',
                'capacity': 3000,
            },
            {
                'name': 'University of Dodoma',
                'code': 'UDOM',
                'location_type': LocationType.UNIVERSITY,
                'region': 'dodoma',
                'area': 'Chimwaga',
                'city': 'Dodoma',
                'contact_email': 'canteen@udom.ac.tz',
                'capacity': 4000,
            },
            {
                'name': 'Muhimbili University (MUHAS)',
                'code': 'MUHAS',
                'location_type': LocationType.UNIVERSITY,
                'region': 'dar_es_salaam',
                'area': 'Upanga',
                'city': 'Dar es Salaam',
                'contact_email': 'canteen@muhas.ac.tz',
                'capacity': 2000,
            },
            {
                'name': 'Ardhi University',
                'code': 'ARU',
                'location_type': LocationType.UNIVERSITY,
                'region': 'dar_es_salaam',
                'area': 'Observation Hill',
                'city': 'Dar es Salaam',
                'contact_email': 'canteen@aru.ac.tz',
                'capacity': 1500,
            },
            {
                'name': 'Dar es Salaam Institute of Technology',
                'code': 'DIT',
                'location_type': LocationType.UNIVERSITY,
                'region': 'dar_es_salaam',
                'area': 'Morogoro Road',
                'city': 'Dar es Salaam',
                'contact_email': 'canteen@dit.ac.tz',
                'capacity': 2500,
            },
            
            # Markets
            {
                'name': 'Kariakoo Market Food Court',
                'code': 'KARIAKOO-MKT',
                'location_type': LocationType.MARKET,
                'region': 'dar_es_salaam',
                'area': 'Kariakoo',
                'city': 'Dar es Salaam',
                'contact_email': 'info@kariakoo-food.co.tz',
                'capacity': 1000,
            },
            {
                'name': 'Mwenge Market Canteen',
                'code': 'MWENGE-MKT',
                'location_type': LocationType.MARKET,
                'region': 'dar_es_salaam',
                'area': 'Mwenge',
                'city': 'Dar es Salaam',
                'contact_email': 'info@mwenge-food.co.tz',
                'capacity': 500,
            },
            {
                'name': 'Tegeta Market Food Center',
                'code': 'TEGETA-MKT',
                'location_type': LocationType.MARKET,
                'region': 'dar_es_salaam',
                'area': 'Tegeta',
                'city': 'Dar es Salaam',
                'contact_email': 'info@tegeta-food.co.tz',
                'capacity': 400,
            },
            {
                'name': 'Kisutu Market Eatery',
                'code': 'KISUTU-MKT',
                'location_type': LocationType.MARKET,
                'region': 'dar_es_salaam',
                'area': 'Kisutu',
                'city': 'Dar es Salaam',
                'contact_email': 'info@kisutu-food.co.tz',
                'capacity': 300,
            },
            
            # Offices/Workplaces
            {
                'name': 'PSPF Towers Canteen',
                'code': 'PSPF-OFFICE',
                'location_type': LocationType.OFFICE,
                'region': 'dar_es_salaam',
                'area': 'Posta',
                'city': 'Dar es Salaam',
                'contact_email': 'canteen@pspf.go.tz',
                'capacity': 800,
            },
            {
                'name': 'NIC House Food Court',
                'code': 'NIC-OFFICE',
                'location_type': LocationType.OFFICE,
                'region': 'dar_es_salaam',
                'area': 'Samora Avenue',
                'city': 'Dar es Salaam',
                'contact_email': 'canteen@nic.go.tz',
                'capacity': 600,
            },
            {
                'name': 'TRA Headquarters Canteen',
                'code': 'TRA-OFFICE',
                'location_type': LocationType.OFFICE,
                'region': 'dar_es_salaam',
                'area': 'Kivukoni',
                'city': 'Dar es Salaam',
                'contact_email': 'canteen@tra.go.tz',
                'capacity': 500,
            },
            {
                'name': 'Dodoma Parliament Canteen',
                'code': 'BUNGE-OFFICE',
                'location_type': LocationType.OFFICE,
                'region': 'dodoma',
                'area': 'Bunge',
                'city': 'Dodoma',
                'contact_email': 'canteen@bunge.go.tz',
                'capacity': 1000,
            },
            
            # Hospitals
            {
                'name': 'Muhimbili National Hospital Cafeteria',
                'code': 'MNH-HOSPITAL',
                'location_type': LocationType.HOSPITAL,
                'region': 'dar_es_salaam',
                'area': 'Upanga',
                'city': 'Dar es Salaam',
                'contact_email': 'cafeteria@mnh.go.tz',
                'capacity': 1500,
            },
            {
                'name': 'Amana Regional Hospital Cafeteria',
                'code': 'AMANA-HOSPITAL',
                'location_type': LocationType.HOSPITAL,
                'region': 'dar_es_salaam',
                'area': 'Ilala',
                'city': 'Dar es Salaam',
                'contact_email': 'cafeteria@amana.go.tz',
                'capacity': 600,
            },
            {
                'name': 'Mwananyamala Hospital Cafeteria',
                'code': 'MWANA-HOSPITAL',
                'location_type': LocationType.HOSPITAL,
                'region': 'dar_es_salaam',
                'area': 'Kinondoni',
                'city': 'Dar es Salaam',
                'contact_email': 'cafeteria@mwananyamala.go.tz',
                'capacity': 500,
            },
            
            # Industrial Areas
            {
                'name': 'Mikocheni Industrial Canteen',
                'code': 'MIKOCHENI-IND',
                'location_type': LocationType.INDUSTRIAL,
                'region': 'dar_es_salaam',
                'area': 'Mikocheni Light Industrial',
                'city': 'Dar es Salaam',
                'contact_email': 'canteen@mikocheni-ind.co.tz',
                'capacity': 800,
            },
            {
                'name': 'Ubungo Industrial Cafeteria',
                'code': 'UBUNGO-IND',
                'location_type': LocationType.INDUSTRIAL,
                'region': 'dar_es_salaam',
                'area': 'Ubungo',
                'city': 'Dar es Salaam',
                'contact_email': 'canteen@ubungo-ind.co.tz',
                'capacity': 1000,
            },
            {
                'name': 'Chang\'ombe Industrial Canteen',
                'code': 'CHANGOMBE-IND',
                'location_type': LocationType.INDUSTRIAL,
                'region': 'dar_es_salaam',
                'area': 'Chang\'ombe',
                'city': 'Dar es Salaam',
                'contact_email': 'canteen@changombe-ind.co.tz',
                'capacity': 700,
            },
            
            # General Restaurants
            {
                'name': 'Slipway Food Village',
                'code': 'SLIPWAY-REST',
                'location_type': LocationType.RESTAURANT,
                'region': 'dar_es_salaam',
                'area': 'Msasani',
                'city': 'Dar es Salaam',
                'contact_email': 'info@slipway-food.co.tz',
                'capacity': 400,
            },
            {
                'name': 'Mlimani City Food Court',
                'code': 'MLIMANI-REST',
                'location_type': LocationType.RESTAURANT,
                'region': 'dar_es_salaam',
                'area': 'Mlimani City',
                'city': 'Dar es Salaam',
                'contact_email': 'info@mlimani-food.co.tz',
                'capacity': 600,
            },
            
            # Mwanza Region
            {
                'name': 'St. Augustine University Canteen',
                'code': 'SAUT-MWZ',
                'location_type': LocationType.UNIVERSITY,
                'region': 'mwanza',
                'area': 'Nyegezi',
                'city': 'Mwanza',
                'contact_email': 'canteen@saut.ac.tz',
                'capacity': 2000,
            },
            {
                'name': 'Mwanza City Market Eatery',
                'code': 'MWZ-MARKET',
                'location_type': LocationType.MARKET,
                'region': 'mwanza',
                'area': 'Kirumba',
                'city': 'Mwanza',
                'contact_email': 'info@mwanza-market.co.tz',
                'capacity': 500,
            },
            
            # Arusha Region
            {
                'name': 'Nelson Mandela African Institution',
                'code': 'NMAIST',
                'location_type': LocationType.UNIVERSITY,
                'region': 'arusha',
                'area': 'Tengeru',
                'city': 'Arusha',
                'contact_email': 'canteen@nmaist.ac.tz',
                'capacity': 1500,
            },
            {
                'name': 'Arusha Central Market Food Court',
                'code': 'ARUSHA-MKT',
                'location_type': LocationType.MARKET,
                'region': 'arusha',
                'area': 'Central',
                'city': 'Arusha',
                'contact_email': 'info@arusha-market.co.tz',
                'capacity': 400,
            },
        ]
        
        created_count = 0
        for rest_data in restaurants_data:
            rest, created = Restaurant.objects.get_or_create(
                code=rest_data['code'],
                defaults=rest_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'  Created: {rest.name} ({rest.get_location_type_display()})')
        
        self.stdout.write(self.style.SUCCESS(f'  Total: {created_count} restaurants created'))

    def create_universities(self):
        """Create legacy universities for backwards compatibility."""
        self.stdout.write('\n[3/4] Creating Legacy Universities...')
        
        universities_data = [
            {'name': 'University of Dar es Salaam', 'code': 'UDSM', 'city': 'Dar es Salaam'},
            {'name': 'Sokoine University of Agriculture', 'code': 'SUA', 'city': 'Morogoro'},
            {'name': 'University of Dodoma', 'code': 'UDOM', 'city': 'Dodoma'},
            {'name': 'Muhimbili University', 'code': 'MUHAS', 'city': 'Dar es Salaam'},
            {'name': 'Ardhi University', 'code': 'ARU', 'city': 'Dar es Salaam'},
            {'name': 'Mzumbe University', 'code': 'MU', 'city': 'Morogoro'},
            {'name': 'Open University of Tanzania', 'code': 'OUT', 'city': 'Dar es Salaam'},
            {'name': 'Dar es Salaam Institute of Technology', 'code': 'DIT', 'city': 'Dar es Salaam'},
        ]
        
        created_count = 0
        for uni_data in universities_data:
            uni, created = University.objects.get_or_create(
                code=uni_data['code'],
                defaults=uni_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  Created {created_count} legacy universities'))

    def create_dietary_plans(self):
        """Create dietary plans for special food requirements."""
        self.stdout.write('\n[4/5] Creating Dietary Plans...')
        
        dietary_plans_data = [
            {
                'name': 'Ulcer Care Diet',
                'dietary_type': 'ulcer',
                'description': 'A diet designed for people with stomach ulcers. Focuses on foods that are gentle on the stomach lining.',
                'foods_to_avoid': 'Spicy foods, acidic foods, fried foods, alcohol, coffee, citrus fruits, tomatoes, carbonated drinks',
                'recommended_foods': 'Bananas, rice, oatmeal, lean proteins, vegetables (non-acidic), milk, yogurt, honey',
                'additional_price': 5000,
            },
            {
                'name': 'Diabetic Friendly Diet',
                'dietary_type': 'diabetic',
                'description': 'A diet designed for people with diabetes. Focuses on low glycemic foods and controlled portions.',
                'foods_to_avoid': 'Sugar, white bread, white rice, sugary drinks, sweets, processed foods, high-carb foods',
                'recommended_foods': 'Whole grains, vegetables, lean proteins, fish, beans, nuts, fruits (in moderation)',
                'additional_price': 5000,
            },
            {
                'name': 'Vegetarian Diet',
                'dietary_type': 'vegetarian',
                'description': 'Plant-based diet that excludes meat but includes dairy and eggs.',
                'foods_to_avoid': 'Meat, poultry, fish, seafood',
                'recommended_foods': 'Vegetables, fruits, grains, legumes, dairy, eggs, nuts, seeds',
                'additional_price': 3000,
            },
            {
                'name': 'Vegan Diet',
                'dietary_type': 'vegan',
                'description': 'Strictly plant-based diet that excludes all animal products.',
                'foods_to_avoid': 'Meat, poultry, fish, seafood, dairy, eggs, honey',
                'recommended_foods': 'Vegetables, fruits, grains, legumes, nuts, seeds, plant-based proteins',
                'additional_price': 5000,
            },
            {
                'name': 'Halal Diet',
                'dietary_type': 'halal',
                'description': 'Diet following Islamic dietary laws.',
                'foods_to_avoid': 'Pork, alcohol, non-halal meat',
                'recommended_foods': 'Halal-certified meat, fish, vegetables, fruits, grains',
                'additional_price': 0,
            },
            {
                'name': 'Gluten Free Diet',
                'dietary_type': 'gluten_free',
                'description': 'Diet free from gluten, suitable for celiac disease or gluten sensitivity.',
                'foods_to_avoid': 'Wheat, barley, rye, bread, pasta, most cereals, beer',
                'recommended_foods': 'Rice, quinoa, corn, potatoes, meat, fish, fruits, vegetables, gluten-free products',
                'additional_price': 7000,
            },
            {
                'name': 'Low Sodium Diet',
                'dietary_type': 'low_sodium',
                'description': 'Diet low in salt, suitable for high blood pressure or heart conditions.',
                'foods_to_avoid': 'Processed foods, canned soups, fast food, salty snacks, soy sauce',
                'recommended_foods': 'Fresh fruits, vegetables, lean proteins, herbs and spices (instead of salt)',
                'additional_price': 3000,
            },
            {
                'name': 'Renal Diet',
                'dietary_type': 'renal',
                'description': 'Diet for kidney disease patients. Controlled protein, sodium, potassium, and phosphorus.',
                'foods_to_avoid': 'High potassium foods (bananas, oranges), high sodium foods, high phosphorus foods, excessive protein',
                'recommended_foods': 'Low potassium vegetables, apples, berries, white rice, moderate lean protein',
                'additional_price': 8000,
            },
            {
                'name': 'Heart Healthy Diet',
                'dietary_type': 'heart_healthy',
                'description': 'Diet focused on cardiovascular health.',
                'foods_to_avoid': 'Trans fats, saturated fats, processed meats, excessive salt, fried foods',
                'recommended_foods': 'Fish, whole grains, fruits, vegetables, nuts, olive oil, lean proteins',
                'additional_price': 4000,
            },
            {
                'name': 'Pregnancy Diet',
                'dietary_type': 'pregnancy',
                'description': 'Nutritious diet for pregnant women with extra folic acid, iron, and calcium.',
                'foods_to_avoid': 'Raw fish, unpasteurized dairy, excessive caffeine, alcohol, raw eggs',
                'recommended_foods': 'Leafy greens, lean proteins, whole grains, dairy, fruits, iron-rich foods',
                'additional_price': 5000,
            },
        ]
        
        created_count = 0
        for plan_data in dietary_plans_data:
            plan, created = DietaryPlan.objects.get_or_create(
                dietary_type=plan_data['dietary_type'],
                defaults=plan_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'  Created: {plan.name}')
        
        self.stdout.write(self.style.SUCCESS(f'  Total: {created_count} dietary plans created'))

    def create_subscription_plans(self):
        """Create subscription plans for restaurants."""
        self.stdout.write('\n[5/5] Creating Subscription Plans...')
        
        plans_data = [
            {
                'name': 'Daily Plan',
                'duration_type': 'day',
                'duration_days': 1,
                'price': 3000,
                'meals_per_day': 2,
            },
            {
                'name': 'Weekly Plan',
                'duration_type': 'week',
                'duration_days': 7,
                'price': 14000,
                'meals_per_day': 2,
            },
            {
                'name': 'Bi-Weekly Plan',
                'duration_type': 'week',
                'duration_days': 14,
                'price': 25000,
                'meals_per_day': 2,
            },
            {
                'name': 'Monthly Plan',
                'duration_type': 'month',
                'duration_days': 30,
                'price': 45000,
                'meals_per_day': 2,
            },
            {
                'name': 'Semester Plan',
                'duration_type': 'semester',
                'duration_days': 120,
                'price': 150000,
                'meals_per_day': 2,
            },
        ]
        
        # Create plans for restaurants
        restaurants = Restaurant.objects.all()
        created_count = 0
        
        for restaurant in restaurants:
            for plan_data in plans_data:
                plan, created = SubscriptionPlan.objects.get_or_create(
                    restaurant=restaurant,
                    name=plan_data['name'],
                    defaults=plan_data
                )
                if created:
                    created_count += 1
        
        # Also create global plans (no specific restaurant)
        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.get_or_create(
                restaurant=None,
                name=plan_data['name'],
                defaults=plan_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  Created {created_count} subscription plans'))

import requests
import csv
from time import sleep
from decimal import Decimal
from django.core.management.base import BaseCommand
from users.models import User, LawyerProfile


def geocode_address(work_place):
    if not work_place.strip():
        return None, None
    api_key = 'pk.282de0e70acbaf9a575d24efb64a2025'
    url = f'https://us1.locationiq.com/v1/search.php?key={api_key}&q={work_place}&format=json'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            lat = data[0].get('lat')
            lon = data[0].get('lon')
            if lat and lon:
                return float(lat), float(lon)
    except Exception as e:
        print(f"Geocoding failed for '{work_place}': {e}")
    return None, None


class Command(BaseCommand):
    help = 'Load cleaned lawyers data from CSV into database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the cleaned lawyers CSV file')
        parser.add_argument('--dry-run', action='store_true', help='Run without saving to DB')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        dry_run = options['dry_run']
        count = 0

        with open(csv_file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if count >= 50:
                    break
                profile_id = row['profile_id'].strip()
                full_name = row['name'].strip()
                name_parts = full_name.split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                address = row['Physical Address'].strip()
                lat, lon = geocode_address(address)
                if lat is None or lon is None:
                    continue
                lat = Decimal(str(lat))
                lon = Decimal(str(lon))
                user = User.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    role='lawyer',
                    is_active=True,
                )
                lawyer_profile_defaults = {
                    'user': user,
                    'profile_id': profile_id,
                    'practising_status': row['Practising Status'].strip().lower() == 'true',
                    'work_place': row['Work Place'].strip(),
                    'physical_address': address,
                    'latitude': lat,
                    'longitude': lon,
                    'cpd_points_2025': int(float(row['CPD_2025_CPD_Points'])),
                    'criminal_law': row.get('Practiced_Criminal Law - General', 'no').strip().lower() == 'yes',
                    'constitutional_law': row.get('Practiced_Constitutional And Human Rights Law', 'no').strip().lower() == 'yes',
                    'corporate_law': row.get('Practiced_Corporate Law', 'no').strip().lower() == 'yes',
                    'family_law': row.get('Practiced_Family Law & Succession Matters', 'no').strip().lower() == 'yes',
                    'pro_bono_legal_services': row.get('Practiced_Pro Bono Legal Services', 'no').strip().lower() == 'yes',
                    'alternative_dispute_resolution': row.get('Practiced_Alternative Dispute Resolution', 'no').strip().lower() == 'yes',
                    'regional_and_international_law': row.get('Practiced_Regional & International Law', 'no').strip().lower() == 'yes',
                    'mining_law': row.get('Practiced_Mining Law', 'no').strip().lower() == 'yes',
                }
                if not dry_run:
                    lawyer_profile, created = LawyerProfile.objects.update_or_create(
                        practice_number=row['Practice Number'].strip(),
                        defaults=lawyer_profile_defaults
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Created: {full_name}"))
                    else:
                        self.stdout.write(self.style.NOTICE(f"Updated: {full_name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"[DRY RUN] Would save: {full_name}"))
                count += 1
                sleep(0.6)
                if count % 10 == 0:
                    self.stdout.write(self.style.HTTP_INFO(f"Processed {count} lawyers so far..."))
        self.stdout.write(
            self.style.SUCCESS(f"Successfully loaded {count} lawyer records.")
        )

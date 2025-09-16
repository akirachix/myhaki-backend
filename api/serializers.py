from rest_framework import serializers
from cpd.models import CPDPoint
from cases.models import CaseAssignment, Detainee, Case
from cases.models import CaseAssignment, Case, Detainee
from users.models import User, LawyerProfile
import requests
import json
from django.conf import settings
import os
from dotenv import load_dotenv
from cases.tasks import async_assign_case
import logging


load_dotenv()

TRANSLATE_PLUS_API_KEY = os.getenv('TRANSLATE_PLUS_API_KEY')
LOCATIONIQ_API_KEY = os.getenv('LOCATIONIQ_API_KEY')
TRANSLATE_PLUS_URL = os.getenv('TRANSLATE_PLUS_URL')
LOCATIONIQ_URL = os.getenv('LOCATIONIQ_URL')
from cases.models import CaseAssignment, Case, Detainee
from users.models import User, LawyerProfile, ApplicantProfile, LskAdminProfile

class LawyerProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.CharField(source='user.email')

    class Meta:
        model = LawyerProfile
        fields = ['practice_number', 'first_name', 'last_name', 'email', 'verified']

class DetaineeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detainee
        fields = '__all__'



class CaseSerializer(serializers.ModelSerializer):
    detainee = serializers.PrimaryKeyRelatedField(queryset=Detainee.objects.all(), required=True )
    detainee_details = DetaineeSerializer(source='detainee', read_only=True)
    assigned_lawyer = LawyerProfileSerializer(source='assignments.first.lawyer', read_only=True)
    predicted_case_type = serializers.CharField(required=False)
    predicted_urgency_level = serializers.CharField(required=False)

    class Meta:
        model = Case
        fields = '__all__'

    def translate_text(self, text):
        url = TRANSLATE_PLUS_URL
        headers = {
            "x-api-key": TRANSLATE_PLUS_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "source": "sw",
            "target": "en"
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            res = response.json()
            if "translations" in res and "translation" in res["translations"]:
                return res["translations"]["translation"]
            else:
                return text
        else:
            return text

    def geocode_location(self, location_text):
        url = LOCATIONIQ_URL
        params = {
            "key": LOCATIONIQ_API_KEY,
            "q": location_text,
            "format": "json"
        }
        response = requests.get(url, params=params)
        if response.status_code == 200 and response.json():
            data = response.json()[0]
            return data['lat'], data['lon']
        return None, None

    def classify_case_ai(self, text):
        text_lower = text.lower()
        if any(word in text_lower for word in ['theft', 'robbery', 'assault', 'murder', 'drugs']):
            return 'criminal', 'high'
        elif any(word in text_lower for word in ['divorce', 'custody', 'property', 'contract']):
            return 'civil', 'medium'
        else:
            return 'other', 'low'

    def create(self, validated_data):
        validated_data['predicted_case_type'] = 'other'
        validated_data['predicted_urgency_level'] = 'medium'

        if 'case_description' in validated_data:
            validated_data['case_description'] = self.translate_text(validated_data['case_description'])

        if 'dependents' in validated_data and validated_data['dependents']:
            dependents_str = json.dumps(validated_data['dependents'])
            translated_dependents_str = self.translate_text(dependents_str)
            validated_data['dependents'] = json.loads(translated_dependents_str)

        if 'police_station' in validated_data and validated_data['police_station']:
            translated_location = self.translate_text(validated_data['police_station'])
            validated_data['police_station'] = translated_location
            lat, lon = self.geocode_location(translated_location)
            validated_data['latitude'] = lat
            validated_data['longitude'] = lon

        predicted_type, predicted_urgency = self.classify_case_ai(validated_data['case_description'])
        validated_data['predicted_case_type'] = predicted_type
        validated_data['predicted_urgency_level'] = predicted_urgency

        case = super().create(validated_data)
        try:
            async_assign_case.delay(case.case_id)
        except Exception as e:
            logger = logging.getLogger("django")
            logger.error(f"Celery async_assign_case failed for case_id {case.case_id}: {e}")
            
        return case

    def update(self, instance, validated_data):
        if 'case_description' in validated_data:
            validated_data['case_description'] = self.translate_text(validated_data['case_description'])

        if 'dependents' in validated_data and validated_data['dependents']:
            dependents_str = json.dumps(validated_data['dependents'])
            translated_dependents_str = self.translate_text(dependents_str)
            validated_data['dependents'] = json.loads(translated_dependents_str)

        if 'police_station' in validated_data and validated_data['police_station']:
            translated_location = self.translate_text(validated_data['police_station'])
            validated_data['police_station'] = translated_location
            lat, lon = self.geocode_location(translated_location)
            validated_data['latitude'] = lat
            validated_data['longitude'] = lon

        return super().update(instance, validated_data)

    def validate(self, data):
        if data.get('monthly_income') == 'greater_than_30000':
            raise serializers.ValidationError({"monthly_income": "You are not eligible for this service"})
        return data



class CPDPointSerializer(serializers.ModelSerializer):
    total_points = serializers.SerializerMethodField()
    

    class Meta:
        model = CPDPoint
        fields = ['cpd_id', 'user', 'case', 'description', 'points_earned', 'total_points', 'created_at', 'updated_at']

    def get_total_points(self, obj):
        return obj.points_earned + obj.lawyer.cpd_points_2025


class CaseAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseAssignment
        fields = '__all__'
    class Meta:
        model = CaseAssignment
        fields = '__all__'



class UserSerializer(serializers.ModelSerializer):
    practice_number = serializers.CharField(required=False, allow_blank=True, write_only=True)
    password = serializers.CharField(write_only=True)
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    profile_id = serializers.SerializerMethodField()
    verified = serializers.SerializerMethodField()
    practising_status = serializers.SerializerMethodField()
    work_place = serializers.SerializerMethodField()
    physical_address = serializers.SerializerMethodField()
    cpd_points_2025 = serializers.SerializerMethodField()
    criminal_law = serializers.SerializerMethodField()
    constitutional_law = serializers.SerializerMethodField()
    corporate_law = serializers.SerializerMethodField()
    family_law = serializers.SerializerMethodField()
    pro_bono_legal_services = serializers.SerializerMethodField()
    alternative_dispute_resolution = serializers.SerializerMethodField()
    regional_and_international_law = serializers.SerializerMethodField()
    mining_law = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'email', 'role', 'phone_number', 'image',
            'is_deleted', 'created_at', 'updated_at', 'password', 'practice_number',
            'profile_id', 'verified', 'practising_status', 'work_place',
            'latitude', 'longitude', 'physical_address', 'cpd_points_2025', 'criminal_law',
            'constitutional_law', 'corporate_law', 'family_law', 'pro_bono_legal_services',
            'alternative_dispute_resolution', 'regional_and_international_law', 'mining_law',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request', None)
        if request and request.query_params.get('role') not in ['lawyer', 'lsk_admin']:
            self.fields.pop('practice_number', None)

    def get_lawyer_profile(self, user):
        if user.role in ['lawyer', 'lsk_admin']:
            try:
                return user.lawyer_profile
            except LawyerProfile.DoesNotExist:
                return None
        return None

    def get_profile_id(self, obj):
        profile = self.get_lawyer_profile(obj)
        return profile.profile_id if profile else None

    def get_latitude(self, obj):
        profile = self.get_lawyer_profile(obj)
        return str(profile.latitude) if profile and profile.latitude else None

    def get_longitude(self, obj):
        profile = self.get_lawyer_profile(obj)
        return str(profile.longitude) if profile and profile.longitude else None

    def get_verified(self, obj):
        profile = self.get_lawyer_profile(obj)
        return profile.verified if profile else None

    def get_practising_status(self, obj):
        profile = self.get_lawyer_profile(obj)
        return profile.practising_status if profile else None

    def get_work_place(self, obj):
        profile = self.get_lawyer_profile(obj)
        return profile.work_place if profile else None

    def get_physical_address(self, obj):
        profile = self.get_lawyer_profile(obj)
        return profile.physical_address if profile else None

    def get_cpd_points_2025(self, obj):
        profile = self.get_lawyer_profile(obj)
        return profile.cpd_points_2025 if profile else None

    def get_criminal_law(self, obj):
        profile = self.get_lawyer_profile(obj)
        return profile.criminal_law if profile else None

    def get_constitutional_law(self, obj):
        profile = self.get_lawyer_profile(obj)
        return profile.constitutional_law if profile else None

    def get_corporate_law(self, obj):
        profile = self.get_lawyer_profile(obj)
        return profile.corporate_law if profile else None

    def get_family_law(self, obj):
        profile = self.get_lawyer_profile(obj)
        return profile.family_law if profile else None

    def get_pro_bono_legal_services(self, obj):
        profile = self.get_lawyer_profile(obj)
        return profile.pro_bono_legal_services if profile else None

    def get_alternative_dispute_resolution(self, obj):
        profile = self.get_lawyer_profile(obj)
        return profile.alternative_dispute_resolution if profile else None

    def get_regional_and_international_law(self, obj):
        profile = self.get_lawyer_profile(obj)
        return profile.regional_and_international_law if profile else None

    def get_mining_law(self, obj):
        profile = self.get_lawyer_profile(obj)
        return profile.mining_law if profile else None

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        practice_number = validated_data.pop('practice_number', None)

        user = User.objects.create_user(
            email=validated_data['email'],
            password=password,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', 'lawyer'),
            phone_number=validated_data.get('phone_number', ''),
            image=validated_data.get('image', None),
            is_deleted=validated_data.get('is_deleted', False),
        )

    if practice_number and User.role in ['lawyer', 'lsk_admin']:
            LawyerProfile.objects.get_or_create(
                user=User,
                defaults={'practice_number': practice_number.strip()}
            )


    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        practice_number = validated_data.pop('practice_number', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        if instance.role in ['lawyer', 'lsk_admin']:
            profile, created = LawyerProfile.objects.get_or_create(user=instance)
            if practice_number is not None:
                profile.practice_number = practice_number
                profile.save()

        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.role not in ['lawyer', 'lsk_admin']:
            lawyer_fields = [
                'profile_id', 'verified', 'practising_status', 'practice_number', 'work_place',
                'latitude', 'longitude', 'physical_address', 'cpd_points_2025', 'criminal_law',
                'constitutional_law', 'corporate_law', 'family_law', 'pro_bono_legal_services',
                'alternative_dispute_resolution', 'regional_and_international_law', 'mining_law',
            ]
            for field in lawyer_fields:
                data.pop(field, None)
        return data

class LawyerRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    practice_number = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    class Meta:
        model = User
        fields = ['email', 'password', 'practice_number', 'first_name', 'last_name']
        extra_kwargs = {'role': {'default': 'lawyer'}}
    def validate_practice_number(self, value):
        value = value.strip().upper()
        try:
            lawyer_profile = LawyerProfile.objects.get(practice_number__iexact=value)
            if lawyer_profile.practice_number != value:
                lawyer_profile.practice_number = value
                lawyer_profile.save()
            return value
        except LawyerProfile.DoesNotExist:
            raise serializers.ValidationError("No lawyer found with this practice number.")
    def create(self, validated_data):
        password = validated_data.pop('password')
        practice_number = validated_data.pop('practice_number')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        email = validated_data.pop('email')
        lawyer_profile = LawyerProfile.objects.get(practice_number__iexact=practice_number.strip().upper())
        user = lawyer_profile.user
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.role = 'lawyer'
        user.is_active = True
        user.set_password(password)
        user.save()
        lawyer_profile.verified = True
        lawyer_profile.save()
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
class ApplicantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = ApplicantProfile
        fields = '__all__'

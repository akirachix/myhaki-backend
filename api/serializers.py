from rest_framework import serializers
from cpd.models import CPDPoint
from cases.models import CaseAssignment, Detainee, Case
from cases.utils import normalize_urgency
from cases.tasks import async_assign_case
from users.models import User, LawyerProfile, ApplicantProfile 
import requests
import json
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger("django")

TRANSLATE_PLUS_API_KEY = os.getenv('TRANSLATE_PLUS_API_KEY')
LOCATIONIQ_API_KEY = os.getenv('LOCATIONIQ_API_KEY')
TRANSLATE_PLUS_URL = os.getenv('TRANSLATE_PLUS_URL')
LOCATIONIQ_URL = os.getenv('LOCATIONIQ_URL')
AI_AGENT_URL = os.getenv('AI_AGENT_URL')


class LawyerProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = LawyerProfile
        fields = ['profile_id', 'practice_number', 'first_name', 'last_name', 'email', 'verified', 'cpd_points_2025',
                  'practising_status', 'work_place', 'physical_address', 'latitude', 'longitude',
                  'criminal_law', 'constitutional_law', 'corporate_law', 'family_law',
                  'pro_bono_legal_services', 'alternative_dispute_resolution',
                  'regional_and_international_law', 'mining_law']
        read_only_fields = ['profile_id', 'verified']


class DetaineeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detainee
        fields = '__all__'


class CaseSerializer(serializers.ModelSerializer):
    detainee = serializers.PrimaryKeyRelatedField(queryset=Detainee.objects.all(), required=True)
    detainee_details = DetaineeSerializer(source='detainee', read_only=True)
    assigned_lawyer_details = serializers.SerializerMethodField(read_only=True)
    predicted_case_type = serializers.CharField(required=False, allow_blank=True, read_only=True)
    predicted_urgency_level = serializers.CharField(required=False, allow_blank=True, read_only=True)

    class Meta:
        model = Case
        fields = '__all__'
        read_only_fields = ['predicted_case_type', 'predicted_urgency_level', 'assignment_attempts'] 
    
    def get_assigned_lawyer_details(self, obj):
        """
        Returns the lawyer assigned to this case via an active CaseAssignment.
        """
        assignment = CaseAssignment.objects.filter(
            case=obj,
            is_assigned=True,
            status__in=['pending', 'accepted']  
        ).select_related('lawyer', 'lawyer__user').first()

        if assignment and assignment.lawyer:
            return LawyerProfileSerializer(assignment.lawyer).data
        return None

    def translate_text(self, text):
        if not text:
            return text
        url = TRANSLATE_PLUS_URL
        headers = {"x-api-key": TRANSLATE_PLUS_API_KEY, "Content-Type": "application/json"}
        payload = {"text": text, "source": "sw", "target": "en"} 
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            if response.status_code == 200:
                res = response.json()
                if "translations" in res and "translation" in res["translations"]:
                    return res["translations"]["translation"]
                logger.warning(f"Translation API response missing 'translation' key: {res}")
                return text 
            else:
                logger.error(f"Translation API returned status {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Translation failed: {e}")
        return text 

    def geocode_location(self, location_text):
        if not location_text:
            return None, None
        url = LOCATIONIQ_URL
        params = {"key": LOCATIONIQ_API_KEY, "q": location_text, "format": "json"}
        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200 and response.json():
                data = response.json()[0] 
                return data['lat'], data['lon']
            else:
                logger.error(f"Geocoding API returned status {response.status_code} or empty response for '{location_text}': {response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Geocoding failed for '{location_text}': {e}")
        return None, None

    def classify_case_ai(self, case_description, trial_date):
        """Call AI agent for predicted case type and urgency"""
        url = AI_AGENT_URL
        if not url:
            logger.error("AI_AGENT_URL is not set in environment variables.")
            return "criminal", "medium"
        try:
            response = requests.post(
                url,
                json={
                    "case_description": case_description,
                    "trial_date": str(trial_date) if trial_date else None
                },
                timeout=120 
            )
            if response.status_code == 200:
                result = response.json()
                prediction = result.get("prediction", {}).get("response", {})
                logger.debug(f"AI Agent prediction: {prediction}")
                case_type = prediction.get("case_type", "other").lower()
                urgency = prediction.get("urgency", "medium").lower()
                return case_type, normalize_urgency(urgency)
            else:
                return self._fallback_classify_case_ai(case_description)  
        except requests.exceptions.RequestException as e:
            logger.error(f"AI agent prediction request failed: {e}")
        return self._fallback_classify_case_ai(case_description) 
       
    def _fallback_classify_case_ai(self, text):
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['rape', 'sexual assault', 'molestation', 'murder', 'terror']):
            return 'criminal', 'high'
        elif any(word in text_lower for word in ['theft', 'robbery', 'assault', 'drugs', 'criminal']):
            return 'criminal', 'high'
        elif any(word in text_lower for word in ['divorce', 'custody', 'family']):
            return 'family', 'high'
        elif any(word in text_lower for word in ['contract', 'property', 'dispute', 'civil', 'corporate']):
            return 'corporate', 'medium'
        elif any(word in text_lower for word in ['human rights', 'constitutional']):
            return 'constitutional and human rights', 'high'
        elif any(word in text_lower for word in ['labour', 'employment', 'worker']):
            return 'labor', 'medium'
        elif any(word in text_lower for word in ['environment', 'pollution']):
            return 'environment', 'medium'
        else:
            return 'criminal', 'medium'

    def create(self, validated_data):
        if 'case_description' in validated_data:
            validated_data['case_description'] = self.translate_text(validated_data['case_description'])

        if validated_data.get('dependents'):
            try:
                dependents_str = json.dumps(validated_data['dependents'])
                translated_dependents_str = self.translate_text(dependents_str)
                validated_data['dependents'] = json.loads(translated_dependents_str)
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Error processing dependents for translation: {e}")
                pass

        if 'police_station' in validated_data and validated_data['police_station']:
            translated_location = self.translate_text(validated_data['police_station'])
            validated_data['police_station'] = translated_location
            lat, lon = self.geocode_location(translated_location)
            validated_data['latitude'] = lat
            validated_data['longitude'] = lon

        trial_date = validated_data.get('trial_date')
        predicted_type, predicted_urgency = self.classify_case_ai(
            validated_data.get('case_description', ''), trial_date
        )
        validated_data['predicted_case_type'] = predicted_type
        validated_data['predicted_urgency_level'] = predicted_urgency

        case = super().create(validated_data)

        try:
            case.status = 'pending'
            case.assignment_attempts = 0 
            case.save()
            
            async_assign_case.delay(case.case_id)
            logger.info(f"Celery task async_assign_case for case {case.case_id} dispatched.")
        except Exception as e:
            logger.error(f"Post-creation logic (setting status/assignment or Celery dispatch) failed for case {case.case_id}: {e}")

        return case

    def update(self, instance, validated_data):
        if 'case_description' in validated_data:
            validated_data['case_description'] = self.translate_text(validated_data['case_description'])

        if validated_data.get('dependents'):
            try:
                dependents_str = json.dumps(validated_data['dependents'])
                translated_dependents_str = self.translate_text(dependents_str)
                validated_data['dependents'] = json.loads(translated_dependents_str)
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Error processing dependents for translation during update: {e}")
                pass

        if 'police_station' in validated_data and validated_data['police_station']:
            translated_location = self.translate_text(validated_data['police_station'])
            validated_data['police_station'] = translated_location
            lat, lon = self.geocode_location(translated_location)
            validated_data['latitude'] = lat
            validated_data['longitude'] = lon

        reclassify = False
        new_description = validated_data.get('case_description', instance.case_description)
        new_trial_date = validated_data.get('trial_date', instance.trial_date)

        if new_description != instance.case_description:
            reclassify = True
        if new_trial_date != instance.trial_date:
            reclassify = True

        if reclassify:
            trial_date = validated_data.get('trial_date', instance.trial_date)
            case_description = validated_data.get('case_description', instance.case_description)
            predicted_type, predicted_urgency = self.classify_case_ai(
                case_description, trial_date
            )
            validated_data['predicted_case_type'] = predicted_type
            validated_data['predicted_urgency_level'] = predicted_urgency

        return super().update(instance, validated_data)

    def validate(self, data):
        if data.get('monthly_income') == 'greater_than_30000':
            raise serializers.ValidationError({"monthly_income": "You are not eligible for this service based on income."})
        return data


class CPDPointSerializer(serializers.ModelSerializer):
    total_points = serializers.SerializerMethodField()

    class Meta:
        model = CPDPoint
        fields = ['cpd_id', 'lawyer', 'case', 'description', 'points_earned', 'total_points', 'created_at', 'updated_at']
        read_only_fields = ['cpd_id', 'created_at', 'updated_at', 'lawyer', 'case']

    def get_total_points(self, obj):
        if obj.lawyer is None:
            return obj.points_earned if obj.points_earned is not None else 0
        else:
            lawyer_total_cpd = getattr(obj.lawyer, 'cpd_points_2025', 0)
            return lawyer_total_cpd


class CaseAssignmentSerializer(serializers.ModelSerializer):
    lawyer_details = LawyerProfileSerializer(source='lawyer', read_only=True)
    case_details = CaseSerializer(source='case', read_only=True)

    class Meta:
        model = CaseAssignment
        fields = '__all__'
        read_only_fields = ['assignment_id', 'is_assigned', 'assign_date', 'status', 'rejection_count', 'created_at', 'updated_at', 'confirmed_by_applicant', 'confirmed_by_lawyer']


class UserSerializer(serializers.ModelSerializer):
    practice_number = serializers.CharField(required=False, allow_blank=True, write_only=True)
    password = serializers.CharField(write_only=True)
    profile_id = serializers.SerializerMethodField()
    verified = serializers.SerializerMethodField()
    practising_status = serializers.SerializerMethodField()
    work_place = serializers.SerializerMethodField()
    physical_address = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    cpd_points_2025 = serializers.IntegerField( source='lawyer_profile.cpd_points_2025',required=True,allow_null=False)
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
        read_only_fields = ['id', 'is_deleted', 'created_at', 'updated_at', 'profile_id', 'verified']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'phone_number': {'required': True}
        }

    def _get_lawyer_profile(self, user):
        """Helper to get lawyer profile if user is a lawyer or lsk_admin."""
        if user.role in ['lawyer', 'lsk_admin']:
            try:
                return user.lawyer_profile
            except LawyerProfile.DoesNotExist:
                return None
        return None

    def get_profile_id(self, obj):
        profile = self._get_lawyer_profile(obj)
        return profile.profile_id if profile else None

    def get_latitude(self, obj):
        profile = self._get_lawyer_profile(obj)
        return str(profile.latitude) if profile and profile.latitude else None

    def get_longitude(self, obj):
        profile = self._get_lawyer_profile(obj)
        return str(profile.longitude) if profile and profile.longitude else None

    def get_verified(self, obj):
        profile = self._get_lawyer_profile(obj)
        return profile.verified if profile else None

    def get_practising_status(self, obj):
        profile = self._get_lawyer_profile(obj)
        return profile.practising_status if profile else None

    def get_work_place(self, obj):
        profile = self._get_lawyer_profile(obj)
        return profile.work_place if profile else None

    def get_physical_address(self, obj):
        profile = self._get_lawyer_profile(obj)
        return profile.physical_address if profile else None

    def get_cpd_points_2025(self, obj):
        profile = self._get_lawyer_profile(obj)
        return profile.cpd_points_2025 if profile else None
    
    def get_criminal_law(self, obj):
        profile = self._get_lawyer_profile(obj)
        return profile.criminal_law if profile else None

    def get_constitutional_law(self, obj):
        profile = self._get_lawyer_profile(obj)
        return profile.constitutional_law if profile else None
    
    def get_corporate_law(self, obj):
        profile = self._get_lawyer_profile(obj)
        return profile.corporate_law if profile else None

    def get_family_law(self, obj):
        profile = self._get_lawyer_profile(obj)
        return profile.family_law if profile else None

    def get_pro_bono_legal_services(self, obj):
        profile = self._get_lawyer_profile(obj)
        return profile.pro_bono_legal_services if profile else None

    def get_alternative_dispute_resolution(self, obj):
        profile = self._get_lawyer_profile(obj)
        return profile.alternative_dispute_resolution if profile else None

    def get_regional_and_international_law(self, obj):
        profile = self._get_lawyer_profile(obj)
        return profile.regional_and_international_law if profile else None

    def get_mining_law(self, obj):
        profile = self._get_lawyer_profile(obj)
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
        
        if practice_number and user.role in ['lawyer', 'lsk_admin']:
            LawyerProfile.objects.get_or_create(
                user=user,
                defaults={'practice_number': practice_number.strip()}
            )
             
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        practice_number = validated_data.pop('practice_number', None)
        cpd_points_2025 = validated_data.pop('cpd_points_2025', None)
        

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
            if cpd_points_2025 is not None:
                profile.cpd_points_2025 = cpd_points_2025
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

from rest_framework import serializers
from cpd.models import CPDPoint
from cases.models import CaseAssignment, Detainee, Case
import requests
import json
from django.conf import settings

class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = '__all__'

    def translate_text(self, text):
        url = "https://api.translateplus.io/v1/translate"
        headers = {
            "x-api-key": settings.TRANSLATE_PLUS_API_KEY,
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
                print("Something is wrong with the response structure:", res)
                return text
        else:
            print(f"Translation API error {response.status_code}:", response.text)
            return text

    def geocode_location(self, location_text):
        url = "https://us1.locationiq.com/v1/search.php"
        params = {
            "key": settings.LOCATIONIQ_API_KEY,
            "q": location_text,
            "format": "json"
        }
        response = requests.get(url, params=params)
        if response.status_code == 200 and response.json():
            data = response.json()[0]
            return data['lat'], data['lon']
        return None, None

    def create(self, validated_data):
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

        return super().create(validated_data)

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
            raise serializers.ValidationError(
                {"monthly_income": "You are not eligible for this service"}
            )
        return data


class CPDPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPDPoint
        fields = '__all__'


class CaseAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseAssignment
        fields = '__all__'


class DetaineeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detainee
        fields = '__all__'

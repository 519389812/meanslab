from django.shortcuts import render
from django.http import JsonResponse
from district.models import District


def get_province(request):
    provinces = District.objects.filter(parent__isnull=True).values()
    return JsonResponse({"provinces": provinces})


def get_city(request):
    city_id = request.GET.get('city_id')
    cities = District.objects.filter(parent_id=city_id).values()
    return JsonResponse({"cities": cities})


def get_district(request):
    district_id = request.GET.get('district_id')
    districts = District.objects.filter(parent_id=district_id).values()
    return JsonResponse({'districts': districts})

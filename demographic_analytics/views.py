from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from crm.models import TelegramUser
from crm.serializers import TelegramUserSerializer
from django.db.models import Avg, Count, IntegerField, Sum
from django.db.models.functions import Cast

class FirstLevelAPIView(APIView):
    def get(self, request, region_name):
        # Фильтрация пользователей по региону
        users = TelegramUser.objects.filter(region=region_name)
        if not users.exists():
            return Response({'error': 'Регион не найден'}, status=status.HTTP_404_NOT_FOUND)

        total_users = users.count()

        # Распределение по полу
        male_count = users.filter(gender__iexact="Мужской").count()
        female_count = users.filter(gender__iexact="Женский").count()
        male_percentage = round((male_count / total_users * 100), 1) if total_users > 0 else 0
        female_percentage = round((female_count / total_users * 100), 1) if total_users > 0 else 0

        # Возрастное распределение
        age_groups = {
            "under_18": users.filter(age__lt=18).count(),
            "18_25": users.filter(age__gte=18, age__lte=25).count(),
            "26_40": users.filter(age__gte=26, age__lte=40).count(),
            "41_60": users.filter(age__gte=41, age__lte=60).count(),
            "61_100": users.filter(age__gte=61, age__lte=100).count(),
            "over_100": users.filter(age__gt=100).count()
        }
        average_age = round(users.aggregate(Avg('age'))['age__avg'], 1) if users.exists() else "Нет данных"

        # Статистика по детям
        children_stats = {}
        for i in range(21):
            children_stats[f"{i}_children"] = users.annotate(children_as_int=Cast('children', IntegerField())).filter(
                children_as_int=i).count()

        total_children = users.annotate(children_as_int=Cast('children', IntegerField())).aggregate(
            total=Sum('children_as_int')
        )['total'] or 0

        avg_children = round(users.annotate(children_as_int=Cast('children', IntegerField())).aggregate(
            avg=Avg('children_as_int')
        )['avg'], 1) if users.exists() else 0

        # Социальные пособия
        benefits_stats = {
            "receiving_benefits": users.filter(benefits__iexact="Да").count(),
            "average_age_benefit_recipients": round(users.filter(benefits__iexact="Да").aggregate(Avg('age'))[
                                                    'age__avg'], 1) if users.filter(benefits__iexact="Да").exists() else "Нет данных",
            "percentage_with_children": round((users.filter(benefits__iexact="Да").exclude(
                children="0").count() / total_users * 100), 1) if total_users > 0 else 0,
        }

        # Категории семейного положения
        valid_marital_statuses = ["Холост/Не замужем", "Женат/Замужем", "В разводе", "Вдовец/Вдова"]
        marital_status_distribution = {
            status: users.filter(marital_status=status).count()
            for status in valid_marital_statuses
        }
        marital_status_distribution["Не указано"] = users.filter(marital_status__isnull=True).count()
        marital_status_avg_age = {
            status: round(users.filter(marital_status=status).aggregate(avg_age=Avg('age'))['avg_age'], 1) or "Нет данных"
            for status in valid_marital_statuses
        }

        # Распределение по возрасту и полу
        age_gender_distribution = {
            "male": {
                "under_18": users.filter(gender__iexact="Мужской", age__lt=18).count(),
                "18_25": users.filter(gender__iexact="Мужской", age__gte=18, age__lte=25).count(),
                "26_40": users.filter(gender__iexact="Мужской", age__gte=26, age__lte=40).count(),
                "41_60": users.filter(gender__iexact="Мужской", age__gte=41, age__lte=60).count(),
                "61_100": users.filter(gender__iexact="Мужской", age__gte=61, age__lte=100).count(),
                "over_100": users.filter(gender__iexact="Мужской", age__gt=100).count()
            },
            "female": {
                "under_18": users.filter(gender__iexact="Женский", age__lt=18).count(),
                "18_25": users.filter(gender__iexact="Женский", age__gte=18, age__lte=25).count(),
                "26_40": users.filter(gender__iexact="Женский", age__gte=26, age__lte=40).count(),
                "41_60": users.filter(gender__iexact="Женский", age__gte=41, age__lte=60).count(),
                "61_100": users.filter(gender__iexact="Женский", age__gte=61, age__lte=100).count(),
                "over_100": users.filter(gender__iexact="Женский", age__gt=100).count()
            }
        }

        # Статистика по очкам за квиз
        total_points = users.aggregate(total_points=Sum('quiz_points'))['total_points'] or 0
        avg_points = round(users.aggregate(avg_points=Avg('quiz_points'))['avg_points'], 1) if users.exists() else 0

        # Статистика по использованным функциям
        functions_stats = {}
        for user in users:
            if isinstance(user.used_functions, list):
                used_functions = user.used_functions
            else:
                used_functions = []
            for func in used_functions:
                if func in functions_stats:
                    functions_stats[func] += 1
                else:
                    functions_stats[func] = 1

        # Статистика по типу пользователя
        type_stats = users.values('is_registered', 'is_web_user').annotate(count=Count('id'))

        # Полные данные пользователей для региона
        user_data = TelegramUserSerializer(users, many=True).data

        data = {
            "region": region_name,
            "total_users": total_users,
            "gender_distribution": {
                "male_percentage": male_percentage,
                "female_percentage": female_percentage,
            },
            "age_distribution": {
                "average_age": average_age,
                "age_groups": age_groups,
            },
            "children_stats": {
                "distribution": children_stats,
                "total_children": total_children,
                "average_children_per_user": avg_children,
            },
            "benefits_stats": benefits_stats,
            "marital_status": {
                "distribution": marital_status_distribution,
                "average_age_by_status": marital_status_avg_age,
            },
            "age_gender_distribution": age_gender_distribution,
            "points_stats": {
                "total_points": total_points,
                "average_points": avg_points,
            },
            "functions_stats": functions_stats,
            "type_stats": list(type_stats),
            "last_activities": user_data  # Полные данные пользователей для региона
        }
        return Response(data)

class CountryAPIView(APIView):
    def get(self, request):
        # Получение всех пользователей
        users = TelegramUser.objects.all()
        if not users.exists():
            return Response({'error': 'Нет данных о пользователях'}, status=status.HTTP_404_NOT_FOUND)

        total_users = users.count()

        # Распределение по полу
        male_count = users.filter(gender__iexact="Мужской").count()
        female_count = users.filter(gender__iexact="Женский").count()
        male_percentage = round((male_count / total_users * 100), 1) if total_users > 0 else 0
        female_percentage = round((female_count / total_users * 100), 1) if total_users > 0 else 0

        # Возрастное распределение
        age_groups = {
            "under_18": users.filter(age__lt=18).count(),
            "18_25": users.filter(age__gte=18, age__lte=25).count(),
            "26_40": users.filter(age__gte=26, age__lte=40).count(),
            "41_60": users.filter(age__gte=41, age__lte=60).count(),
            "61_100": users.filter(age__gte=61, age__lte=100).count(),
            "over_100": users.filter(age__gt=100).count()
        }
        average_age = round(users.aggregate(Avg('age'))['age__avg'], 1) if users.exists() else "Нет данных"

        # Статистика по детям
        children_stats = {}
        for i in range(21):  # Категории от 0 до 20 детей
            children_stats[f"{i}_children"] = users.annotate(children_as_int=Cast('children', IntegerField())).filter(
                children_as_int=i).count()

        total_children = users.annotate(children_as_int=Cast('children', IntegerField())).aggregate(
            total=Sum('children_as_int')
        )['total'] or 0

        avg_children = round(users.annotate(children_as_int=Cast('children', IntegerField())).aggregate(
            avg=Avg('children_as_int')
        )['avg'], 1) if users.exists() else 0

        # Социальные пособия
        benefits_stats = {
            "receiving_benefits": users.filter(benefits__iexact="Да").count(),
            "average_age_benefit_recipients": round(users.filter(benefits__iexact="Да").aggregate(Avg('age'))[
                                                    'age__avg'], 1) if users.filter(benefits__iexact="Да").exists() else "Нет данных",
            "percentage_with_children": round((users.filter(benefits__iexact="Да").exclude(
                children="0").count() / total_users * 100), 1) if total_users > 0 else 0,
        }

        # Категории семейного положения
        valid_marital_statuses = ["Холост/Не замужем", "Женат/Замужем", "В разводе", "Вдовец/Вдова"]
        marital_status_distribution = {
            status: users.filter(marital_status=status).count()
            for status in valid_marital_statuses
        }
        marital_status_distribution["Не указано"] = users.filter(marital_status__isnull=True).count()
        marital_status_avg_age = {
            status: round(users.filter(marital_status=status).aggregate(avg_age=Avg('age'))['avg_age'], 1) or "Нет данных"
            for status in valid_marital_statuses
        }

        # Распределение по возрасту и полу
        age_gender_distribution = {
            "male": {
                "under_18": users.filter(gender__iexact="Мужской", age__lt=18).count(),
                "18_25": users.filter(gender__iexact="Мужской", age__gte=18, age__lte=25).count(),
                "26_40": users.filter(gender__iexact="Мужской", age__gte=26, age__lte=40).count(),
                "41_60": users.filter(gender__iexact="Мужской", age__gte=41, age__lte=60).count(),
                "61_100": users.filter(gender__iexact="Мужской", age__gte=61, age__lte=100).count(),
                "over_100": users.filter(gender__iexact="Мужской", age__gt=100).count()
            },
            "female": {
                "under_18": users.filter(gender__iexact="Женский", age__lt=18).count(),
                "18_25": users.filter(gender__iexact="Женский", age__gte=18, age__lte=25).count(),
                "26_40": users.filter(gender__iexact="Женский", age__gte=26, age__lte=40).count(),
                "41_60": users.filter(gender__iexact="Женский", age__gte=41, age__lte=60).count(),
                "61_100": users.filter(gender__iexact="Женский", age__gte=61, age__lte=100).count(),
                "over_100": users.filter(gender__iexact="Женский", age__gt=100).count()
            }
        }

        # Статистика по очкам за квиз
        total_points = users.aggregate(total_points=Sum('quiz_points'))['total_points'] or 0
        avg_points = round(users.aggregate(avg_points=Avg('quiz_points'))['avg_points'], 1) if users.exists() else 0

        # Статистика по использованным функциям
        functions_stats = {}
        for user in users:
            if isinstance(user.used_functions, list):
                used_functions = user.used_functions
            else:
                used_functions = []
            for func in used_functions:
                if func in functions_stats:
                    functions_stats[func] += 1
                else:
                    functions_stats[func] = 1

        # Статистика по типу пользователя
        type_stats = users.values('is_registered', 'is_web_user').annotate(count=Count('id'))

        # Полные данные пользователей
        user_data = TelegramUserSerializer(users, many=True).data

        data = {
            "country": "Все регионы",
            "total_users": total_users,
            "gender_distribution": {
                "male_percentage": male_percentage,
                "female_percentage": female_percentage,
            },
            "age_distribution": {
                "average_age": average_age,
                "age_groups": age_groups,
            },
            "children_stats": {
                "distribution": children_stats,
                "total_children": total_children,
                "average_children_per_user": avg_children,
            },
            "benefits_stats": benefits_stats,
            "marital_status": {
                "distribution": marital_status_distribution,
                "average_age_by_status": marital_status_avg_age,
            },
            "age_gender_distribution": age_gender_distribution,
            "points_stats": {
                "total_points": total_points,
                "average_points": avg_points,
            },
            "functions_stats": functions_stats,
            "type_stats": list(type_stats),
            "all_users": user_data  # Полные данные пользователей
        }
        return Response(data)


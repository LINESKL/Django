from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from crm.models import TelegramUser
from django.db.models import Avg, Count, IntegerField, Sum
from django.db.models.functions import Cast
from django.utils.dateparse import parse_date
from django.db.models.functions import TruncDay
from django.db.models.functions import ExtractWeekDay

class CountryStatisticsAPIView(APIView):
    def get(self, request):
        start_date = parse_date(request.query_params.get("start_date"))
        end_date = parse_date(request.query_params.get("end_date"))
        region = request.query_params.get("region")

        if start_date and end_date:
            users = users.filter(created_at__range=(start_date, end_date))
        if region:
            users = users.filter(region__iexact=region)
        # Получение всех пользователей
        users = TelegramUser.objects.all()
        if not users.exists():
            return Response({'error': 'Нет данных о пользователях'}, status=status.HTTP_404_NOT_FOUND)

        total_users = users.count()

        # Распределение по полу
        male_count = users.filter(gender__iexact="Мужской").count()
        female_count = users.filter(gender__iexact="Женский").count()
        male_percentage = (male_count / total_users * 100) if total_users > 0 else 0
        female_percentage = (female_count / total_users * 100) if total_users > 0 else 0

        # Возрастное распределение
        age_groups = {
            "under_18": users.filter(age__lt=18).count(),
            "18_25": users.filter(age__gte=18, age__lte=25).count(),
            "26_40": users.filter(age__gte=26, age__lte=40).count(),
            "41_60": users.filter(age__gte=41, age__lte=60).count(),
            "61_100": users.filter(age__gte=61, age__lte=100).count(),
            "over_100": users.filter(age__gt=100).count()
        }
        average_age = users.aggregate(Avg('age'))['age__avg'] or "Нет данных"

        # Статистика по детям
        children_stats = {}
        for i in range(21):  # Категории от 0 до 20 детей
            children_stats[f"{i}_children"] = users.annotate(children_as_int=Cast('children', IntegerField())).filter(
                children_as_int=i).count()

        total_children = users.annotate(children_as_int=Cast('children', IntegerField())).aggregate(
            total=Sum('children_as_int')
        )['total'] or 0

        avg_children = users.annotate(children_as_int=Cast('children', IntegerField())).aggregate(
            avg=Avg('children_as_int')
        )['avg'] or 0

        # Социальные пособия
        benefits_stats = {
            "receiving_benefits": users.filter(benefits__iexact="Да").count(),
            "average_age_benefit_recipients": users.filter(benefits__iexact="Да").aggregate(Avg('age'))[
                                                  'age__avg'] or "Нет данных",
            "percentage_with_children": (users.filter(benefits__iexact="Да").exclude(
                children="0").count() / total_users * 100) if total_users > 0 else 0,
        }

        # Формирование итогового ответа
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
        }
        return Response(data)

class GenderDistributionAPIView(APIView):
    def get(self, request, region_name):
        users = TelegramUser.objects.filter(region=region_name)
        if not users.exists():
            return Response({'error': 'Регион не найден'}, status=status.HTTP_404_NOT_FOUND)

        total_users = users.count()
        male_count = users.filter(gender__iexact="Мужской").count()
        female_count = users.filter(gender__iexact="Женский").count()
        male_percentage = (male_count / total_users * 100) if total_users > 0 else 0
        female_percentage = (female_count / total_users * 100) if total_users > 0 else 0

        data = {
            "region": region_name,
            "gender_distribution": {
                "male_percentage": male_percentage,
                "female_percentage": female_percentage,
            },
        }
        return Response(data)


class AgeDistributionAPIView(APIView):
    def get(self, request, region_name):
        users = TelegramUser.objects.filter(region=region_name)
        if not users.exists():
            return Response({'error': 'Регион не найден'}, status=status.HTTP_404_NOT_FOUND)

        age_groups = {
            "under_18": users.filter(age__lt=18).count(),
            "18_25": users.filter(age__gte=18, age__lte=25).count(),
            "26_40": users.filter(age__gte=26, age__lte=40).count(),
            "41_60": users.filter(age__gte=41, age__lte=60).count(),
            "61_100": users.filter(age__gte=61, age__lte=100).count(),
            "over_100": users.filter(age__gt=100).count()
        }
        average_age = users.aggregate(Avg('age'))['age__avg'] or "Нет данных"

        data = {
            "region": region_name,
            "age_distribution": {
                "average_age": average_age,
                "age_groups": age_groups,
            },
        }
        return Response(data)


class ChildrenStatsAPIView(APIView):
    def get(self, request, region_name):
        users = TelegramUser.objects.filter(region=region_name)
        if not users.exists():
            return Response({'error': 'Регион не найден'}, status=status.HTTP_404_NOT_FOUND)

        children_stats = {}
        for i in range(21):  # Категории от 0 до 20 детей
            children_stats[f"{i}_children"] = users.annotate(children_as_int=Cast('children', IntegerField())).filter(
                children_as_int=i).count()

        total_children = users.annotate(children_as_int=Cast('children', IntegerField())).aggregate(
            total=Sum('children_as_int')
        )['total'] or 0

        avg_children = users.annotate(children_as_int=Cast('children', IntegerField())).aggregate(
            avg=Avg('children_as_int')
        )['avg'] or 0

        data = {
            "region": region_name,
            "children_stats": {
                "distribution": children_stats,
                "total_children": total_children,
                "average_children_per_user": avg_children,
            },
        }
        return Response(data)


class BenefitsStatsAPIView(APIView):
    def get(self, request, region_name):
        users = TelegramUser.objects.filter(region=region_name)
        if not users.exists():
            return Response({'error': 'Регион не найден'}, status=status.HTTP_404_NOT_FOUND)

        benefits_stats = {
            "receiving_benefits": users.filter(benefits__iexact="Да").count(),
            "average_age_benefit_recipients": users.filter(benefits__iexact="Да").aggregate(Avg('age'))[
                                                  'age__avg'] or "Нет данных",
            "percentage_with_children": (users.filter(benefits__iexact="Да").exclude(
                children="0").count() / users.count() * 100) if users.count() > 0 else 0,
        }

        data = {
            "region": region_name,
            "benefits_stats": benefits_stats,
        }
        return Response(data)

class MaritalStatsAPIView(APIView):
    def get(self, request, region_name):
        # Фильтрация пользователей по региону
        users = TelegramUser.objects.filter(region=region_name)
        if not users.exists():
            return Response({'error': 'Регион не найден'}, status=status.HTTP_404_NOT_FOUND)

        # Категории семейного положения
        valid_marital_statuses = ["Холост/Не замужем", "Женат/Замужем", "В разводе", "Вдовец/Вдова"]

        # Распределение по категориям
        marital_status_distribution = {
            status: users.filter(marital_status=status).count()
            for status in valid_marital_statuses
        }
        marital_status_distribution["Не указано"] = users.filter(marital_status__isnull=True).count()

        # Средний возраст в каждой группе семейного положения
        marital_status_avg_age = {
            status: users.filter(marital_status=status).aggregate(avg_age=Avg('age'))['avg_age'] or "Нет данных"
            for status in valid_marital_statuses
        }

        data = {
            "region": region_name,
            "marital_status": {
                "distribution": marital_status_distribution,
                "average_age_by_status": marital_status_avg_age,
            },
        }
        return Response(data)

class AgeGenderDistributionAPIView(APIView):
    def get(self, request, region_name):
        users = TelegramUser.objects.filter(region=region_name)
        if not users.exists():
            return Response({'error': 'Регион не найден'}, status=status.HTTP_404_NOT_FOUND)

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

        data = {
            "region": region_name,
            "age_gender_distribution": age_gender_distribution
        }
        return Response(data)

class UserFunctionsAPIView(APIView):
    def get(self, request, region_name=None):
        # Фильтрация пользователей по региону
        users = TelegramUser.objects.all()
        if region_name:
            users = users.filter(region__iexact=region_name)

        if not users.exists():
            return Response({"error": "Нет данных о пользователях"}, status=status.HTTP_404_NOT_FOUND)

        # Подготовка данных для таблицы
        functions_data = []
        for user in users:
            # Проверка: если used_functions строка, преобразуем её в список
            if isinstance(user.used_functions, str):
                used_functions = [func.strip() for func in user.used_functions.split(",")]
            else:
                used_functions = user.used_functions or []

            for func in used_functions:
                functions_data.append({
                    "user_id": user.user_id,
                    "username": user.username or "Аноним",
                    "region": user.region or "Не указано",
                    "function_name": func,
                    "timestamp": user.last_activity.strftime("%d.%m.%Y, %H:%M:%S") if user.last_activity else "Не указано"
                })

        if not functions_data:
            return Response({"error": "Нет данных о использованных функциях"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"functions": functions_data})



# Analitica
class TrendsAPIView(APIView):
    def get(self, request):
        # Получаем параметры
        start_date_str = request.query_params.get("start_date")
        end_date_str = request.query_params.get("end_date")

        # Проверяем, что параметры существуют
        start_date = parse_date(start_date_str) if start_date_str else None
        end_date = parse_date(end_date_str) if end_date_str else None

        users = TelegramUser.objects.all()

        # Применяем фильтрацию, если даты заданы
        if start_date and end_date:
            users = users.filter(last_activity__range=(start_date, end_date))

        # Группировка по дням
        trends = users.annotate(day=TruncDay('last_activity')).values('day').annotate(
            count=Count('id')
        ).order_by('day')

        return Response({"trends": list(trends)})


class RegionalComparisonAPIView(APIView):
    def get(self, request):
        users = TelegramUser.objects.all()
        # Сравнение по регионам
        regional_data = users.values('region').annotate(
            total_users=Count('id')
        ).order_by('-total_users')

        return Response({"regions": list(regional_data)})


class AnomalyDetectionAPIView(APIView):
    def get(self, request):
        users = TelegramUser.objects.all()

        trends = users.annotate(day=TruncDay('last_activity')).values('day').annotate(
            count=Count('id')
        )

        counts = [t['count'] for t in trends]
        avg_count = sum(counts) / len(counts) if counts else 0
        std_dev = (sum((x - avg_count) ** 2 for x in counts) / len(counts)) ** 0.5 if counts else 0

        anomalies = [t for t in trends if t['count'] > avg_count + 2 * std_dev]

        return Response({"anomalies": anomalies})

class WeekdayActivityAPIView(APIView):
    def get(self, request):
        weekday_stats = TelegramUser.objects.annotate(weekday=ExtractWeekDay('last_activity')).values('weekday').annotate(total=Count('id')).order_by('weekday')
        days_mapping = ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
        data = [{'day': days_mapping[day['weekday'] - 1], 'total': day['total']} for day in weekday_stats]
        return Response({'weekdays': data})

class SegmentationAPIView(APIView):
    def get(self, request):
        gender_stats = TelegramUser.objects.values('gender').annotate(total=Count('id'))
        age_groups = {

            '18-25': TelegramUser.objects.filter(age__gte=18, age__lte=25).count(),
            '26-40': TelegramUser.objects.filter(age__gte=26, age__lte=40).count(),
            '41-60': TelegramUser.objects.filter(age__gte=41, age__lte=60).count(),
            '60+': TelegramUser.objects.filter(age__gte=60).count(),
        }
        return Response({'gender': list(gender_stats), 'age_groups': age_groups})

import datetime
import json
from json import JSONDecodeError

from django.db.models import Q
from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import News
from .serializers import NewsSerializer


def validate_parameters(json_request, valid_keys_json):
    """
    validate the mandatory key name, key value is present or not
    :param json_request:
    :param valid_keys_json:
    :return:
    """
    response = {}
    try:
        error = False
        provided_keys = json_request.keys()
        for key in valid_keys_json:
            if key not in provided_keys:
                error = True
                response.update({
                    key: {"error": "Key " + key + " is not available"}
                })
            else:
                if (len(str(json_request[key]).strip())) == 0:
                    error = True
                    response.update({
                        key: {"error": "Value of key " + key + " is not available "}
                    })
        if error:
            return True, response
        else:
            return False, response
    except Exception as ex:
        response.update({
            "error": str(ex)
        })
        return True, response


class NewsAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        list all the news
        :param request:
        :return:
        """
        queryset = News.objects.all()
        serializer = NewsSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Takes the details of news and inserts it in database",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the news'),
                'details': openapi.Schema(type=openapi.TYPE_STRING, description='Details of the news'),
                'date': openapi.Schema(type=openapi.TYPE_STRING, description='Date of the news'),
                'news_from': openapi.Schema(type=openapi.TYPE_STRING, description='Origin of the news'),
                'news_url': openapi.Schema(type=openapi.TYPE_STRING, description='URL of the news')
            }
        )
    )
    def post(self, request):
        """
        Store the individual news detail
        :param request:
        :return:
        """

        try:
            data = json.loads(request.body)
            valid_keys = ["title", "details", "date", "news_from", "news_url"]
            is_errors, response = validate_parameters(data, valid_keys)
            if is_errors:
                return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)
            else:
                title = data.get("title")
                details = data.get("details")
                date = data.get("date")
                news_from = data.get("news_from")
                news_url = data.get("news_url")
                date = datetime.datetime.strptime(date, "%Y-%m-%d")
                News.objects.create(title=title.strip(), details=details.strip(), news_from=news_from.strip(),
                                    news_url=news_url.strip(), date=date)
                return JsonResponse({"message": "Record created!"}, status=status.HTTP_201_CREATED)
        except JSONDecodeError as e:
            return JsonResponse({"error": "Invalid Json"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return JsonResponse({"error": "Valid format for date is YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NewsDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, id):
        """
        Get the record from the db
        :param id: pk of news row
        :return:
        """
        try:
            return True, News.objects.get(id=id)
        except News.DoesNotExist as e:
            return False, {"error": "record  not exist"}

    def get(self, request, id=None):
        """
        Get the record from the db and return the detail
        :param request:
        :param id: pk of news in db
        :return:
        """
        try:
            success_status, result = self.get_object(id)
            if success_status:
                serializer = NewsSerializer(result)
                return Response(serializer.data)
            else:
                return JsonResponse(result, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        """
        Updated the existing record
        :param request:
        :param id: pk of news record
        :return:
        """
        try:
            data = json.loads(request.body)
            valid_keys = ["title", "details", "date", "news_from", "news_url"]
            is_errors, response = validate_parameters(data, valid_keys)
            if is_errors:
                return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)
            else:
                success_status, instance = self.get_object(id)
                if success_status:
                    title = data.get("title")
                    details = data.get("details")
                    date = data.get("date")
                    news_from = data.get("news_from")
                    news_url = data.get("news_url")
                    date = datetime.datetime.strptime(date, "%Y-%m-%d")
                    instance.title = title.strip()
                    instance.details = details.strip()
                    instance.news_from = news_from.strip()
                    instance.news_url = news_url.strip()
                    instance.date = date
                    instance.save()
                    return JsonResponse({"message": "Record Updated!"}, status=status.HTTP_200_OK)
                else:
                    return JsonResponse(instance, status=status.HTTP_404_NOT_FOUND)
        except JSONDecodeError as e:
            return JsonResponse({"error": "Invalid Json"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return JsonResponse({"error": "Valid format for date is YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        """
        Deleting the news row from the db
        :param request:
        :param id: pk of news row
        :return:
        """
        try:
            success_status, instance = self.get_object(id)
            if success_status:
                instance.delete()
                return JsonResponse({"message": "Record deleted!"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return JsonResponse(instance, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def search_news_by_keyword(request):
    """
    Search the news by keyword
    :param request:
    :return:
    """
    try:
        data = json.loads(request.body)
        valid_keys = ["keyword"]
        is_errors, response = validate_parameters(data, valid_keys)
        if is_errors:
            return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            keyword = data.get("keyword")
            news_obj = News.objects.filter(Q(title__contains=keyword) | Q(details__contains=keyword))
            if news_obj:
                serializer = NewsSerializer(news_obj, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return JsonResponse({"message": "No data available!"}, status=status.HTTP_200_OK)
    except JSONDecodeError as e:
        return JsonResponse({"error": "Invalid Json"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

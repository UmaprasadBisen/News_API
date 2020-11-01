import datetime
import json
from json import JSONDecodeError

import newspaper
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

    @swagger_auto_schema(
        operation_description="List all the news.",
        responses={200: '[{"id":xx,"title":xxx,"details":xxx,"date":xx,"news_from":xx,"news_url":xx}]'}

    )
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
        operation_description="Add single record for news",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the news'),
                'details': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the news'),
                'date': openapi.Schema(type=openapi.TYPE_STRING,
                                       description='Published date of the news in YYY-MM-DD format'),
                'news_from': openapi.Schema(type=openapi.TYPE_STRING, description='Source of the news'),
                'news_url': openapi.Schema(type=openapi.TYPE_STRING, description='URL for the news')
            }
        ),
        responses={201: '{"message": "Record created!"}'}

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
                if News.objects.filter(title=title, news_from=news_from, news_url=news_url).exists():
                    return JsonResponse({"error": "News already exists!"}, status=status.HTTP_400_BAD_REQUEST)
                else:
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

    @swagger_auto_schema(
        operation_description="Detail of single news.",
        responses={200: '{"id":xx,"title":xxx,"details":xxx,"date":xx,"news_from":xx,"news_url":xx}'}
    )
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
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return JsonResponse(result, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Update the existing news",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the news'),
                'details': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the news'),
                'date': openapi.Schema(type=openapi.TYPE_STRING,
                                       description='Published date of the news in YYY-MM-DD format'),
                'news_from': openapi.Schema(type=openapi.TYPE_STRING, description='Source of the news'),
                'news_url': openapi.Schema(type=openapi.TYPE_STRING, description='URL for the news')
            }
        ),
        responses={200: '{"message": "Record Updated!"}'}

    )
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

    @swagger_auto_schema(
        operation_description="Delete the existing news",
        responses={204: '{"message": "Record deleted!"}'}

    )
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


class FilterNews(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Search the news by keywords in title or description",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'keyword': openapi.Schema(type=openapi.TYPE_STRING, description='Keyword for searching')
            }
        ),
        responses={200: '[{"id":xx,"title":xxx,"details":xxx,"date":xx,"news_from":xx,"news_url":xx}]'}
    )
    def post(self, request):
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


class ScrapedNews(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Scrape the news and insert them if and only if they have published date.",

        responses={201: '{"message": "Records created!"}'}
    )
    def post(self, request):
        """
        insert the bulk news from the websites
        reference for scrapping
        https://holwech.github.io/blog/Automatic-news-scraper/

        :param request:
        :return:
        """
        try:
            # Loads the JSON files with news sites
            with open('NewsPapers.json') as data_file:
                companies = json.load(data_file)
            #     As library execute for many news so need to limit
            LIMIT = 5
            for company, value in companies.items():
                paper = newspaper.build(value['link'], memoize_articles=False)
                count = 0
                for content in paper.articles:
                    count = count + 1
                    if count > LIMIT:
                        break
                    try:
                        content.download()
                        content.parse()
                    except Exception as e:
                        continue
                    # Again, for consistency, if there is no found publish date the article will be skipped.
                    # After 5 downloaded articles from the same newspaper without publish date,
                    # the company will be skipped.
                    if content.publish_date is None:
                        continue

                    # Comparing the article publish date and current date
                    # Proceed only when both date are same as per the problem statement
                    publish_date = content.publish_date
                    if datetime.datetime.now().strftime("%d-%m-%Y") == publish_date.strftime("%d-%m-%Y"):
                        # check if news already exist or not in db
                        title = content.title
                        details = content.text
                        news_from = company
                        news_url = content.url
                        if not News.objects.filter(title=title, news_from=news_from, news_url=news_url).exists():
                            News.objects.create(title=title.strip(), details=details.strip(),
                                                news_from=news_from.strip(),
                                                news_url=news_url.strip(), date=publish_date)

            return JsonResponse({"message": "Records created!"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return JsonResponse({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

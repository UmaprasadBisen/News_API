from django.urls import path

from news_api_app.views import NewsAPIView, NewsDetailsAPIView, search_news_by_keyword

urlpatterns = [
    path('news/', NewsAPIView.as_view()),
    path('news/<int:id>/', NewsDetailsAPIView.as_view()),
    path('news-filter/', search_news_by_keyword)
]

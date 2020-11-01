from django.urls import path, include

from news_api_app.views import NewsAPIView, NewsDetailsAPIView, FilterNews, ScrapedNews

urlpatterns = [
    path('news/', NewsAPIView.as_view()),
    path('bulk-news/', ScrapedNews.as_view()),
    path('news/<int:id>/', NewsDetailsAPIView.as_view()),
    path('news-filter/', FilterNews.as_view())

]

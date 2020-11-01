from django.urls import path

from news_api_app.views import NewsAPIView, NewsDetailsAPIView, search_news_by_keyword, save_scrapped_news

urlpatterns = [
    path('news/', NewsAPIView.as_view()),
    path('bulk-news/', save_scrapped_news),
    path('news/<int:id>/', NewsDetailsAPIView.as_view()),
    path('news-filter/', search_news_by_keyword)
]

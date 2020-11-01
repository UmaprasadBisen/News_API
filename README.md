# News_API
### Problem Statement
1. Need to create web API for the listing of news and searching news with keywords
2. Need to write a small scraper for below JSON links and get the news on one API call for current
date and store it in the table in this format (Id, Date, Title, Details, New From (CNN, Times,
etc.) and URL of News)
3. You need to ensure that no duplicate news gets entered in the table via scraper
4. News can be searched via any keyword in title or in detail field
5. Also, we will need API to delete any news by passing ID and we need separate API to update
the news details
6. Write a small authentication mechanism which will give JWT token and this token will be used
to call any other API’s. If the token gets expired, then no result with be shown
```
{
  "Washington Post": {
  "link": "washingtonpost.com"
  },
  "CNN": {
  "link": "http://edition.cnn.com/"
  },
  "Time": {
  "link": "http://time.com/"
  },
  "QZ": {
  "link": "https://qz.com/"
  },
  "Slashdot": {
  "link": "https://slashdot.org/"
  }
}
```
## Setup

### Install required packages:
```bash
pip install -r requirement.txt
```

### setup postgresql DB credentials using one of the  following method
#### 1. creating .env file

-add .env file with the following content in the same folder as setting.py
```
DB_USERNAME=xxx
DB_PASSWORD=xxxx
DB_PORT=xxxx
DB_NAME=xxxx
DB_HOST=xx.xx.xx.xx
```
#### 2. Export the environment variable
```bash
export DB_USERNAME=xxx
export DB_PASSWORD=xxxx
export DB_PORT=xxxx
export DB_NAME=xxxx
export DB_HOST=xx.xx.xx.xx
```

### Perform database migration by executing the following:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Create superuser for getting JWT Token
```bash
python manage.py createsuperuser
```
provide the info like username, email and password .
This can be used to exchange the access token and refresh token


### Run Development Server

```bash
python manage.py runserver
```

### Detailed API Documentation
```
http:\\127.0.0.1:8000\swagger\
```

### Available endpoints are 
```
POST /api/token/
POST /api/token/refresh/
POST /bulk-news/
POST /news-filter/
GET /news/
POST /news/
GET /news/{id}/
PUT /news/{id}/
DELETE /news/{id}/
```

### Third Party Library for scraping news 
newspaper3k==0.2.8 

### Basic Architecture
![alt text](/architechture.png)


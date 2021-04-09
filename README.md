# Django App

Django app that renders the data using Vue.js and redis. It downloads new Bhav equity file from [link](https://www.bseindia.com/markets/MarketInfo/BhavCopy.aspx) daily at 6 PM IST.

## Installation
```bash
git clone https://github.com/pssukhwani/market-info.git
cd ~/market_info
pip install -r requirements.txt
```
Install Redis:
```bash
For mac users: brew update && brew install redis
For Debian Linux users: sudo apt-get install redis-server
```

## local settings:
Create Local settings file under:
```bash
cd ~/market_info/market_info/
touch custom_settings.py
nano custom_settings.py
```
Add the following:
```
from urllib.parse import urlparse

DEBUG = True
ALLOWED_HOSTS = ["*"]
REDIS_URL = urlparse('http://localhost:6379/')
LOCAL_HOST = 'http://localhost:8000'
SECURE_HSTS_SECONDS = 0
SECURE_SSL_REDIRECT = False
```

## Run Server
```bash
brew services start redis # Start Redis Server
python manage.py runserver # Start Django Server
```

Open http://localhost:8000/home

1) Install Scrapy Splash Docker
    http://splash.readthedocs.io/en/stable/install.html
    
2) Install Firefox 47.02.
    a) Install SQLite package
    b) check if it shows up or not
    https://addons.mozilla.org/en-US/firefox/addon/sqlite-manager/
    
3) install all python packages
    pip install pysqlite3
    pip install selenium
    pip install scrapy
    pip install plotly
    pip install pandas
    pip install lxml
    pip install hashlib
    pip install scrapy_splash
    pip install --upgrade twisted
    pip install dash
    pip install dash-renderer
    pip install dash-html-components
    pip install dash-core-components
    pip install plotly --upgrade  
    pip install numpy
    
4) Install other packakes if you get runtime error of unsupported library  (search on google)

5) Unzip SmartMonitoring in some folder

6) Run docker service by going to Splash subdirectory and invoking ".\SmartMonitoring\Splash>splash.bat"

7) Run the scraper my invoking 'run_all.py' by going to ".\SmartMonitoring\SmartMonitoring>run_all.py"

8) You can change the scraping dates by changing below parameter in '.\SmartMonitoring\SmartMonitoring\timedecorator.py'

START_DATE_OFFSET = 5 #(relative to today)
END_DATE_OFFSET = 1

9) Default route list at ".\SmartMonitoring\SmartMonitoring\spiders\resources\default_routes.xml". Change it as per your need.

10) Web interface to pull the data and search and run is at ".\SmartMonitoring\SmartMonitoring>runui.py"

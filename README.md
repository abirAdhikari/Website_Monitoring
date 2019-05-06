## Website_Monitoring

## Liscensing Information: READ LISCENCE


**Author & Contributor List **
-----------
Abirlal Adhikari

All bugs and fixes can be reported to the comments.

**Files and Folders
--------
```
/Monitor:

  /Splash:
  
      Splash.bat

  /Monitor:
  
  chromedriver.exe
  
  hyperlink.txt 
  
  Proxy_List.txt  

  competitivedataitem.py  
  
  __init__.py       
  
  timedecorator.py
  
  competitivedata.py    
  
  items.py     
  
  run_server.py   
  
  urlgenerator.py
  
  example_cell_coloring.py  
  
  middlewares.py   
  
  example_hyperlinks.py     
 
  scrapyutils.py
  
  hawkeyeutils.py           
  
  pipelines.py     
  
  settings.py
  
  README.txt 
  
  pip_install.txt
  
  /spiders:
  
    ahataxis.py           
    
    makemytrip.py   
    
    chromedriver.exe  
    
    hippocabs.py  
    
    mytaxiindia.py  
    
    wiwigo.py
    
    getmecab.py       
    
    __init__.py   
    
    onewaycab.py
    /resources:
    
      served_cities_mytaxiindia.json
    /sqlDB:
    
    /db
```
### How to run the file
-----
While you clone the whole package, you need to populate resources folder with relevant routes information for all the services. An example for mytaxiindia is given. 

To generate the scraped valued to a file in sqlDB folder, first run the ```run_server.py``` and open a dash board in your browser at ```localhost:8052``` and play with the UI.

For some websites which uses javascript you need to install docker and run the splash.bat file first before scraping.


### Bugs
-----
Makemytrip scrapy is not working currently as the urlgenerator for mmt is not updated. Issue is occuring due to some changes done in the mmt website. Patch will be updated soon.
####Change all the names Hawkeye to Monitor


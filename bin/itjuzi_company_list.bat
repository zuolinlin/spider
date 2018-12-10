@echo off
rem echo press any key to start
rem pause
echo running....
cd ..
scrapy crawl itjuzi_api_company_list -s DOWNLOAD_DELAY=1 -s CLOSESPIDER_TIMEOUT=1800 -s LOG_FILE=/logs/itjuzi_api_company_list_%date:~0,4%-%date:~5,2%-%date:~8,2%.log
rem echo press any key to exit
rem pause
exit
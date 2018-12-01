@echo off
rem echo press any key to start
rem pause
echo running....
cd ..
scrapy crawl itjuzi_api_company_info -s DOWNLOAD_DELAY=1 -s CLOSESPIDER_TIMEOUT=18000 -s LOG_FILE=/logs/itjuzi_api_company_info_1-5.log
rem echo press any key to exit
rem pause
exit
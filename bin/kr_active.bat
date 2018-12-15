@echo off
rem echo press any key to start
rem pause
echo running....
cd ..
scrapy crawl kr_active -s DOWNLOAD_DELAY=1 -s CLOSESPIDER_TIMEOUT=10800 -s LOG_FILE=/logs/kr_active_%date:~0,4%-%date:~5,2%-%date:~8,2%.log
rem echo press any key to exit
rem pause
exit
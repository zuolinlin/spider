@echo off
rem echo press any key to start
rem pause
echo running....
cd ..
scrapy crawl chinaventure_active -s CLOSESPIDER_TIMEOUT=3600 -s LOG_FILE=/logs/chinaventure_active_%date:~0,4%-%date:~5,2%-%date:~8,2%.log
rem echo press any key to exit
rem pause
exit
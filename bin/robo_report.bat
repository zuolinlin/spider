@echo off
rem echo press any key to start
rem pause
echo running....
cd ..
scrapy crawl robo_report -s LOG_FILE=/logs/robo_report.log
echo press any key to exit
pause
exit
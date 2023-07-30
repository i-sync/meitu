#! /bin/bash

cd /var/www/meitu/meitu

ts=`date "+%F %T"`

nohup /usr/local/bin/scrapy crawl beauty > "nohup/nohup-beauty-$ts.out" 2>&1 &

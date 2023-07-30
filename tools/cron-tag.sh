#! /bin/bash

cd /var/www/meitu/meitu

ts=`date "+%F %T"`

nohup /usr/local/bin/scrapy crawl tag > "nohup/nohup-tag-$ts.out" 2>&1 &

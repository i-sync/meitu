#! /bin/bash

cd /var/www/meitu/meitu

ts=`date "+%F %T"`

nohup /usr/local/bin/scrapy crawl album > "nohup/nohup-album-$ts.out" 2>&1 &

#! /bin/bash

cd /var/www/meitu/meitu

ts=`date "+%F %T"`

nohup /usr/local/bin/scrapy crawl model > "nohup/nohup-model-$ts.out" 2>&1 &

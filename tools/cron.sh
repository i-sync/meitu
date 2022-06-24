#! /bin/bash

cd /var/www/meitu/meitu

ts=`date +%s`

nohup /usr/local/bin/scrapy crawl album > "nohup-$ts.out" 2>&1 &

echo "sleep 180, and then regenerate sitemap."
sleep 180
cd /var/www/meitu/tools

/usr/bin/python3 generate-sitemap.py
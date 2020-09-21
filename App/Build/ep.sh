#!/bin/bash
sleep 20
python3 migrations.py -user=postgres -passwd=postgres -host=postgres -port=5432 -dbname=AppFollow
sleep 5
python3 main.py -user=postgres -passwd=postgres -host=postgres -port=5432 -dbname=AppFollow -max-news=30 -timeout=30
#!/bin/bash
git pull
python3 main.py
git commit -am "update-data"
git push

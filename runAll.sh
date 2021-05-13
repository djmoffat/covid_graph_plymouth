#!/bin/bash
git pull
/usr/local/bin/python3 main.py
git add images/* index.md
git commit -m "update-data"
git push

#!/bin/bash
python3 download_xml.py
python3 parser.py
python3 upload_csv.py
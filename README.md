
# Description
This project was built that has derived from a wide variety of sources.
The aim of this project was to collate research papers from various institutions to track published research on a particular medical topic. Research papers come from all across the world so the way data is put into medical databases such as Medline varies widely.
 
I created a pipeline which downloaded xmls from a source, cleaned and used Natural Language Processing and other tools to normalize the data before uploading it to to an S3 bucket. This project utilised Python, Pandas, AWS, spaCy.

N.B. This repo consists of the final state of the app, as the original project repo was initiated as a private repo on a separate account. Therefore previous repo history (commits etc) cannot be found.

# Setup

## Requirements
User must have access to my AWS S3 bucket otherwise test_xmls can be used to for starting point.
All requirements are stored in the requirements.txt file.

## Installation 

Clone repo in terminal:
- run `git clone https://github.com/KAcodes/GlobalMedCollate.git`


Create and Activate virtual environment:
- run `python3 -m venv venv`
      `source ./venv/bin/activate`
 
Install necessary requirements:
- run  `pip3 install -r requirements.txt`

### Environment variables
AWS keys to an AWS account with S3 bucket containing the bucket are needed `.env`:
`AWS_ACCESS_KEY_ID`
`AWS_SECRET_ACCESS_KEY`


Run shell script to create csv:
- run  `bash (or other shell) run_scripts.sh`

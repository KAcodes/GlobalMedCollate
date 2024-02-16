FROM python:latest

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY institutes.csv .

RUN python3 -m spacy download en_core_web_sm 

COPY download_xml.py .
COPY parser.py .
COPY upload_csv.py .

COPY run_scripts.sh .
RUN chmod +x run_scripts.sh

CMD ["./run_scripts.sh"]
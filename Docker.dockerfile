FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip \
 && pip install -r requirements.txt \
 && python -m spacy download en_core_web_sm

EXPOSE 5000
CMD ["python", "app.py"]

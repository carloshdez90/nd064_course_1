FROM python:3.8-slim-bullseye

WORKDIR /app
COPY ./techtrends /app/

RUN python init_db.py

RUN pip install -r requirements.txt

CMD python app.py

EXPOSE 3111
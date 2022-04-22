FROM python:3.7-slim
LABEL author='Arteev Ilia' version=1

WORKDIR /app
COPY requirements.txt ./
RUN pip3 install -r requirements.txt --no-cache-dir

COPY api ./api
COPY foodgram ./foodgram
COPY recipes ./recipes
COPY users ./users
COPY manage.py ./
COPY fixtures.json ./

CMD ["gunicorn", "foodgram.wsgi:application", "--bind" , "0:8000"]


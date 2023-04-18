FROM python:3.6.6

RUN python -m venv /opt/venv
RUN /opt/venv/bin/pip install postgres
RUN /opt/venv/bin/pip install django
RUN /opt/venv/bin/pip install python-dotenv
RUN /opt/venv/bin/pip install djangorestframework

COPY socmed_aggs ./socmed_aggs
COPY speed_layer_api ./speed_layer_api
ADD manage.py .

EXPOSE 8000

CMD /opt/venv/bin/python ./manage.py runserver 0.0.0.0:8000

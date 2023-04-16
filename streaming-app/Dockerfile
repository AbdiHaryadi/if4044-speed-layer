FROM python:3.6.6

RUN python -m venv /opt/venv
RUN /opt/venv/bin/pip install kafka-python==2.0.2
RUN /opt/venv/bin/pip install requests==2.27.1

ADD main.py .
CMD ["/opt/venv/bin/python", "./main.py"]

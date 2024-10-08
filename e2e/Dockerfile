FROM python:3.13

WORKDIR /usr/local/bin

RUN pip install Flask
RUN pip install PyYAML
RUN pip install vertx-eventbus-client

COPY sourceplusplus-*.tar.gz ./sourceplusplus.tar.gz

RUN pip install sourceplusplus.tar.gz

COPY E2ETest.py .

ADD ./spp-probe.yml .

CMD ["python", "E2ETest.py"]

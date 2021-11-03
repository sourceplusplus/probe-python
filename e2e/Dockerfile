FROM python:3.10

WORKDIR /usr/local/bin

RUN pip install Flask
RUN pip install PyYAML

COPY vertx-eventbus-client-1.0.0.dev0.tar.gz .

RUN pip install vertx-eventbus-client-1.0.0.dev0.tar.gz

COPY sourceplusplus-0.1.0.tar.gz .

RUN pip install sourceplusplus-0.1.0.tar.gz

COPY E2ETest.py .

RUN mkdir config
ADD ./spp-probe.yml ./config/

ADD ./config/spp-platform.crt ./config/

CMD ["python", "E2ETest.py"]

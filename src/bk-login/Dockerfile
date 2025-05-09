FROM node:18.17.1-bullseye-slim AS StaticBuilding
ENV NPM_VERSION 9.6.7

COPY src/bk-login/pages /
WORKDIR /
RUN npm install
RUN npm run build

FROM python:3.11.10-slim-bullseye
USER root

RUN rm /etc/apt/sources.list && \
    echo "deb https://mirrors.tencent.com/debian bullseye main" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.tencent.com/debian-security bullseye-security main" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.tencent.com/debian bullseye-updates main" >> /etc/apt/sources.list

RUN mkdir ~/.pip &&  printf '[global]\nindex-url = https://mirrors.tencent.com/pypi/simple/' > ~/.pip/pip.conf

RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essential pkg-config

ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

RUN pip install --upgrade pip setuptools

WORKDIR /app
COPY src/bk-login/requirements.txt /app
RUN pip install -r requirements.txt

COPY src/bk-login/bklogin /app/bklogin
COPY src/bk-login/bin /app/bin
COPY src/bk-login/manage.py /app
COPY src/idp-plugins/idp_plugins /app/bklogin/idp_plugins

COPY --from=StaticBuilding /dist /app/staticfiles
COPY --from=StaticBuilding /dist/index.html /app/templates/index.html

CMD ["bash", "/app/bin/start.sh"]

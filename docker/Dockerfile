FROM python:3.9.7-buster as app
ENV \
    WORKDIR=/app \
    TERM=xterm \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=1
WORKDIR $WORKDIR
RUN \
    apt-get update -y \
    && apt install -y \
        apt-utils \
        build-essential \
        ca-certificates \
        wget \
        curl \
        git \
        gnupg \
        gpg-agent \
        libboost-all-dev \
        libbz2-dev \
        libfreetype6-dev \
        libjpeg-dev \
        libjpeg62 \
        libpng-dev \
        libpq-dev  \
        libssl-dev \
        libtool \
        libwebp-dev \
        libwebp6 \
        python3-lxml \
      && rm -rf /var/lib/apt/lists/*

RUN pip install -U pip setuptools poetry
COPY pyproject.toml poetry* ${WORKDIR}/
RUN poetry install --no-dev --no-interaction --no-ansi
ADD . ${WORKDIR}
RUN ./manage.py collectstatic --noinput -v 0


FROM nginx:1.21-alpine as nginx
COPY --from=app /www/assets/ /www/assets/
ADD ./docker/nginx/dev/nginx.conf /etc/nginx/conf.d/default.conf.template
CMD cat /etc/nginx/conf.d/default.conf.template | API_HOST=${API_HOST:-d11-app-api} FLOWER_HOST=${FLOWER_HOST:-d11-app-flower} envsubst '$API_HOST $FLOWER_HOST' > /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'

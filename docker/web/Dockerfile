FROM docker.io/zaplon/gabinet
COPY . /app
WORKDIR /app
ENV DJANGO_SETTINGS_MODULE production_settings
RUN echo yes | ./manage.py compress
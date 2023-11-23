FROM python:3.8-alpine3.18

# Install build dependencies
RUN apk update \
    && apk add --no-cache gcc musl-dev libffi-dev openssl-dev

# Additional dependencies for psycopg2
RUN apk add --no-cache postgresql-libs postgresql-dev

COPY ./src /src
COPY requirements /requirements

WORKDIR src
EXPOSE 8000

RUN pip install -r /requirements/requirements.txt
ENV PATH="/py/bin:$PATH"
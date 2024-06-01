FROM python:3.7 AS builder
WORKDIR /app
COPY install/requirements.txt install/requirements.txt
RUN pip3 install -r install/requirements.txt

FROM python:3.7-slim-buster
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.7/site-packages /usr/local/lib/python3.7/site-packages
COPY . .
RUN ln -sf /dev/stdout /app/refreshMetadata.log
CMD [ "python3", "refreshMetadata.py"]
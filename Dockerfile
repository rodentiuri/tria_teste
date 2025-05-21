FROM python:3.9-slim

# Configurar locale para suportar UTF-8
RUN apt-get update && apt-get install -y locales && \
    sed -i -e 's/# pt_BR.UTF-8 UTF-8/pt_BR.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=pt_BR.UTF-8

ENV LANG=pt_BR.UTF-8

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY etl.py .

RUN mkdir -p ./saida

ENTRYPOINT ["python", "etl.py"] 
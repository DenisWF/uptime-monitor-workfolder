FROM python:3.12-slim

WORKDIR /srv
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY config.yaml .

RUN useradd --system --no-create-home monitor
USER monitor

CMD ["python", "-m", "app.main"]
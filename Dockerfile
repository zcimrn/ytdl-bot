FROM python:alpine
WORKDIR /bot
COPY requirements.txt .
RUN pip install -U pip && pip install -r requirements.txt && rm requirements.txt
COPY client.session bot.py .
CMD ./bot.py

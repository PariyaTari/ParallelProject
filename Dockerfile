FROM python:3.10-bullseye

WORKDIR /src

COPY requirements.txt .

RUN pip install -U pip
RUN pip install -r requirements.txt

COPY . /src

EXPOSE 7000

CMD ["python","main.py"]



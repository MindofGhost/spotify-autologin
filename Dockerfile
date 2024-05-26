FROM joyzoursky/python-chromedriver:3.9-alpine-selenium

WORKDIR /src
VOLUME [ "/app/profiles" ]
COPY main.py /src

CMD ["python", "main.py"]
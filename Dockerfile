FROM python:3.8.6

WORKDIR /usr/src/app

COPY . ./

RUN chmod 777 ./startup.sh && \
    sed -i 's/\r//' ./startup.sh
RUN pip install -r requirements.txt
RUN pip install gunicorn

EXPOSE 5000

CMD ["./startup.sh"]

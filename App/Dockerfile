FROM python:latest
WORKDIR /App
RUN pip install --upgrade pip
COPY Build/requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8080
COPY /Build/ep.sh /ep.sh
RUN chmod +x /ep.sh
ENTRYPOINT ["/ep.sh"]
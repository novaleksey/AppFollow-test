FROM python:latest
WORKDIR /App
COPY Build/requirements.txt requirements.txt
COPY /Build/ep.sh /ep.sh
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8080
RUN chmod +x /ep.sh
ENTRYPOINT ["/ep.sh"]

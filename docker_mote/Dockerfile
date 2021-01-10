FROM python

# copy local to other one
COPY requirements.txt /usr/src/app/requirements.txt

WORKDIR /usr/src/app

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "mote.py" ] 
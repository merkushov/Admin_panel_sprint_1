FROM python:3.9

# set work directory
WORKDIR /usr/src/app

COPY requirements ./requirements
RUN pip install --upgrade pip
RUN pip install -r ./requirements/dev.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .

# copy project
COPY . .

# Entrypoint
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
# Due to the use of f strings Python > 3.6 is required
FROM python:3.7

# install netcat (needed for entrypoint.sh)
RUN apt-get update \
  && apt-get -y install netcat \
  && apt-get clean

# set working directory
RUN mkdir -p /usr/src/pricepicker
WORKDIR /usr/src/pricepicker

# copy requirements
COPY ./requirements.txt /usr/src/pricepicker/requirements.txt

# install requirements
RUN pip install -r requirements.txt

# add entrypoint.sh
COPY ./entrypoint.sh /usr/src/pricepicker/entrypoint.sh

# add remaining files
COPY . /usr/src/pricepicker

# run server
CMD ["./entrypoint.sh"]
ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
#RUN apk add --no-cache python3 bash py3-pip

# requirements from THIS repo/branch (upstream wget pulled main and would desync a fork build)
COPY requirements.txt /requirements.txt

# install dependencies
RUN pip install -r /requirements.txt --break-system-packages

RUN pip install zeroconf requests --break-system-packages

COPY / .
RUN chmod a+x /src/run.sh

CMD [ "/src/run.sh" ]
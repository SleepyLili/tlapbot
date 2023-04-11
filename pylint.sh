#!/bin/sh

cp /etc/ssl/certs/ca-certificates.crt /

apk add --no-cache py-pip linux-headers build-base python3-dev xvfb > /dev/null

cp /ca-certificates.crt /etc/ssl/certs/ca-certificates.crt
rm -f /etc/ssl/cert.pem
ln -s /etc/ssl/certs/ca-certificates.crt /etc/ssl/cert.pem

# FIX CERTIFICATES
for X in $(find /usr -name *.pem); do
    rm -f "$X"
    ln -s /etc/ssl/cert.pem "$X"
done

cd /source

pip install --upgrade wheel setuptools > /dev/null
pip install -r requirements.txt > /dev/null
pip install autopep8 pylint > /dev/null

# FIX CERTIFICATES
for X in $(find /usr -name *.pem); do
    rm -f "$X"
    ln -s /etc/ssl/cert.pem "$X"
done

Xvfb -ac :0 -screen 0 1280x1024x24 &
sleep 5

export DISPLAY=":0"

for X in $(find /source/tlapbot -name *.py); do
    echo 'CHECKING: '"$X"
    pylint --disable=F0401 "$X"
    pylint_exit=$?
    if [ $pylint_exit != 0 ]; then
        echo 'Pylint detected errors in '"$X"' - please fix them if possible.'
        exit 1
    fi
done

echo 'Linting check: OK!'
exit 0

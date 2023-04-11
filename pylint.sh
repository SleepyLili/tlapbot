#!/bin/sh

cp /etc/ssl/certs/ca-certificates.crt /

apk add --no-cache py-pip linux-headers build-base python3-dev > /dev/null 2>&1 3>&1

cp /ca-certificates.crt /etc/ssl/certs/ca-certificates.crt
rm -f /etc/ssl/cert.pem
ln -s /etc/ssl/certs/ca-certificates.crt /etc/ssl/cert.pem

# FIX CERTIFICATES
for X in $(find /usr -name *.pem); do
    rm -f "$X"
    ln -s /etc/ssl/cert.pem "$X"
done

cd /source

pip install --upgrade wheel setuptools > /dev/null 2>&1 3>&1
pip install -r requirements.txt > /dev/null 2>&1 3>&1
pip install autopep8 pylint > /dev/null 2>&1 3>&1

# FIX CERTIFICATES
for X in $(find /usr -name *.pem); do
    rm -f "$X"
    ln -s /etc/ssl/cert.pem "$X"
done

for X in $(find /source/tlapbot -name '*.py'); do
    echo ">>> CHECKING: $X <<<"
    pylint --disable=F0401 "$X"
    pylint_exit=$?
    if [ $pylint_exit != 0 ]; then
        echo ""
        echo " >>> !<>! <<< "
        echo "Pylint detected errors in $X - please fix them if possible."
    fi
done

echo 'Linting check: Finished!'
exit 0

#!/bin/sh

cp /etc/ssl/certs/ca-certificates.crt /

apk add --no-cache markdown > /dev/null
cd /source

echo '<!DOCTYPE html>' > index.html
echo '<html lang="en-US">' >> index.html
cat docs/head.html >> index.html

echo '<body>' >> index.html
markdown README.md >> index.html
echo '</body>' >> index.html
echo '</html>' >> index.html

apk add --no-cache py-pip linux-headers build-base python3-dev xvfb appstream tar libc6-compat curl upx > /dev/null

cp /ca-certificates.crt /etc/ssl/certs/ca-certificates.crt
rm -f /etc/ssl/cert.pem
ln -s /etc/ssl/certs/ca-certificates.crt /etc/ssl/cert.pem

# FIX CERTIFICATES
for X in $(find /usr -name *.pem); do
    rm -f "$X"
    ln -s /etc/ssl/cert.pem "$X"
done

GLIBC_REPO=https://github.com/sgerrand/alpine-pkg-glibc
GLIBC_VERSION=2.30-r0

for pkg in glibc-${GLIBC_VERSION} glibc-bin-${GLIBC_VERSION}; \
    do curl -sSL ${GLIBC_REPO}/releases/download/${GLIBC_VERSION}/${pkg}.apk -o /tmp/${pkg}.apk
done

apk add --allow-untrusted --no-cache -f /tmp/*.apk > /dev/null
/usr/glibc-compat/sbin/ldconfig /lib /usr/glibc-compat/lib

pip install --upgrade wheel setuptools > /dev/null
pip install -r requirements.txt > /dev/null
pip install pyinstaller > /dev/null

# FIX CERTIFICATES
for X in $(find /usr -name *.pem); do
    rm -f "$X"
    ln -s /etc/ssl/cert.pem "$X"
done

Xvfb -ac :0 -screen 0 1280x1024x24 &
sleep 5

py_deps_tlapbot=""
for X in $(cat requirements.txt); do
    py_deps_tlapbot=$py_deps_tlapbot' --collect-all '$X
done

for X in $(find tlapbot/ -name '__pycache__'); do
    rm -rf "$X"
done

py_data_tlapbot=""
for X in ./tlapbot/*; do
    if [ -f "$X" ]; then
        BASENAME=$(basename "$X")
        py_data_tlapbot=$py_data_tlapbot" --add-data $BASENAME:$BASENAME"
    fi
done

py_dirs_tlapbot=""
for X in ./tlapbot/*; do
    if [ -d "$X" ]; then
        BASENAME=$(basename "$X")
        py_dirs_tlapbot=$py_dirs_tlapbot" --add-data $BASENAME/*:$BASENAME/"
    fi
done

cd tlapbot

DISPLAY=":0" pyinstaller -F --onefile --console \
 --additional-hooks-dir=. $py_dirs_tlapbot $py_data_tlapbot \
  $py_deps_tlapbot -i ../docs/icon.png -n tlapbot -c __init__.py

mv dist/tlapbot ../tlapbot-musl
rm -rf dist build log

cd ..

strip tlapbot-musl

chmod +x tlapbot-musl

wget -q https://dl-cdn.alpinelinux.org/alpine/latest-stable/main/x86_64/apk-tools-static-2.12.10-r1.apk -O installer.apk

cd /
tar -xzf /source/installer.apk
cd /source

rm -f installer.apk
/sbin/apk.static -X https://dl-cdn.alpinelinux.org/alpine/latest-stable/main -U --allow-untrusted -p /source/tlapbot.AppDir/ --initdb add --no-cache alpine-base busybox libc6-compat

cd tlapbot.AppDir/
rm -rf etc var home mnt srv proc sys boot opt
cd ..

cp docs/icon.png tlapbot.AppDir/icon.png

echo '[Desktop Entry]' > tlapbot.AppDir/tlapbot.desktop
echo 'Name=tlapbot' >> tlapbot.AppDir/tlapbot.desktop
echo 'Categories=Settings' >> tlapbot.AppDir/tlapbot.desktop
echo 'Type=Application' >> tlapbot.AppDir/tlapbot.desktop
echo 'Icon=icon' >> tlapbot.AppDir/tlapbot.desktop
echo 'Terminal=true' >> tlapbot.AppDir/tlapbot.desktop
echo 'Exec=/lib/ld-musl-x86_64.so.1 /usr/bin/tlapbot' >> tlapbot.AppDir/tlapbot.desktop

chmod +x tlapbot.AppDir/tlapbot.desktop

echo '#!/bin/sh' > tlapbot.AppDir/AppRun
echo 'tlapbot_RUNPATH="$(dirname "$(readlink -f "${0}")")"' >> tlapbot.AppDir/AppRun
echo 'tlapbot_EXEC="${tlapbot_RUNPATH}"/usr/bin/tlapbot' >> tlapbot.AppDir/AppRun
echo 'export LD_LIBRARY_PATH="${tlapbot_RUNPATH}"/lib:"${tlapbot_RUNPATH}"/lib64:$LD_LIBRARY_PATH' >> tlapbot.AppDir/AppRun
echo 'export LIBRARY_PATH="${tlapbot_RUNPATH}"/lib:"${tlapbot_RUNPATH}"/lib64:"${tlapbot_RUNPATH}"/usr/lib:"${tlapbot_RUNPATH}"/usr/lib64:$LIBRARY_PATH' >> tlapbot.AppDir/AppRun
echo 'export PATH="${tlapbot_RUNPATH}/usr/bin/:${tlapbot_RUNPATH}/usr/sbin/:${tlapbot_RUNPATH}/usr/games/:${tlapbot_RUNPATH}/bin/:${tlapbot_RUNPATH}/sbin/${PATH:+:$PATH}"' >> tlapbot.AppDir/AppRun
echo 'exec "${tlapbot_EXEC}" "$@"' >> tlapbot.AppDir/AppRun
#echo 'exec "${tlapbot_RUNPATH}"/lib/ld-musl-x86_64.so.1 "${tlapbot_EXEC}" "$@"' >> tlapbot.AppDir/AppRun

chmod +x tlapbot.AppDir/AppRun

mkdir -p tlapbot.AppDir/usr/bin
cp tlapbot-musl tlapbot.AppDir/usr/bin/tlapbot
chmod +x tlapbot.AppDir/usr/bin/tlapbot

wget -q https://github.com/AppImage/AppImageKit/releases/download/13/appimagetool-x86_64.AppImage -O toolkit.AppImage
chmod +x toolkit.AppImage

cd /opt/
/source/toolkit.AppImage --appimage-extract
mv /opt/squashfs-root /opt/appimagetool.AppDir
ln -s /opt/appimagetool.AppDir/AppRun /usr/local/bin/appimagetool
chmod +x /opt/appimagetool.AppDir/AppRun
cd /source

ARCH=x86_64 appimagetool tlapbot.AppDir/

rm -rf tlapbot.AppDir
rm -f toolkit.AppImage
chmod +x tlapbot-x86_64.AppImage
mv tlapbot-x86_64.AppImage tlapbot-musl-x86_64.AppImage

sha256sum tlapbot-musl > sha256sum.txt
sha256sum tlapbot-musl-x86_64.AppImage >> sha256sum.txt

mkdir -pv /runner/page/
cp -rv /source/* /runner/page/
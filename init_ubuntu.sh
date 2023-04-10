#!/bin/sh

TZ="Europe/Warsaw"
DEBIAN_FRONTEND=noninteractive

apt update > /dev/null
apt install --yes markdown > /dev/null
cd /source

echo '<!DOCTYPE html>' > index.html
echo '<html lang="en-US">' >> index.html
cat docs/head.html >> index.html

echo '<body>' >> index.html
markdown README.md >> index.html
echo '</body>' >> index.html
echo '</html>' >> index.html

apt install --yes python3-pip linux-headers-5.19.0-38-generic build-essential python3-dev xvfb appstream tar lsb-release apt-utils file > /dev/null

pip install --upgrade wheel setuptools > /dev/null
pip install -r requirements.txt > /dev/null
pip install pyinstaller > /dev/null

Xvfb -ac :0 -screen 0 1280x1024x24 &
sleep 5

py_deps_tlapbot=""
for X in $(cat requirements.txt); do
    py_deps_tlapbot=$py_deps_tlapbot' --collect-all '$X
done

for X in $(find . -name '__pycache__'); do
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

mv dist/tlapbot ../tlapbot-glibc
rm -rf dist build log

cd ..

strip tlapbot-glibc

chmod +x tlapbot-glibc

mkdir -p tlapbot.AppDir/var/lib/dpkg
mkdir -p tlapbot.AppDir/var/cache/apt/archives
apt install --yes debootstrap fakeroot fakechroot
fakechroot fakeroot debootstrap --variant=fakechroot --arch amd64 22.04 /source/tlapbot.AppDir/ http://archive.ubuntu.com/ubuntu > /dev/null

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
echo 'Exec=/usr/bin/tlapbot' >> tlapbot.AppDir/tlapbot.desktop

chmod +x tlapbot.AppDir/tlapbot.desktop

echo '#!/bin/sh' > tlapbot.AppDir/AppRun
echo 'tlapbot_RUNPATH="$(dirname "$(readlink -f "${0}")")"' >> tlapbot.AppDir/AppRun
echo 'tlapbot_EXEC="${tlapbot_RUNPATH}"/usr/bin/tlapbot' >> tlapbot.AppDir/AppRun
echo 'export LD_LIBRARY_PATH="${tlapbot_RUNPATH}"/lib:"${tlapbot_RUNPATH}"/lib64:$LD_LIBRARY_PATH' >> tlapbot.AppDir/AppRun
echo 'export LIBRARY_PATH="${tlapbot_RUNPATH}"/lib:"${tlapbot_RUNPATH}"/lib64:"${tlapbot_RUNPATH}"/usr/lib:"${tlapbot_RUNPATH}"/usr/lib64:$LIBRARY_PATH' >> tlapbot.AppDir/AppRun
echo 'export PATH="${tlapbot_RUNPATH}/usr/bin/:${tlapbot_RUNPATH}/usr/sbin/:${tlapbot_RUNPATH}/usr/games/:${tlapbot_RUNPATH}/bin/:${tlapbot_RUNPATH}/sbin/${PATH:+:$PATH}"' >> tlapbot.AppDir/AppRun
echo 'exec "${tlapbot_EXEC}" "$@"' >> tlapbot.AppDir/AppRun

chmod +x tlapbot.AppDir/AppRun

mkdir -p tlapbot.AppDir/usr/bin
cp tlapbot-glibc tlapbot.AppDir/usr/bin/tlapbot
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

mv tlapbot-x86_64.AppImage tlapbot-glibc-x86_64.AppImage

rm -rf tlapbot.AppDir
rm -f toolkit.AppImage
chmod +x tlapbot-glibc-x86_64.AppImage

sha256sum tlapbot-glibc > sha256sum.txt
sha256sum tlapbot-glibc-x86_64.AppImage >> sha256sum.txt

mkdir -pv /runner/page/
cp -rv /source/* /runner/page/
#!/usr/bin/env bash
# This is a very simple example on how to bundle a Python application as an AppImage
# using virtualenv and AppImageKit using Ubuntu
# NOTE: Please test the resulting AppImage on your target systems and copy in any additional
# libraries and/or dependencies that might be missing on your target system(s).

########################################################################
# Create the AppDir
########################################################################

APP=kmol-editor
LOWERAPP=${APP,,}

mkdir -p ENV/$APP.AppDir/
cd ENV/$APP.AppDir/

########################################################################
# Create a virtualenv inside the AppDir
########################################################################

MY_APPDIR=${PWD}

mkdir -p usr
virtualenv --always-copy --python=python3 ./usr

# Copy other modules.
cp /usr/lib/python3.5/ssl.py ./usr/lib/python3.5/ssl.py

source usr/bin/activate

# Source some helper functions
wget -q https://raw.githubusercontent.com/AppImage/AppImages/master/functions.sh -O ./functions.sh
. ./functions.sh

mkdir -p usr/bin/

# Show python and pip versions
python --version
pip --version

# Install python dependencies into the virtualenv
pip install -r ../../requirements.txt

# Copy all built-in scripts.
PYVER=$(python -c "from distutils import sysconfig;print(sysconfig.get_config_var('VERSION'))")
PYDIR=$(python -c "from distutils import sysconfig;print(sysconfig.get_config_var('DESTLIB'))")
MY_PYDIR=${MY_APPDIR}/usr/lib/python${PYVER}

echo "Remove venv distutils ..."
rm -fr -v ${MY_PYDIR}/distutils

echo "Copy built-in script patch from '${PYDIR}' to '${MY_PYDIR}' ..."
cd ${PYDIR}
for f in *; do
    if [ ${f} == "__pycache__" ] || [ ${f} == "test" ] \
        || [ ${f} == "venv" ] || [ ${f} == "idlelib" ]; then continue; fi

    if [[ ${f} == *.py ]]; then
        cp -n -v ${f} ${MY_PYDIR}
    fi

    if [ ! -d ${f} ]; then continue; fi

    echo "Create '${MY_PYDIR}/${f}'"
    mkdir -p ${MY_PYDIR}/${f}
    cp -n -v ${f}/*.py ${MY_PYDIR}/${f}

    cd ${f}

    for sub_f in *; do
        if [ ${sub_f} == "__pycache__" ]; then continue; fi

        if [[ ${sub_f} == *.py ]]; then
            cp -n -v ${sub_f} ${MY_PYDIR}/${f}
        fi

        if [ ! -d ${sub_f} ]; then continue; fi

        echo "Create '${MY_PYDIR}/${f}/${sub_f}'"
        mkdir -p ${MY_PYDIR}/${f}/${sub_f}
        cp -n -v ${sub_f}/*.py ${MY_PYDIR}/${f}/${sub_f}
    done

    cd ..
done
cd ${MY_APPDIR}


# Python libraries.
SCRIPTDIR=$(python -c "from distutils import sysconfig;print(sysconfig.get_config_var('SCRIPTDIR'))")
for f in ${SCRIPTDIR}/libpython3*.so*; do
    cp -n -v ${f} ./usr/lib
done

deactivate

########################################################################
# "Install" app in the AppDir
########################################################################

cp ../../launch_kmol.py usr/bin/$LOWERAPP
sed -i "1i\#!/usr/bin/env python" usr/bin/$LOWERAPP
chmod a+x usr/bin/$LOWERAPP

cp ../../icons_rc.py usr/bin
cp -r ../../core usr/bin
find . -type f -name '*.ui' -delete

########################################################################
# Finalize the AppDir
########################################################################

get_apprun

cd ../..
VERSION=$(python3 -c "from core.info import __version__; print(__version__)")
cd ENV/$APP.AppDir/

cat > $LOWERAPP.desktop <<EOF
[Desktop Entry]
Name=$APP
Exec=$LOWERAPP
Type=Application
Icon=$LOWERAPP
Comment=A light text editor using tree project to edit text-based files.
EOF

# Make the AppImage ask to "install" itself into the menu
get_desktopintegration $LOWERAPP
cp ../../icons/kmol.png $LOWERAPP.png

########################################################################
# Bundle dependencies
########################################################################

copy_deps ; copy_deps ; copy_deps
delete_blacklisted
move_lib

########################################################################
# Package the AppDir as an AppImage
########################################################################

cd ..
generate_appimage

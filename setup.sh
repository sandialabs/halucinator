#!/bin/bash
. /etc/bash_completion
set -e 
set -x
sudo apt install -y ethtool python-tk gdb-multiarch tcpdump

VIRT_ENV="halucinator"
AVATAR_REPO=https://github.com/avatartwo/avatar2.git

CREATE_VIRT_ENV=true

#Look for flags and override
while [ -n "$1" ]; do
 case "$1" in
 -e)
    VIRT_ENV="$2"
    echo "Using Virtual Environment $2"
    shift
    ;;
 -r)
    AVATAR_REPO="$2"
    AVATAR_COMMIT="HEAD"
    echo "Using Avatar Repo $2"
    shift
    ;;
 -nc)
    CREATE_VIRT_ENV=false
    ;;
  * ) echo "Option $1 not recognized";;
 esac
 shift
done


if [ "$CREATE_VIRT_ENV" = true ]; then
   echo "Created Virtual Environment $VIRT_ENV"
   mkvirtualenv -p `which python3` "$VIRT_ENV"
fi

# Activate the virtual environment ('workon' doesn't work in the script)
source "$WORKON_HOME/$VIRT_ENV/bin/activate"


# If avatar already cloned just pull
if pushd deps/avatar2; then
    git pull
    popd
else
    git clone  "$AVATAR_REPO" deps/avatar2    
fi

pushd deps/avatar2

#Get submodules of avatar and build qemu
git submodule update --init --recursive
pip install -e .

pushd targets
./build_qemu.sh
#./build_panda.sh
popd
popd

# Install halucinator dependencies
pip install -r src/requirements.txt
pip install -e src

#!/usr/bin/env bash
#
# This file is intended as a guide to installation, and not a complete script that will work on all platforms. Use accordingly.
#

if [ "$(uname)" == "Darwin" ]; then
    ANADONCA_OS_NAME='MacOSX'      
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    ANADONCA_OS_NAME='Linux'
elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ]; then
    ANADONCA_OS_NAME='Windows'
fi

# Download and install Anaconda
wget -P /tmp/ "http://repo.continuum.io/archive/Anaconda2-2.5.0-${ANADONCA_OS_NAME}-x86_64.sh"
bash "/tmp/Anaconda2-2.5.0-${ANADONCA_OS_NAME}-x86_64.sh" -b -p $HOME/anaconda
export PATH="$HOME/anaconda/bin:$PATH"
echo 'export PATH="$HOME/anaconda/bin:$PATH"' >> ~/.bash_profile

#!/usr/bin/env bash

curl -Lko data/fgvc-aircraft-2013b.tar.gz \
 http://www.robots.ox.ac.uk/~vgg/data/fgvc-aircraft/archives/fgvc-aircraft-2013b.tar.gz

mkdir data/fgvc-aircraft-2013b
tar -xvf data/fgvc-aircraft-2013b.tar.gz -C data/fgvc-aircraft-2013b --strip-components=1

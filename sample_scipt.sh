#!/usr/bin/env bash

for path in `ls -d [0-9]*`; do
    for target in `ls $path/*.csv`; do
         cp $target ${path}_`basename $target`
    done
done

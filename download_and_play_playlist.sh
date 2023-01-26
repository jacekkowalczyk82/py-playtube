#!/usr/bin/env bash

PLAYLIST_URL=$1
PLAYLIST_NAME=$2
PLAYLIST_DIR=$3

mkdir -p ${PLAYLIST_DIR}
cd ${PLAYLIST_DIR}

youtube-dl -f 251 --restrict-filenames ${PLAYLIST_URL}

for file in $(find . -name "*.webm") do 
    echo "${PLAYLIST_DIR}/${file} " >> ~/Music/${PLAYLIST_NAME}.txt
 done

py-playtube.sh ~/Music/${PLAYLIST_NAME}.txt  --random 

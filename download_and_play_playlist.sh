#!/usr/bin/env bash

PLAYLIST_URL=$1
PLAYLIST_NAME=$2
PLAYLIST_DIR=$3

# Usage: 
# ./download_and_play_playlist.sh 'https://www.youtube.com/playlist?list=PLpxLTu3yeWT9Vk2FRHMn1_LDY9q2YgVW1' moja-youtube-music-2 ~/private/music/youtube-dl-temp



mkdir -p ${PLAYLIST_DIR}
cd ${PLAYLIST_DIR}

if [ -e ~/Music/${PLAYLIST_NAME}.txt ]; then 
    echo "Music already downloaded to the given playlist file ~/Music/${PLAYLIST_NAME}.txt !!! "
else

echo "${PLAYLIST_URL} " >> ~/Music/${PLAYLIST_NAME}.txt

for file_name in $(yt-dlp -f 251 --get-filename --restrict-filenames ${PLAYLIST_URL}); do 
    echo $file_name
    echo "${PLAYLIST_DIR}/${file_name} " >> ~/Music/${PLAYLIST_NAME}.txt

done

echo "Download the playlist"
yt-dlp -f 251 --restrict-filenames ${PLAYLIST_URL}
fi 

echo "Random play the playlist "
py-playtube.sh ~/Music/${PLAYLIST_NAME}.txt  --random 

#!/usr/bin/env python

import os
import sys
import subprocess


from os.path import expanduser
HOME = expanduser("~")

DEFAULT_PLAYLIST_FILE = HOME + "/.playtube-list.txt"

PLAYLIST = dict({})

def open_play_list_file(file_path):
    global PLAYLIST
    
    with open(file_path, 'r') as txtfile:
        for line in txtfile:
            print(line)
            PLAYLIST[line] = "to_play"

    return 0
    

def play_playlist():
    os.makedirs(HOME + "/private/music/youtube-dl-temp", exist_ok=True)
    os.chdir(HOME + "/private/music/youtube-dl-temp")
    
    for audio in PLAYLIST.keys():
        # download 
        #youtube-dl -f 251 --get-filename --restrict-filenames $VIDEO_URL
        process1 = subprocess.Popen(["youtube-dl", "-f", "251", "--get-filename", "--restrict-filenames", audio],
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
        stdout1, stderr1 = process1.communicate()
        file_name = stdout1.decode("UTF-8")
        
        print("stdout", stdout1)
        print("File_name", file_name)
        print("stderr",stderr1)
        
        if os.path.isfile(file_name):
            print(f"File {file_name} already exist")
        else:
            process2 = subprocess.Popen(["youtube-dl", "-f", "251", "-o", file_name, audio],
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
            stdout2, stderr2 = process2.communicate()
            
            print("stdout", stdout2)
            print("stderr",stderr2)
            
        #play 
        process3 = subprocess.Popen(["mplayer", "-novideo", file_name],
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
        stdout3, stderr3 = process3.communicate()
        
        print("stdout", stdout3)
        print("stderr",stderr3)

        # mark as played
        PLAYLIST[audio] = "played"
        

    
def main():
    print("youtube playlist player")
    open_play_list_file(DEFAULT_PLAYLIST_FILE)
    play_playlist()
    
if __name__ == "__main__":
    # execute only if run as a script
    main()
	
    

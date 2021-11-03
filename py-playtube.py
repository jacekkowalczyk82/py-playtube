#!/usr/bin/env python

import os
import sys
import subprocess


from os.path import expanduser
HOME = expanduser("~")

DEFAULT_PLAYLIST_FILE = HOME + "/.playtube-list.txt"
PLAYTUBE_TEMP = HOME + "/private/music/youtube-dl-temp"

STATUS_KEY = "status"
TITLE_KEY = "title"

AUDIO_FORMAT = "251"
#AUDIO_FORMAT = "140"

 
def open_play_list_file(file_path, playlist):
    with open(file_path, 'r') as txtfile:
        for line in txtfile:
            audio_url=""
            if "#" in line:
                line_elements = line.split("#")
                audio_url = line_elements[0].strip()
            else:
                audio_url = line.strip()
            print(line)
            if audio_url not in playlist:
                playlist[audio_url] = {STATUS_KEY:"to_play", TITLE_KEY:""}

    return playlist, os.path.abspath(file_path)
    
    
def save_played_playlist(playlist, file_path):
    file = open(file_path, "a") 
    for audio in playlist:
        file.write(f"{audio}   # {playlist[audio][TITLE_KEY]}\n")
         
    file.close() 
        
def get_audio_to_play(playlist):
    print("DEBUG", playlist)
    to_be_played_list = []
    for audio in playlist.keys():
        if playlist[audio][STATUS_KEY] == "to_play":
            to_be_played_list.append(audio)
    return to_be_played_list
    
    
def get_next_to_play(to_be_played_list):
    return to_be_played_list[0]
    
  
def download(playlist, audio):
    if not audio:
        return ""
    #youtube-dl -f 251 --get-filename --restrict-filenames $VIDEO_URL
    process1 = subprocess.Popen(["youtube-dl", "-f", AUDIO_FORMAT, "--get-filename", "--restrict-filenames", audio],
             stdout=subprocess.PIPE, 
             stderr=subprocess.PIPE)
    stdout1, stderr1 = process1.communicate()
    file_name_decoded = stdout1.decode("UTF-8")
    file_name = file_name_decoded.strip()
    
    playlist[audio][TITLE_KEY] = file_name
                    
    print("stdout", stdout1)
    print("File_name", file_name)
    print("stderr",stderr1)

    if os.path.isfile(file_name):
        print(f"File {file_name} already exist")
    else:
        print(f"Downloading {file_name}")
        process2 = subprocess.Popen(["youtube-dl", "-f", AUDIO_FORMAT, "-o", file_name, audio],
             stdout=subprocess.PIPE, 
             stderr=subprocess.PIPE)
        stdout2, stderr2 = process2.communicate()
    
        print("stdout", stdout2)
        print("stderr",stderr2)
    return file_name
    

def play_audio(file_name):
    if not file_name:
        return 1
    #play 
    print(f"Playing {file_name}")
    process3 = subprocess.Popen(["mplayer", "-novideo", file_name],
             stdout=subprocess.PIPE, 
             stderr=subprocess.PIPE)
    stdout3, stderr3 = process3.communicate()

    #print("stdout", stdout3)
    print("stderr",stderr3)
    return 0 
            
        
def play_playlist(playlist, file_path):
    os.makedirs(PLAYTUBE_TEMP, exist_ok=True)
    os.chdir(PLAYTUBE_TEMP)
    
    to_be_played_list = get_audio_to_play(playlist)
    keep_playing = False
    if len(to_be_played_list) > 0:
        keep_playing = True
        
    while keep_playing == True:    
        audio = get_next_to_play(to_be_played_list)
        
        if playlist[audio][STATUS_KEY] == "to_play":
           
            if "https" in audio:
                file_name = download(playlist, audio)
                play_audio(file_name) 
            elif os.path.isfile(audio):
                play_audio(audio) 
            else:
                print(f"ERROR: invalid URL or path: {audio}")
            

            # mark as played
            playlist[audio][STATUS_KEY] = "played"
            
            #refresh to be played list 
            playlist, file_path = open_play_list_file(file_path, playlist)
            to_be_played_list = get_audio_to_play(playlist)
            if len(to_be_played_list) > 0:
                keep_playing = True
            else:
                keep_playing = False
            
            save_played_playlist(playlist, file_path + "_played_temp.txt")
            # end of loop 
            
    print("All youtube songs from the list were played")
    save_played_playlist(playlist, file_path + "_played.txt")

    
def main(args):
    print("youtube playlist player")
    playlist = dict({})
    if len(args) > 1:
        if os.path.isfile(args[1]):
            # play the argument playlist file 
            playlist, file_path = open_play_list_file(args[1], playlist)
    else:
        playlist, file_path = open_play_list_file(DEFAULT_PLAYLIST_FILE, playlist)
        
    play_playlist(playlist, file_path)
    
if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
    
    print("Bye Bye")

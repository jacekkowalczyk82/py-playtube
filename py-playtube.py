#!/usr/bin/env python

import os
import sys
import subprocess
import random 

from os.path import expanduser
HOME = expanduser("~")

#YOUTUBE_DOWNLOAD_APP="youtube-dl"  original one but because of the recent bug I switched to yt-dlp

YOUTUBE_DOWNLOAD_APP="yt-dlp"

DEFAULT_PLAYLIST_FILE = HOME + "/.playtube-list.txt"
PLAYTUBE_TEMP = HOME + "/private/music/youtube-dl-temp"

STATUS_KEY = "status"
TITLE_KEY = "title"

AUDIO_FORMAT = "251"
#AUDIO_FORMAT = "140"

PLAY_ORDER = "LIST_ORDER"

"""
#!/usr/bin/env bash 
cd  /home/jacek/git/py-playtube
python3 py-playtube.py $*
"""
 
def open_play_list_file(file_path, playlist_dict):
    with open(file_path, 'r') as txtfile:
        for line in txtfile:
            audio_url=""
            title=""
            if "#" in line:
                line_elements = line.split("#")
                audio_url = line_elements[0].strip()
                if "# PLAYLIST:" in line: 
                    title = line_elements[1].strip()

            else:
                audio_url = line.strip()
            print(line)
            if audio_url not in playlist_dict:
                playlist_dict[audio_url] = {STATUS_KEY:"to_play", TITLE_KEY:title}

    return playlist_dict, os.path.abspath(file_path)
    
    
def save_played_playlist(playlist_dict, file_path, mode="a"):
    file = open(file_path, mode) 
    for audio in playlist_dict:
        file.write(f"{audio}   # {playlist_dict[audio][TITLE_KEY]}\n")
         
    file.close() 
        

def add_header_to_playlist_file(header, playlist_file_path, mode="a"):
    file = open(playlist_file_path, mode) 

    file.write(f"#  {header}\n")
         
    file.close() 


def add_audio_files_to_playlist_file(local_cache_dir, audio_files, playlist_file_path, mode="a"):
    # print(f"DEBUG::add_audio_files_to_playlist_file {playlist_file_path}")

    file = open(playlist_file_path, mode) 
    for audio in audio_files:
        file.write(f"{local_cache_dir}/{audio}\n")
         
    file.close() 
        


def get_audio_to_play(playlist, play_order):
    # print("DEBUG", playlist)
    to_be_played_list = []
    
    for audio in playlist.keys():
        if playlist[audio][STATUS_KEY] == "to_play":
            to_be_played_list.append(audio)
    #if play_order == "LIST_ORDER":
    #    return to_be_played_list
    if play_order == "RANDOM":
        random.shuffle(to_be_played_list)
    
    return to_be_played_list
    
    
def get_next_to_play(to_be_played_list):
    return to_be_played_list[0]
    

def get_video_id(youtube_url):
    if "watch?v=" in youtube_url:
        url_elements = youtube_url.split("watch?v=")
        if "&" in url_elements[1]:
            url_elements2 = url_elements[1].split("&")
            return url_elements2[0].strip()
        else:
            return url_elements[1].strip()
    else:
        return None

def find_local_audio_by_video_id(local_youtubedl_temp, video_id):
    found_files = []
    for file in os.listdir(local_youtubedl_temp):
        if video_id in file:
            path = os.path.join(local_youtubedl_temp, file)
            # found_files.append(path)
            # print(path)
            return path

    # if found_files[0]:
    #     return found_files[0]    
    return None;


def download_or_get_local(playlist, audio):
    if not audio:
        return ""
    
    video_id = get_video_id(audio)
    print(f"video_id {str(video_id)}")
    file_name = find_local_audio_by_video_id(video_id)
    if file_name:
        print(f"Found local audio by video_id: {str(file_name)}")
              
    else:    
        print(f"\nDownloading {str(audio)}")
        #yt-dlp -f 251 --get-filename --restrict-filenames $VIDEO_URL
        #youtube-dl -f 251 --get-filename --restrict-filenames $VIDEO_URL
        process1 = subprocess.Popen([YOUTUBE_DOWNLOAD_APP, "-f", AUDIO_FORMAT, "--get-filename", "--restrict-filenames", audio],
             stdout=subprocess.PIPE, 
             stderr=subprocess.PIPE)
        stdout1, stderr1 = process1.communicate()
        file_name_decoded = stdout1.decode("UTF-8")
        file_name = file_name_decoded.strip()
    
    if not file_name:
        # this will replace the title from the original playlist txt file
        return None


    playlist[audio][TITLE_KEY] = file_name
                    
    # print("stdout", stdout1)
    print("File_name", file_name)
    # print("stderr",stderr1)

    if os.path.isfile(file_name):
        print(f"File {file_name} already exist")
    else:
        print(f"\nDownloading {file_name}")
        process2 = subprocess.Popen([YOUTUBE_DOWNLOAD_APP, "-f", AUDIO_FORMAT, "-o", file_name, audio],
             stdout=subprocess.PIPE, 
             stderr=subprocess.PIPE)
        stdout2, stderr2 = process2.communicate()
    
        # print("stdout", stdout2)
        # print("stderr",stderr2)
    return file_name
    

  
def download_sublist(playlist_dict, audio_youtube_list):
    print("download_sublist")
    if not audio_youtube_list:
        return ""
    # yt-dlp -f 251 --get-filename --restrict-filenames $VIDEO_URL
    # youtube-dl -f 251 --get-filename --restrict-filenames $VIDEO_URL
    process1 = subprocess.Popen([YOUTUBE_DOWNLOAD_APP, "-f", AUDIO_FORMAT, "--get-filename", "--restrict-filenames", audio_youtube_list],
             stdout=subprocess.PIPE, 
             stderr=subprocess.PIPE)
    stdout1, stderr1 = process1.communicate()
    file_names_decoded = stdout1.decode("UTF-8")
    file_names_string = file_names_decoded.strip()
    file_names_list = file_names_string.splitlines()
    
    # we do not want to replace the title from the original playlist txt file
    # playlist_dict[audio_youtube_list][TITLE_KEY] = str(file_names_list)
    
    # print("stdout", stdout1)
    print("File_names", file_names_list)
    # print("playlist_dict", playlist_dict)
    # print("stderr",stderr1)
    
    print(f"Downloading {str(file_names_list)}")
    process2 = subprocess.Popen([YOUTUBE_DOWNLOAD_APP, "-f", AUDIO_FORMAT, "--restrict-filenames", audio_youtube_list],
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE)
    stdout2, stderr2 = process2.communicate()
       
    # print("stdout", stdout2)
    # print("stderr",stderr2)
            
    for file_name in file_names_list:
        print("File_name", file_name)
        
    return file_names_list
 


def play_audio(file_name):
    if not file_name:
        return 1
    if not os.path.exists(file_name):
        print(f"File not found {file_name}")
        return 2
        
    #play 
    print(f"\nPlaying {file_name}")
    
    with open("/tmp/py-playtube-mplayer.log", "a") as mplayer_log:
        with open("/tmp/py-playtube-mplayer.err.log", "a") as mplayer_err:
            process3 = subprocess.Popen(["mplayer", "-novideo", file_name],
             stdout=mplayer_log, 
             stderr=mplayer_err)
            stdout3, stderr3 = process3.communicate()

    # print("mplayer::stdout ", stdout3)
    # print("mplayer::stderr ", stderr3)
    return 0 
            
        
def play_playlist(playlist_dict, file_path):
    os.makedirs(PLAYTUBE_TEMP, exist_ok=True)
    os.chdir(PLAYTUBE_TEMP)
    
    to_be_played_list = get_audio_to_play(playlist_dict, PLAY_ORDER)
    keep_playing = False
    if len(to_be_played_list) > 0:
        keep_playing = True
        
    while keep_playing == True:    
        audio = get_next_to_play(to_be_played_list)
        
        if playlist_dict[audio][STATUS_KEY] == "to_play":
           
            if "https" in audio and "watch?v=" in audio:
                
                file_name = download_or_get_local(playlist_dict, audio)
                play_audio(file_name) 
            elif "https" in audio and "playlist?list=" in audio:
                sublist = download_sublist(playlist_dict, audio)
                # save sublist  file names list to the txt list file
                # PLAYTUBE_TEMP/file_name
                
                add_header_to_playlist_file(f"{playlist_dict[audio][TITLE_KEY]} {audio}", file_path)
                add_audio_files_to_playlist_file(PLAYTUBE_TEMP, sublist, file_path, mode="a")

                for file_name in sublist:
                    play_audio(file_name)                 
            elif os.path.isfile(audio):
                play_audio(audio) 
            else:
                print(f"ERROR: invalid URL or path: {audio}")
            

            # mark as played
            playlist_dict[audio][STATUS_KEY] = "played"
            
            #refresh to be played list 
            playlist_dict, file_path = open_play_list_file(file_path, playlist_dict)
            to_be_played_list = get_audio_to_play(playlist_dict, PLAY_ORDER)
            if len(to_be_played_list) > 0:
                keep_playing = True
            else:
                keep_playing = False
            
            save_played_playlist(playlist_dict, file_path + "_played_temp.txt", "wt")
            # end of loop 
            
    print("All youtube songs from the list were played")
    save_played_playlist(playlist_dict, file_path + "_played.txt")

    
def main(args):
    global PLAY_ORDER
    print("YouTube playlist player")
    # print("DEBUG::args: " + str(args))
    playlist = dict({})
    if len(args) > 2:
        # print("DEBUG::len(args) > 2")
        # the second param can be a flag, for example SHUFFLE/RANDOM
        if args[2] == "--random":
            PLAY_ORDER = "RANDOM"
            # print("DEBUG::RANDOM")

    if len(args) > 1:
        # print("DEBUG::len(args) > 1")
        if os.path.isfile(args[1]):
            # print("DEBUG::os.path.isfile(args[1]) " + args[1])
            # play the argument playlist file 
            playlist, file_path = open_play_list_file(args[1], playlist)
        else: 
            # print("DEBUG::os.path.isfile(args[1]) False")
            file_path = None
    else:
        # print("DEBUG::else - DEFAULT playlist")
        playlist, file_path = open_play_list_file(DEFAULT_PLAYLIST_FILE, playlist)

    if file_path:    
        play_playlist(playlist, file_path)
    else: 
        print("No playlist file path provided")
    
if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
    
    print("Bye Bye")

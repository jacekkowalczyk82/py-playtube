#!/usr/bin/env python

from configparser import ConfigParser
import json
import os
import sys
import subprocess
import random 

from os.path import expanduser
HOME = expanduser("~")

#YOUTUBE_DOWNLOAD_APP="youtube-dl"  original one but because of the recent bug I switched to yt-dlp

YOUTUBE_DOWNLOAD_APP="yt-dlp"

DEFAULT_PLAYLIST_FILE = HOME + "/.playtube-list.txt"
PLAYTUBE_TEMP = ""

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
 
def read_config(config_file_path):
    config_parser = ConfigParser()
    print(config_parser.sections())
    # with open(config_file_path) as config_file:
    #     config_parser.read_file(config_file)
    config_parser.read(config_file_path)
    print(config_parser.sections())
    print(config_parser["default"])
    print(dict(config_parser["default"]))
    config = dict(config_parser["default"])

    
    if "aws" in config_parser.sections():
        print(dict(config_parser["aws"]))
        config.update(config_parser["aws"])
    
    print(config)
    return config


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


def get_one_message_from_queue(config):

    import boto3
    # Get the service resource
    sqs = boto3.resource('sqs')

    queue_name = config.get("playtube.queue.name")

    # Get the queue. This returns an SQS.Queue instance
    queue = sqs.get_queue_by_name(QueueName=queue_name)

# You can now access identifiers and attributes
    print(queue.url)
    print("DelaySeconds", queue.attributes.get("DelaySeconds"))
    print("queue attributes", str(queue.attributes))

    # Process messages by printing out body and optional author name    
    message = None
    messages = queue.receive_messages()
    if len(messages) > 0:
        print(f"There shoul be some message on queue: {queue_name}")
        message = messages[0]

        # if len(queue.receive_messages()) == 1:
        #     message = messages[0]
        # elif len(queue.receive_messages()) > 1:
            
    else:
        print("No messages in queue")

    if message:
    # for message in queue.receive_messages():
         # Print out the body 
        print(f"Received message on {queue_name}: {message.body}")

        # Let the queue know that the message is processed
        message.delete()
        return message.body
    return None   


def get_next_to_play(file_path, playlist_dict, to_be_played_list, config):
    print ("DEBUG::get_next_to_play")
    if config:
        print ("DEBUG::get_next_to_play, config yes")
        playtube_temp = HOME + config.get("playtube.home.temp")
        provider = config.get("playtube.queue.provider")
        if provider and provider == "aws":
            print ("DEBUG::get_next_to_play, config yes, AWS yes")
            message_string = get_one_message_from_queue(config)
            if message_string:
                message = json.loads(message_string)

                print ("DEBUG::get_next_to_play, config yes, AWS yes, message yes")
                if message.get("action") == "ADD_AND_PLAY":
                    audio_url = message.get("url")
                    if audio_url:
                        title = message.get("title")
                        playlist_dict[audio_url] = {STATUS_KEY:"to_play", TITLE_KEY:title}
                        add_audio_files_to_playlist_file(playtube_temp, [audio_url], file_path, mode="a")
                        to_be_played_list.append(audio_url)
                        return audio_url;
                
                elif message.get("action") == "ADD":
                    audio_url = message.get("url")
                    if audio_url:
                        title = message.get("title")
                        playlist_dict[audio_url] = {STATUS_KEY:"to_play", TITLE_KEY:title}
                        add_audio_files_to_playlist_file(playtube_temp, [audio_url], file_path, mode="a")
                        to_be_played_list.append(audio_url)
                        return to_be_played_list[0];
                else:
                    print("Invalid message format ")
                    return to_be_played_list[0]     
            else:
                print("No messages ")
                # no queue messages, just play next one 
                return to_be_played_list[0]                 

        else:
            print ("DEBUG::get_next_to_play, config no AWS")
            return to_be_played_list[0]
    else:
        print ("DEBUG::get_next_to_play, config None")
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


def download_or_get_local(playlist, audio, local_youtubedl_temp):
    if not audio:
        return ""
    
    video_id = get_video_id(audio)
    print(f"video_id: {str(video_id)}")
    file_name = find_local_audio_by_video_id(local_youtubedl_temp, video_id)

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
        if file_name not in playlist_dict:
            playlist_dict[file_name] = {STATUS_KEY:"to_play", TITLE_KEY:file_name}
        print("File_name", file_name)
        
    return file_names_list
 


def play_audio(file_name):
    if not file_name:
        return 1
    if not os.path.exists(file_name):
        print(f"File not found {file_name}")
        return 2
        
    #play 
    print(f"Playing {file_name}")
    
    with open("/tmp/py-playtube-mplayer.log", "a") as mplayer_log:
        with open("/tmp/py-playtube-mplayer.err.log", "a") as mplayer_err:
            process3 = subprocess.Popen(["mplayer", "-novideo", file_name],
             stdout=mplayer_log, 
             stderr=mplayer_err)
            stdout3, stderr3 = process3.communicate()

    # print("mplayer::stdout ", stdout3)
    # print("mplayer::stderr ", stderr3)
    return 0 
            
        
def play_playlist(playlist_dict, file_path, config):
    global PLAYTUBE_TEMP

    PLAYTUBE_TEMP = HOME + "/" + config.get("playtube.home.temp")

    os.makedirs(PLAYTUBE_TEMP, exist_ok=True)
    os.chdir(PLAYTUBE_TEMP)

    play_counter = 0     
    to_be_played_list = get_audio_to_play(playlist_dict, config.get("play.order"))
    keep_playing = False
    if len(to_be_played_list) > 0:
        keep_playing = True
        
    while keep_playing == True:    
        audio = get_next_to_play(file_path, playlist_dict, to_be_played_list, config) 

        # print (playlist_dict)
        print ("get_next_to_play:", audio)
        if playlist_dict[audio][STATUS_KEY] == "to_play":
           
            play_counter = play_counter + 1
            playlist_size = len(playlist_dict.keys())
            print(f"\nPlaying audio {play_counter} of total {playlist_size}")
        
            if "https" in audio and "watch?v=" in audio:
                
                file_name = download_or_get_local(playlist_dict, audio, PLAYTUBE_TEMP)


                play_audio(file_name) 
            elif "https" in audio and "playlist?list=" in audio:
                sublist = download_sublist(playlist_dict, audio)
                # save sublist  file names list to the txt list file
                # PLAYTUBE_TEMP/file_name
                
                add_header_to_playlist_file(f"{playlist_dict[audio][TITLE_KEY]} {audio}", file_path)
                add_audio_files_to_playlist_file(PLAYTUBE_TEMP, sublist, file_path, mode="a")

                # as sublist is downloaded and added to the playlist dict 
                # lests just go to the next interation of the loop
                # for file_name in sublist:
                    # play_audio(file_name)                 

            elif os.path.isfile(audio):
                play_audio(audio) 
            else:
                print(f"ERROR: invalid URL or path: {audio}")
            

            # mark as played
            playlist_dict[audio][STATUS_KEY] = "played"
            # if this is a sublist  it will be marked as played but the individual audios will be added to the play order
            
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
    global PLAYTUBE_CONFIG 

    print("YouTube playlist player")
    # print("DEBUG::args: " + str(args))
    playlist = dict({})
    
    if len(args) > 1:
        if len(args) > 2:
            print("DEBUG::len(args) > 2")
            print("DEBUG::args[2]: ", args[2])
            PLAYTUBE_CONFIG = read_config(args[2])

        else:
            # from default home location 
            # /home/jacek/.config/py-playtube
            PLAYTUBE_CONFIG = read_config(".config/py-playtube/config.ini")

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
    
    if not PLAYTUBE_CONFIG:
        return 
    
    if PLAYTUBE_CONFIG.get("play.order"):
        PLAY_ORDER = PLAYTUBE_CONFIG.get("play.order")
    else:
        PLAY_ORDER = "LIST_ORDER"
    
    

    if file_path:    
        play_playlist(playlist, file_path, PLAYTUBE_CONFIG)
    else: 
        print("No playlist file path provided")
    
if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
    
    print("Bye Bye")

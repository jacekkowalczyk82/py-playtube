# py-playtube

simple python wrapper for youtube-dl or yt-dlp and mplayer to play youtube audio from the console 

This is a very DRAFT code, it works for me. 
Tested at macos, FreeBSD, Linux

## Requirements

Installed youtube-dl or yt-dlp and mplayer. 

## How to use it 

Create a file: ~/.playtube-list.txt and add there some youtube videos URLs. 

for example: 

```
https://www.youtube.com/watch?v=FBOx1IB2F44
https://www.youtube.com/watch?v=-fcNoePKTtU
https://www.youtube.com/watch?v=1bYJO61bgDM
https://www.youtube.com/watch?v=ylX7fcqEa8w
https://www.youtube.com/watch?v=NnfQu8Ob34g
https://www.youtube.com/watch?v=63TQKWokqeU
https://www.youtube.com/watch?v=AWTNT68FkB8
https://www.youtube.com/watch?v=vc-Kh4oXHkE
https://www.youtube.com/watch?v=zvpX1nTyEmc

```

start the script 

```
python3 py-playtube.py 
# or
chmod 755 py-playtube.py 
./py-playtube.py 

# play playlist 

python3 /home/jacek/git/py-playtube/py-playtube.py /home/jacek/Music/py-playtube-kombi.txt 

# play in random order
python3 /home/jacek/git/py-playtube/py-playtube.py /home/jacek/Music/py-playtube-kombi.txt --random
```

Example script to play the playlist

```
#!/usr/bin/env bash 

cd $HOME/
python3 /home/jacek/git/py-playtube/py-playtube.py /home/jacek/Music/py-playtube-kombi.txt "$@"




```

Enjoy !!!


## The py-playtube has integration with AWS sqs 

The application can read from AWS SQS messages that alows to add new audio urls remotely 

For example sending message to the SQS queue:

```
{
  "action": "ADD_AND_PLAY",
  "url": "https://www.youtube.com/watch?v=9Uj2VyG8T0I",
  "title": "Man in the rain"
}
```

will tell the application to add this given url to the playlist and play it as next. 



Simple bot for downloading youtube videos and sending them as audio to you.
Can download playlists and also will split long videos (longer than 20 minutes) into chunks as it seems that tg servers reject big files.

## Setup 
Place your tg api token into env_file like this:
    
    TG_TOKEN=<your token>
 
and run following in the root of the repo:

    docker build -t to_mp3:0.1 .
    ./run.sh
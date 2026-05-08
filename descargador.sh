#!/bin/bash
URL=$1
FORMATO=$2
DESTINO="/media/hdd/Mp3"

mkdir -p "$DESTINO"

if [ "$FORMATO" == "audio" ]; then
    yt-dlp -f "ba[ext=m4a]" -x --audio-format m4a -o "$DESTINO/%(title)s.%(ext)s" "$URL"
else
    yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" -o "$DESTINO/%(title)s.%(ext)s" "$URL"
fi

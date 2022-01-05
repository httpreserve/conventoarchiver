#!/usr/bin/bash

# Script to supply httpreserve.info with links from arg[1] to then
# save them in the Internet Archive.
#
#  $ nohup ./httpreserver.sh <links-list> &
#
# Depends-on: jq, urlencode.
#
# Part of github.com/httpreserve
#
# By Ross Spencer.

echoerr() { echo "$@" 1>&2; }

echoerr "httpreserving links: started"

HTTPRESERVE="http://localhost:2040/save?url="

count=0
while read LINK ; do
   ENCODED=$(urlencode "$LINK")
   OUTPUT=$(curl -s -X GET "$HTTPRESERVE$ENCODED")
   EARLIEST=$(echo $OUTPUT | jq ".InternetArchiveLinkEarliest")
   LATEST=$(echo $OUTPUT | jq ".InternetArchiveLinkLatest")
   echo [$count]: $EARLIEST
   echo [$count]: $LATEST
   (( count++ ))
   sleep 5
done < $1

echoerr "httpreserving links: done"

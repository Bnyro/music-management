#!/bin/bash

cat "$1" | while read line; do
  xdg-open "https://piped.chatoyer.de/watch?v=$line"
  read -p "Enter to accept: " input </dev/tty
  [ -z $input ] && echo "$line" >> NEW
done

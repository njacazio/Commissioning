#!/bin/bash

#Script to format the .tex files

List=$(find | grep "\.tex" | grep --invert-match bak | grep --invert-match backup | grep --invert-match "\.aux" | xargs)
echo "Formatting $List"

Avoid=""

if [[ ! -d backups ]]; then
  mkdir backups
  touch backups/.gitignore
  echo "*" >backups/.gitignore
fi

for i in ${List[@]}; do
  Dir=${i%/*}
  echo "$i is in dir $Dir"
  if [[ -d "$Dir/localSettings.yaml" ]]; then
    echo "Skipping dir $Dir"
    continue
  fi

  if [[ ${Dir} != "." ]]; then
    if [[ ! -f ${Dir}/localSettings.yaml ]]; then
      ln -s $PWD/localSettings.yaml $Dir
    fi
    LastDir=$PWD
    cd $Dir
    latexindent -s -l -w -c=$LastDir/backups ${i##*/}
    cd -
  else
    latexindent -s -l -w -c=backups ${i}
  fi
done

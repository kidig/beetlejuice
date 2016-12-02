#!/bin/bash

export LC_ALL=en_US.UTF-8

function newWindow() {
  TARGET=$(tmux new-window -P)
}

function splitH() {
  TARGET=$(tmux splitw -P -v -p ${1:-50} -t ${TARGET})
}

function splitV() {
  TARGET=$(tmux splitw -P -h -p ${1:-50} -t ${TARGET})
}

function run() {
  tmux send-keys -t ${TARGET} "$1" C-m
}

if [[ $TMUX ]]; then
  tmux set-option -g mouse on

  if [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    tmux set-window-option -g mode-mouse on
    tmux set-option -g mouse-select-pane on
  fi

  tmux bind q kill-session

  newWindow
  run "source .env"
  run "./venv/bin/python3 manage.py runserver"
  splitH
  run "source .env"
  run "./venv/bin/python3 manage.py robust_worker --beat"

else
  tmux new-session $0
fi

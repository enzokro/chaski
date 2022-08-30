#!/bin/bash

# clean out the old library and site
if [[ -d chaski ]]; then
  rm -Rf chaski
fi
if [[ -d _docs ]]; then
  rm -Rf _docs
fi

# run library building and site-deploying commands
nbdev_prepare
nbdev_quarto
nbdev_deploy

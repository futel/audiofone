#!/bin/bash

# Run puredata with the tones osc patch

# TODO: Daemonize

pd -alsa -send "pd dsp 1" -nogui /opt/futel/src/pd/tones.pd

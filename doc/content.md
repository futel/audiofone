## Configuring content

Sound files must be placed on a mounted USB drive.

* VFAT filesystem
* content in root directory
* WAV files
* filenames in the format NUMBER[_TEXT].wav
 * NUMBER is the number the user enters for that content to be played
 * TEXT is arbitrary
 * examples
  * 5035555555_monologue.wav
  * 503555555.wav

## File format

The sound file format is:
* PCM
* 16-bit little endian (LE)
* 44.1kHz sampling rate
* Mono (preferred) or stereo (if stereo, only the left channel will be played)

## normalizing audio

You can use the `normalize-audio` utility to normalize the volume of the audio files.
Warning: this will destructively modify the files in-place (keep a copy as originals prior to doing this).

```
sudo apt update && sudo apt install normalize-audio
normalize-audio *.wav

```

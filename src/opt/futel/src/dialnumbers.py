"""
Match dialed numbers against soundfile names in the audio directory.
"""

from enum import Enum, auto
import os

audio_directory = "/mnt/futel"


class NumberValidity(Enum):
    INVALID_KEY = auto()
    NOT_PREFIX = auto()
    POSSIBLE_PREFIX = auto()


def have_number(number):
    """
    Return soundfile or enum for number.
    """
    if(invalid_dialplan(number)):
        return NumberValidity.INVALID_KEY
    soundfile = get_soundfile(number)
    if soundfile is not None:
        return soundfile
    if not possible_number(number):
        return NumberValidity.NOT_PREFIX
    return NumberValidity.POSSIBLE_PREFIX

def soundfile_number(filename):
    """ Return number corresponding to soundfile. """
    filename = filename.split('.').pop(0)
    return filename.split('_').pop(0)

def get_soundfile(number):
    """ Return normalized soundfile name corresponding to number. """
    for filename in os.listdir(audio_directory):
        if soundfile_number(filename) == number:
            # Remove suffix, if there, player doesn't want it.
            # Assume only one . in filename.
            return filename.split('.').pop(0)
    return None

def possible_number(number):
    """ Return True if number should not receive an invalid notification. """
    possible_numbers = [
        soundfile_number(filename) for filename in os.listdir(audio_directory)]
    if len(number) < max(len(number) for number in possible_numbers):
        return True
    return False

def invalid_dialplan(number):
    """Return True if number matches a forbidden sequence."""
    if number.startswith("0"): return True
    if "#" in number: return True
    if "*" in number: return True
    return False

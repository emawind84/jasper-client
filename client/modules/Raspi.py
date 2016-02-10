# -*- coding: utf-8-*-
import datetime
import re
from client.app_utils import getTimezone
from semantic.dates import DateService

WORDS = ["HI", "RASPI"]


def handle(text, mic, profile):
    """
        I say hi to my raspi!
    """

    mic.say("Hi %s how are you today?" % profile['first_name'])
    
    mic.activeListen()
    
    mic.say("Good!")


def isValid(text):
    """
        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\braspi\b', text, re.IGNORECASE))

# Copyright (C) 2011 Philter Phactory Ltd.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE X
# CONSORTIUM BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name of Philter Phactory Ltd. shall
# not be used in advertising or otherwise to promote the sale, use or other
# dealings in this Software without prior written authorization from Philter
# Phactory Ltd.

from base_prosthetic import Prosthetic
from django.template.loader import render_to_string
import logging
import math
import random
import re
import time
import urllib

import models


#TODO: "Where is everybody?" functionality


GREETINGS = ["Hi %s", "Hello %s", "Heya %s", "Hi there %s", "Oh hello, %s",
             "Greetings %s"]

MISSINGS = ["Hmm, where's %s ?", "Why haven't I seen %s lately?",
            "I haven't seen %s today...", "Where's %s?", "I miss %s.",
            "Missing %s..."]

MISS_PROBABILITY = 12 # 1 in n

GREET_DISTANCE = 1.1 # miles


class NoLocationFoundException(Exception):
    """An exception to mark that no location was found. As its name implies."""
    pass


class Greeter(Prosthetic):
    """A prosthetic that allows a user's Weavrs to greet each other if they
       are positioned close to each other, or to wonder where they have got
       to."""

    def is_awake(self, state):
        """Whether the Weavr is awake or asleep"""
        return state['awake']

    def should_post(self, state):
        """Whether the Weavr should post or not at the moment"""
        return self.is_awake(state)

    def get_location(self, access_token=None):
        """Get the Weavr's current location.
           Raises NoLocatioNFoundException if no current location."""
        if access_token == None:
            access_token = self.token
        locations = access_token.get_json("/1/weavr/location/")['locations']
        if len(locations) == 0:
            logging.info("no location found")
            raise NoLocatioNFoundException()
        location = locations[0]
        return location
   
    def distance(self, latitude, longitude, location):
        """Calculate the Euclidian distance between this weavr and the other"""
        return math.sqrt(abs(pow((float(location['lat']) - latitude), 2) +
                             pow((float(location['lon']) - longitude), 2)))

    def post_greeting(self, state, other_token):
        """Post a message greeting the other"""
        logging.info("greeting %s" % other_token.weavr_name)
        name_html = '<a href="%s">%s</a>' % (other_token.weavr_url,
                                             other_token.weavr_name)
        greeting = random.choice(GREETINGS) % name_html
        self.post("/1/weavr/post/", {
                "category":"status",
                "title":greeting,
                "keywords":state["emotion"],
                })

    def post_missing(self, state, other_token):
        """Post a message saying the weavr misses the other"""
        logging.info("missing %s" % other_token.weavr_name)
        name_html = '<a href="%s">%s</a>' % (other_token.weavr_url,
                                             other_token.weavr_name)
        missing = random.choice(MISSINGS) % name_html
        self.post("/1/weavr/post/", {
                "category":"status",
                "title":self.get_title(what),
                "body":embed,
                "keywords":state["emotion"],
                })
        
    def maybe_post_missing(self, state, other_token):
        """Post a missing message at random infrequent intervals"""
        if random.randrange(0, MISS_PROBABILITY) == 0:
            self.post_missing(state, other_token)

    def maybe_greet(self, state, other, latitude, longitude):
        """If in range, greet the other weavr"""
        try:
            other_location = self.get_location(other.weavr_token)
            if(self.distance(latitude,
                             longitude,
                             other_location) <= GREET_DISTANCE):
                self.post_greeting(state, other.weavr_token)
            else:
                self.maybe_post_missing(state, other.weavr_token)
        except NoLocationFoundException, nlf:
            logging.info("No location found for %s" % str(other))

    def maybe_greet_others(self, state, location):
        """Check the user's other registered Weavrs to see of we should greet"""
        others = models.other_weavrs_in_group(self.token)
        latitude = float(location['lat'])
        longitude = float(location['lon'])
        for other in others:
            self.maybe_greet(state, other, latitude, longitude)

    def act(self, force=False):
        result = "Error"
        logging.info("Starting")
        try:
            state = self.get("/1/weavr/state/")
            logging.info("Got state")
            if self.should_post(state):
                location = self.get_location()
                self.maybe_greet_others(state, location)
                result = "Ran greeter logic"
            else:
                result = "Shouldn't post, so didn't"
        except NoLocationFoundException, e:
            logging.info("No location found")
            logging.info(str(e))
            pass
        except Exception, e:
            logging.error("Exception in greeter prosthetic:\n%s" % str(e))
        return result

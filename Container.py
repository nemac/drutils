import sys, re, os, optparse, shutil, json, drutils, subprocess, time

from Nappl import *
from NapplMeta import *

class Container:
    def __init__(self, appName):
        self.appName = appName
        self.meta = None

    @staticmethod
    def load(appName):
        """Return an instance of a Container object corresponding to an container.  The
        returned object will have a 'meta' property which has been pre-loaded with 
        a NapplMeta object containing the container metadata."""
        meta = NapplMeta(appName)
        if not os.path.exists(meta.datafile):
            raise Exception("Container not found.")
        meta.load()
        if meta.data['application']['type'] == "drupal":
            container = DrupalContainer(appName)
            container.meta = meta
            return container
        raise Exception("Unknown container type '%s'" % meta.data['application']['type'])

    @staticmethod
    def list_containers():
        """Return a list of the current application containers; each entry in the list
        is a python dict containing metadata about the application."""
        if not os.path.exists("/var/nappl"):
            raise Exception("/var/nappl directory not found")
        apps = []
        for appname in os.listdir("/var/nappl"):
            a = NapplMeta(appname)
            a.load()
            apps.append(a.data)
        return apps



#!/usr/bin/python3

import requests
import webbrowser
import json

from threading import Thread

class Deezer(Thread) :
    
    status = False
        
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}):
        Thread.__init__(self, group, self.titles, name, args, kwargs)
        self._return = None
        
    def search_deezer(self, search):
        url = "https://api.deezer.com/search?q=" + search
        response = requests.get(url)
        js = response.json()
        for value in js['data'] :
            if value['title'].lower() == search.lower() :
                return (len(value['title'].split()), value)
        return (1, search.lower())
    
    def titles(self, input) :
        words = input.split()
        titles = []
        format = []
        start_index = 0
        while start_index < len(words) :
            stored_result = (0, '')
            for index in range(len(words)) :
                search = words[start_index:index + 1:]
                if search :
                    (size, result) = self.search_deezer(" ".join(search))
                    if size > stored_result[0] :
                        stored_result = (size, result)            
            start_index += stored_result[0]
            titles.append(stored_result[1])
        for index in range(len(titles)) :
            title = titles[index]
            if not isinstance(title, str) :
                format.append([title['id'], title['album']['cover'], title['title'], title['artist']['name'], title['album']['title']])
            else :
                format.append(['', '', title, '', ''])
        self.status = True
        return format
        
    def run(self) :
        Thread__target = self.titles
        Thread__args = self._args
        Thread__kwargs = {}
        self._return = Thread__target(*Thread__args, **Thread__kwargs)
        
    def join(self) :
        Thread.join(self)
        return self._return
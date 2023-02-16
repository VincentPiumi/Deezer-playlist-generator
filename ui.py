import tkinter as tk
import tkinter.messagebox
import customtkinter
import os
import requests
import threading
import deez
import time

from tkinter import ttk
from tkinter.messagebox import showerror
from export import Export
from deez import *
from PIL import ImageTk, Image
from threading import Thread
from io import BytesIO

class SongFrame(customtkinter.CTkFrame):
    options = {'padx': 5, 'pady': 5}
    has_error = False
    songs = []
    
    def __init__(self, container, deez, export):
        super().__init__(container)
        self.exp = export
        while deez.status == False :
            self.update()
        self.songs = deez.join()
        self.columnconfigure(3, weight=len(self.songs) + 2)
        self.grid(column=0, row=1, sticky=tk.NSEW, **self.options)
        self.display_header()
        self.display_songs()
        self.export()
        
    
    def display_header(self) :
        headers = ["", "TITRE", "ARTISTE", "ALBUM"]
        self.song_label_name = customtkinter.CTkLabel(self, text=headers[0])
        self.song_label_name.grid(column=0, row=0, sticky=tk.W, **self.options)
        self.song_label_name.height = 55
        self.song_label_name.width = 55
        for header in range(1, len(headers)) :
            self.song_label_name = customtkinter.CTkLabel(self, text=headers[header])
            self.song_label_name.grid(column=header, row=0, sticky=tk.W, **self.options)
        
    def display_image(self, url, index) :
        if len(url) != 0 :
            response = requests.get(url)
            response_content = response.content
            img = customtkinter.CTkImage(light_image=Image.open(BytesIO(response_content)),
                                              dark_image=Image.open(BytesIO(response_content)),
                                              size=(50, 50))
            self.song_label = customtkinter.CTkLabel(self, image=img, text="")
            self.song_label.grid(column=0, row=index + 1, sticky=tk.W, **self.options)
        else :
            self.has_error = True
        
    def display_songs(self) :
        for index, song in enumerate(self.songs):
            self.display_image(song[1], index)
            for col in range(1, 4) :
                self.song_label = customtkinter.CTkLabel(self, text=song[col + 1])
                self.song_label.grid(column=col, row=index + 1, sticky=tk.W, **self.options)
                           
    def export(self) :
        self.export_button = customtkinter.CTkButton(self, text="Export to Deezer", fg_color=("gray75", "gray30"), command=self.export_event)
        self.export_button.grid(row=len(self.songs) + 1, column=0, pady=10, padx=20)
            
    def export_event(self) :
        self.mb_options = {'default': "no"}
        if self.has_error :
            alert_message = "Au moins un titre n'a pas été trouvé, voulez-vous tout de même exporter la playlist ?"
            self.alert_messagebox = tkinter.messagebox.askyesno(title="Attention", message=alert_message, **self.mb_options)
            if self.alert_messagebox :
                self.export_button.configure(state=tkinter.DISABLED)
                songs_id = [str(song[0]) for song in self.songs if song[0] != '']
                self.export_status(self.exp.main_export(songs_id))         
        else :
            alert_message = "Êtes-vous sûr de vouloir exporter la playlist ?"
            self.alert_messagebox = tkinter.messagebox.askyesno(title="Attention", message=alert_message, **self.mb_options)
            if self.alert_messagebox :
                self.export_button.configure(state=tkinter.DISABLED)  
                songs_id = [str(song[0]) for song in self.songs]
                self.export_status(self.exp.main_export(songs_id)) 
        
    def export_status(self, status) :
        if status :
            self.exportstatus_label = customtkinter.CTkLabel(self, text="Playlist sent to Deezer", text_font=("Courier italic", -12))
            self.exportstatus_label.grid(row=len(self.songs) + 1, column=3, pady=10, padx=20)
        else :
            self.exportstatus_label = customtkinter.CTkLabel(self, text="Error during export", text_font=("Courier italic", -12))
            self.exportstatus_label.grid(row=len(self.songs) + 1, column=3, pady=10, padx=20)
            
    def update_grid(self, index) :
        if index > 3 :
            self.grid_forget()
        else :
            self.grid(column=0, row=index, sticky=tk.NSEW, **self.options)
               
class InputFrame(customtkinter.CTkFrame):  
    songframes = []
    sf_index = 1
    
    def __init__(self, container):
        super().__init__(container)
        self.export = Export()
        
        self.columnconfigure(1, weight=1)
        options = {'padx': 5, 'pady': 5}

        self.input_label = customtkinter.CTkLabel(self, text="Entrez votre phrase : ")
        self.input_label.grid(column=0, row=0, sticky=tk.E, **options)
        
        self.input = tk.StringVar()
        self.input_entry = customtkinter.CTkEntry(self, textvariable=self.input)
        self.input_entry.grid(column=1, row=0, sticky=tk.EW, **options)
        self.input_entry.focus()
        
        self.validate_button = customtkinter.CTkButton(self, text='Validate', fg_color=("gray75", "gray30"), command=self.validate)
        container.bind('<Return>', self.validate_on_entry)
        self.validate_button.grid(column=2, row=0, sticky=tk.E, **options)
        
        self.grid(padx=10, pady=10, sticky=tk.NSEW)
  
    def validate_on_entry(self, event) :
        self.validate()
  
    def validate(self) :
        try:
            input = self.input.get()
            deez = Deezer(args=(input,))
            deez.start()
            sf = SongFrame(app, deez, self.export)
            
            self.songframes.append([sf, self.sf_index])
            self.sf_index += 1
            if self.sf_index > 2 :
                for sf, index in self.songframes :
                    update_index = self.sf_index - index
                    sf.update_grid(update_index)
            
        except ValueError as error:
            showerror(title='Error', message=error)

class Application(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        screen_width = int(self.winfo_screenwidth() / 2)
        screen_height = self.winfo_screenheight()
        
        self.title("Deezer - Générateur de playlists")
        self.geometry(f'{screen_width}x{screen_height}')
        self.resizable(True, True)
        self.columnconfigure(0, weight=1)
        ico = Image.open('./assets/deezer.ico')
        img = ImageTk.PhotoImage(ico)
        self.wm_iconphoto(False, img)

if __name__ == "__main__":    
    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("blue")
    app = Application()
    InputFrame(app)
    app.mainloop()  

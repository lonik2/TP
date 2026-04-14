import os
import random
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from PIL import Image, ImageTk
import io

class ReproductorMusical:
    def __init__(self, root):
        self.root = root
        self.root.title("Reproductor de Música - Proyecto Final")
        self.root.geometry("600x500")
        
        pygame.mixer.init()        
        
        self.lista_canciones = []
        self.indice_actual = 0
        self.modo_aleatorio = False
        self.modo_repetir = False
        self.reproduciendo = False
        
        self.crear_interfaz()
        self.actualizar_barra_progreso()

    def crear_interfaz(self):
        frame_superior = tk.Frame(self.root)
        frame_superior.pack(pady=10, fill="x", padx=10)
        
        frame_medio = tk.Frame(self.root)
        frame_medio.pack(pady=10, fill="both", expand=True, padx=10)
        
        frame_inferior = tk.Frame(self.root)
        frame_inferior.pack(pady=10, fill="x", padx=10)

        tk.Button(frame_superior, text="Cargar Carpeta", command=self.cargar_carpeta).pack(side="left", padx=5)
        tk.Button(frame_superior, text="Guardar Playlist", command=self.guardar_playlist).pack(side="left", padx=5)
        tk.Button(frame_superior, text="Cargar Playlist", command=self.cargar_playlist).pack(side="left", padx=5)

        self.listbox = tk.Listbox(frame_medio, width=40)
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.seleccionar_cancion)

        frame_info = tk.Frame(frame_medio, width=200)
        frame_info.pack(side="right", fill="y", padx=10)
        
        self.label_caratula = tk.Label(frame_info, text="Sin Carátula", bg="gray", width=20, height=10)
        self.label_caratula.pack(pady=5)
        
        self.label_titulo = tk.Label(frame_info, text="Título: ---", font=("Arial", 10, "bold"))
        self.label_titulo.pack()
        self.label_artista = tk.Label(frame_info, text="Artista: ---")
        self.label_artista.pack()
        self.label_album = tk.Label(frame_info, text="Álbum: ---")
        self.label_album.pack()

        self.barra_progreso = ttk.Progressbar(frame_inferior, orient="horizontal", length=400, mode="determinate")
        self.barra_progreso.pack(pady=5)
        
        self.label_tiempo = tk.Label(frame_inferior, text="00:00 / 00:00")
        self.label_tiempo.pack()

        frame_controles = tk.Frame(frame_inferior)
        frame_controles.pack(pady=5)
        
        tk.Button(frame_controles, text="⏮ Anterior", command=self.anterior).pack(side="left", padx=5)
        tk.Button(frame_controles, text="▶ Play", command=self.reproducir).pack(side="left", padx=5)
        tk.Button(frame_controles, text="⏸ Pausa", command=self.pausar).pack(side="left", padx=5)
        tk.Button(frame_controles, text="⏹ Stop", command=self.parar).pack(side="left", padx=5)
        tk.Button(frame_controles, text="⏭ Siguiente", command=self.siguiente).pack(side="left", padx=5)

        frame_extras = tk.Frame(frame_inferior)
        frame_extras.pack(pady=5)
        
        self.btn_aleatorio = tk.Button(frame_extras, text="Aleatorio: OFF", command=self.toggle_aleatorio)
        self.btn_aleatorio.pack(side="left", padx=5)
        
        self.btn_repetir = tk.Button(frame_extras, text="Repetir: OFF", command=self.toggle_repetir)
        self.btn_repetir.pack(side="left", padx=5)
        
        tk.Label(frame_extras, text="Volumen:").pack(side="left", padx=5)
        self.slider_volumen = ttk.Scale(frame_extras, from_=0, to=1, orient="horizontal", command=self.cambiar_volumen)
        self.slider_volumen.set(0.5) # Volumen a la mitad por defecto
        self.slider_volumen.pack(side="left")

        def cargar_carpeta(self):
        carpeta = filedialog.askdirectory()
        if not carpeta:
            return
        
        self.lista_canciones.clear()
        self.listbox.delete(0, tk.END)
        
        for archivo in os.listdir(carpeta):
            if archivo.endswith(".mp3"):
                ruta_completa = os.path.join(carpeta, archivo)
                info = self.extraer_metadatos(ruta_completa)
                self.lista_canciones.append(info)
                # Mostrar en la lista de forma simple
                texto_lista = f"{info['artista']} - {info['titulo']}"
                self.listbox.insert(tk.END, texto_lista)

    def extraer_metadatos(self, ruta):
        info = {
            "ruta": ruta,
            "titulo": os.path.basename(ruta).replace(".mp3", ""),
            "artista": "Desconocido",
            "album": "Desconocido",
            "duracion": 0
        }
        try:
            audio = MP3(ruta, ID3=ID3)
            info["duracion"] = audio.info.length
            
            # Leer etiquetas ID3
            if audio.tags:
                if 'TIT2' in audio.tags:
                    info["titulo"] = str(audio.tags['TIT2'])
                if 'TPE1' in audio.tags:
                    info["artista"] = str(audio.tags['TPE1'])
                if 'TALB' in audio.tags:
                    info["album"] = str(audio.tags['TALB'])
        except Exception as e:
            print(f"Error leyendo {ruta}: {e}")
            
        return info

    def reproducir(self):
        if not self.lista_canciones:
            return
            
        cancion = self.lista_canciones[self.indice_actual]
        pygame.mixer.music.load(cancion["ruta"])
        pygame.mixer.music.play()
        self.reproduciendo = True
        
        # Actualizar info en pantalla
        self.label_titulo.config(text=f"Título: {cancion['titulo']}")
        self.label_artista.config(text=f"Artista: {cancion['artista']}")
        self.label_album.config(text=f"Álbum: {cancion['album']}")
        self.mostrar_caratula(cancion["ruta"])
        
        # Marcar en la lista
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(self.indice_actual)
        self.listbox.activate(self.indice_actual)

    def pausar(self):
        if self.reproduciendo:
            pygame.mixer.music.pause()
            self.reproduciendo = False
        else:
            pygame.mixer.music.unpause()
            self.reproduciendo = True

    def parar(self):
        pygame.mixer.music.stop()
        self.reproduciendo = False

    def siguiente(self):
        if not self.lista_canciones: return
        
        if self.modo_aleatorio:
            self.indice_actual = random.randint(0, len(self.lista_canciones) - 1)
        else:
            self.indice_actual += 1
            if self.indice_actual >= len(self.lista_canciones):
                if self.modo_repetir:
                    self.indice_actual = 0
                else:
                    self.indice_actual = len(self.lista_canciones) - 1
                    self.parar()
                    return
        self.reproducir()

    def anterior(self):
        if not self.lista_canciones: return
        self.indice_actual -= 1
        if self.indice_actual < 0:
            self.indice_actual = 0
        self.reproducir()
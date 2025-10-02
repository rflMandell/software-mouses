""" 
Interface grafica principal do Mouse Manager
Utiliza tkinter para criar uma GUI funcional
Versao: 1.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, font 
import threading
import sys
import os
import time 
from typing import Optional, Dict, Any, List 
from dataclasses import asdict

#adiciona o diretorio pai ao path para import os modulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from modules.mouse_detector import MouseDetector, MouseInfo
    from modules.system_settings import SystemMouseSettings, MouseSettings, MouseAcceleration
except ImportError as e:
    print(f"erro ao importar modulos: {e}")
    sys.exit(1)
    
class MouseManagerGUI:
    """
    Interface grafica principal do MouseManager
    Fornece uma experiencia completa de gerenciamento de mouses
    """
    
    def __init__(self):
        """Inicializa a interface grafica"""
        self.rott = tk.Tk()
        self.setup_window()
        
        #inicializa os modulos
        try:
            self.mouse_detector = MouseDetector()
            self.system_settings = SystemMousSettings()
        except Exception as e:
            messagebox.showerror("Erro de inicializacao",
                                 f"Erro ao inicializar modulos:\n {e}")
            self.root.destroy()
            return
        
        #variaveis de controle
        self.current_settings: Optional[MouseSettings] = None
        self.settings_backup: Optional[MouseSettings] = None
        self.auto_refresh_enable = tk.BooleanVar(value=True)
        self.refresh_interval = 5000 #5secs
        self.refresh_job = None
        
        #variaveis da interface
        self.setup_variables()
        
        #configura a interface
        self.setup_ui()
        self.setup_styles()
        
        #carrega dados inicias
        self.load_initial_data()
        
        #iniciar refresh automatico
        self.start_auto_refresh()
        
    def setup_window(self):
        """Configura a janela principal"""
        self.root.title("Mouse Manager MVP - Gerenciador Universal de Mouses")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        self.root.resizable(True, True)
        
        #icone da janela (em breve?)
        try: 
            #tenta definir um icone padrao
            self.root.iconbitmap(default="")
        except:
            pass
        
        #centraliza a janela
        self.center_window()
        
        #configura o fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    
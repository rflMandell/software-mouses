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
        
    def setup_variables(self):
        """Configura as variaveis de controle da interface"""
        #variaveis de configuracao
        self.speed_var = tk.IntVar(value=10)
        self.accel_var = tk.BooleanVar(value=True)
        self.dclick_var = tk.IntVar(value=500)
        self.swap_buttons_var = tk.BooleanVar(value=False)
        self.wheel_lines_var = tk.IntVar(value=3)
        self.hover_time_var = tk.IntVar(value=400)
        
        #variaveis de status
        self.status_var = tk.StringVar(value="Inicializando...")
        self.mice_count_var = tk.StringVar(value="0 mouses detectados")
        
        #bind para mudancas automaticas
        self.speed_var.trace('w', self.on_setting_change)
        self.dclick_var.trace('w', self.on_setting_change)
        self.wheel_lines_var.trace('w', self.on_setting_change)
        self.hover_time_var.trace('w', self.on_setting_change)
        
    def setup_styles(self):
        """COnfigura estilos personalizados"""
        style = ttk.Style()
        
        #configura o tema
        try:
            styles.theme_use('clam')
        except:
            pass
        
        # estilos personalizados
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 10, 'bold'))
        style.configure('Info,TLabel', font=('Arial', 9))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        style.configure('Warning.TLabel', foreground='orange')
        
    def setup_ui(self):
        """Configura a interface do usuario"""
        #frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        #barra de ferrmanentas supeirior
        self.setup_toolbar(main_frame)
        
        # notebook para abas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # cnofgura as abas
        self.setup_detection_tab()
        self.setup_settings_tab()
        self.setup_advanced_tab()
        self.setup_about_tab()
        
        #barra de status
        self.setup_status_bar(main_frame)
        
    def setup_toolbar(self, parent):
        """Configura a toolbar"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0,5))
        
        #titulo principal
        title_label = ttk.Label(toolbar, text="Mouse Manager MVP",
                                style='Title.TLabel')
        title_label.pack(side=tk.LEFT)
        
        #botoes da toolbar
        buttom_frame = ttk.Frame(toolbar)
        buttom_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="Atualizar Tudo",
                   command=self.refresh_all_data).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(button_frame, text="Backup",
                   command=self.create_backup).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(button_frame, text="Restaurar",
                   command=self.restore_backup).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(button_frame, text="Padroes",
                   command=self.restore_defaults).pack(side=tk.LEFT, padx=2)
        
        #checkbox para auto-refresh
        ttk.Checkbutton(button_frame, text="Auto-refresh",
                        variable=self.auto_refresh_enable,
                        command=self.toggle_auto_refresh).pack(side=tk.LEFT, padx=5)
        
    def setup_detection_tab(self):
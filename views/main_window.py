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
            self.system_settings = SystemMouseSettings()
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
            style.theme_use('clam')
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
        
        ttk.Button(buttom_frame, text="Atualizar Tudo",
                   command=self.refresh_all_data).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(buttom_frame, text="Backup",
                   command=self.create_backup).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(buttom_frame, text="Restaurar",
                   command=self.restore_backup).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(buttom_frame, text="Padroes",
                   command=self.restore_defaults).pack(side=tk.LEFT, padx=2)
        
        #checkbox para auto-refresh
        ttk.Checkbutton(buttom_frame, text="Auto-refresh",
                        variable=self.auto_refresh_enable,
                        command=self.toggle_auto_refresh).pack(side=tk.LEFT, padx=5)
        
    def setup_detection_tab(self):
        """Configura a aba de deteccao de mouses"""
        detection_frame = ttk.Frame(self.notebook)
        self.notebook.add(detection_frame, texto="Mouses Detectados")
        
        #Frame superior com informacoes e controles
        top_frame = ttk.Frame(detection_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        #informacoes de contagem
        info_frame = ttk.LabelFrame(top_frame, text="Resumo")
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        
        self.mice_count_label = ttk.Label(info_frame, textvariable=self.mice_count_var,
                                          style='Subtitle.TLabel')
        self.mice_count_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.connection_summary_label = ttk.Label(info_frame, text="",
                                                  style='Info.TLabel')
        self.connection_summary_label.pack(anchor=tk.W, padx=5, pady=2)
        
        #botoes de controle
        control_frame = ttk.Frame(top_frame)
        control_frame.pack(side="right")
        
        ttk.Button(control_frame, text="Atualizar Lista",
                   command=self.refresh_mice_list).pack(pady=2)
        ttk.Button(control_frame, text="Detalhes",
                   command=self.show_detailed_info).pack(pady=2)
        ttk.Button(control_frame, text="Exportar",
                   command=self.export_mice_info).pack(pady=2)
        
        #Treeview para mostrar mouses
        tree_frame = ttk.LabelFrame(detection_frame, text="Dispositivos Detectados")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        #configuracao do treeview
        colums = ('Nome', 'Fabricante', 'VID', 'PID', 'Conexao', 'Serial', 'Release')
        self.mice_tree = ttk.Treeview(tree_frame, colums=colums, show='headings', height=8)
        
        #configurar colunas
        column_widths = {'Nome': 200, 'Fabricante': 150, 'VID': 80, 'PID': 80,
                         'Conexao': 100, 'Serial': 120, 'Release': 80}
        
        for col in colums:
            self.mice_tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c))
            self.mice_tree.column(col, width=column_widths.get(col, 100), minwidth=60)
            
        # scrollbars para o treeview
        tree_scroll_frame = ttk.Frame(tree_frame)
        tree_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        v_scrollbar = ttk.Scrollbar(tree_scroll_frame, orient=tk.VERTICAL,
                                    command=self.mice_tree_yview)
        h_scrollbar = ttk.Scrollbar(tree_scroll_frame, orient=tk.HORIZONTAL,
                                    comand=self.mice_tree.xview)
        
        self.mice_tree.configure(yscrollcommand=v_scrollbar.self,
                                 xcrollcommand=h_scrollbar.set)
        
        #pack treeview e scrollbars
        self.mice_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_scroll_frame.grid_rowconfigure(0, weight=1)
        tree_scroll_frame.grid_columnconfigure(0, weight=1)
        
        #frame de informacoes detalhadas
        detail_frame = ttk.LabelFrame(detection_frame, text="Informacoes Detalhadas")
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.into_text = scrolledtext.ScolledText(detail_frame, height=6, wrap=tk.WORD,
                                                  font=('Consolas', 9))
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        #bind para selecao na arvore
        self.mice_tree.bind('<<TreeviewSelect>>', self.on_mouse_select)
        self.mice_tree.bind('<Double-1>', self.on_mouse_double_click)
        
    def setup_settings_tab(self):
        """Configura a aba de configuracoes do sistema"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Configuracoes")
        
        #Frame principal com scroll
        canvas = tk.Canvas(settings_frame)
        scrollbar = tk.Scrollbar(settings_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_windoe((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        #configuracoes principais
        self.setup_speed_settings(scrollable_frame)
        self.setup_acceleration_settings(scrollable_frame)
        self.setup_click_settings(scrollable_frame)
        self.setup_advanced_settings(scrollable_frame)
        
        #botao de acao
        self.setup_action_buttons(scrollable_frame)
        
        #pack canvas e scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        #bind mouse whell
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scoll(int(-1*(e.delta/120)), "units"))
        
    def setup_speed_settings(self, parent):
        """Configura controles de velocidade"""
        speed_frame = ttk.LabelFrame(parent, text="Velocidade do Mouse")
        speed_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(speed_frame, text="Velodidade (1-20):").pack(anchor=tk.W, padx=5, pady=2)
        
        speed_control_frame = ttk.Frame(speed_frame)
        speed_control_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.speed_scale = ttk.Scale(speed_control_frame, from_=1, to=20, orient=tk.HORIZONTAL,
                                     variable=self.speed_var, command=self.on_speed_change)
        self.speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.speed_label = ttk.Label(speed_control_frame, text="10", width=3)
        self.speed_label.pack(side=tk.RIGHT, padx=(5,0))
        
        #botoes de preset
        preset_frame = ttk.Frame(speed_frame)
        preset_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(preset_frame, text="Lento", width=8,
                   command=lambda: self.speed_var.set(5)).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Normal", width=8,
                   command=lambda: self.speed_var.set(10)).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Rapido", width=8,
                   command=lambda: self.speed_var.set(15)).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Muito Rapido", width=8,
                   command=lambda: self.speed_var.set(20)).pack(side=tk.LEFT, padx=2)
        
    def setup_acceleration_settings(self, parent):
        """Configura controles de aceleracao"""
        accel_frame = ttk.LabelFrame(parent, text="Aceleracao do Mouse")
        accel_frame.pack(fill=tk.X, padx=10, pady=5)
        
        #checkbox principal
        accel_check = ttk.Checkbutton(accel_frame, text="Habilitar aceleracao do mouse",
                                        variable=self.accel_var, command=self.on_acceleration_change)
        accel_check.pack(anchor=tk.W, padx=5, pady=5)
        
        #Frame para niveis de aceleracao
        level_frame = ttk.Frame(accel_frame)
        level_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(level_frame, text="Nivel:").pack(side=tk.LEFT)
        
        ttk.Button(level_frame, txt="Baixo", width=8,
                    command=lambda: self.set_acceleration_level(MouseAcceleration.LOW)).pack(side=tk.LEFT, padx=2)
        ttk.Button(level_frame, txt="Medio", width=8,
                    command=lambda: self.set_acceleration_level(MouseAcceleration.MEDIUM)).pack(side=tk.LEFT, padx=2)
        ttk.Button(level_frame, txt="Alto", width=8,
                    command=lambda: self.set_acceleration_level(MouseAcceleration.HIGH)).pack(side=tk.LEFT, padx=2)
        
        #informacoes sobre
        info_label = ttk.Label(accel_frame, 
                               text="A aceleracao faz o cursor se mover mais rapido quando voce mode o mouse rapidamente.",
                               style='Info.TLabel', wraplength=400)
        info_label.pack(anchor=tk.W, padx=5, pady=2)
        
    def setup_click_settings(self, parent):
        """Configura controles de clique"""
        click_frame = ttk.LabelFrame(parent, text="Configuracoes de Clique")
        click_frame.pack(fill=tk.X, padx=10, pady=5)
        
        #velodicdade do duplo clique
        dclick_subframe = ttk.Frame(click_frame)
        dclick_subframe.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(dclick_subframe, text="Velocidade do Duplo Clique (100-900 ms):").pack(anchor=tk.W)
        
        dclick_control_frame = ttk.Frame(dclick_subframe)
        dclick_control_frame.pack(fill=tk.X, pady=2)
        
        self.dclick_scale = ttk.Scale(dclick_control_frame, from_=100, to=900, orient=tk.HORIZONTAL,
                                      variable=self.dclick_var, command=self.on_click_change)
        self.dclick_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.dclick_label = ttk.Label(dclick_control_frame, text="500ms", width=8)
        self.dclick_label.pack(side=tk.RIGHT, padx=(5,0))
        
        #botao de teste
        ttk.Button(dclick_subframe, text="Testar Duplo Clique",
                   command=self.test_double_click).pack(anchor=tk.W, pady=2)
        
        #troca de botoes
        ttk.Checkbutton(click_frame, text="Trocar botoes primario e secundario",
                        variable=self.swap_buttons_var,
                        command=self.on_button_swap_change).pack(anchor=tk.W, padx=5, pady=5)
        
    def setup_advanced_settings(self, parent):
        """Configura configuracoes avancadas"""
        advanced_frame = ttk.LabelFrame(parent, text="Configuracoes Avancadas")
        advanced_frame.pack(fill=tk.X, padx=10, pady=5)
        
        #scroll da roda
        whell_subframe = ttk.Frame(advanced_frame)
        whell_subframe.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(whell_subframe, text="Linhas por scroll da roda (1-100):").pack(anchor=tk.W)
        
        wheel_control_frame = ttk.Frame(whell_subframe)
        wheel_control_frame.pack(fill=tk.X, pady=2)
        
        self.wheel_scale = ttk.Scale(wheel_control_frame, from_=1, to=100, orient=tk.HORIZONTAL,
                                     variable=self.wheel_lines_var, command=self.on_wheel_change)
        self.wheel_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.wheel_label = ttk.Label(wheel_control_frame, text="3", width=4)
        self.wheel_label.pack(side=tk.RIGHT, padx=(5,0))
        
        #tempo de hover
        hover_subframe = ttk.Frame(advanced_frame)
        hover_subframe.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(hover_subframe, text="Tempo de hover (100-2000 mx):").pack(anchor=tk.W)
        
        hover_control_frame = ttk.Frame(hover_subframe)
        hover_control_frame.pack(fill=tk.X, pady=2)
        
        self.hover_scale = ttk.Scale(hover_control_frame, from_=100, to=2000, orient=tk.HORIZONTAL,
                                     variable=self.hover_time_var, command=self.on_hover_change)
        self.hover_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.hover_label = ttk.Label(hover_control_frame, text="400 ms", width=8)
        self.hover_label.pack(side=tk.RIGHT, padx=(5,0))
        
    def setup_action_buttons(self, parent):
        """Configura botoes de acao"""
        button_frame = ttk.LabelFrame(parent, tect="Acoes")
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Primeira linha de botoes
        row1 = ttk.Frame(button_frame)
        row1.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(row1, text="Aplicar configuracoes", 
                   command=self.apply_settings).pack(side=tk.LEFT, padx=2)
        ttk.Button(row1, text="Atualizar",
                   command=self.load_current_settings).pack(side=tk.LEFT, padx=2)
        ttk.Button(row1, text="Restaurar Padroes",
                   command=self.restore_defaults).pack(side=tk.LEFT, padx=2)
        
        #segunda linha de butoes
        row2 = ttk.Frame(button_frame)
        row2.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(row2, text="Criar Backup",
                   command=self.create_backup).pack(side=tk.LEFT, padx=2)
        ttk.Button(row2, text="Restaurar Backup",
                   command=self.restore_backup).pack(side=tk.LEFT, padx=2)
        ttk.Button(row2, text="Ver Resumo",
                   command=self.show_settings_summary).pack(side=tk.LEFT, padx=2)
        
    def setup_advanced_tab(self):
        """Configura a aba de configuracoes avancadas"""
        advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(advanced_frame, text="Avancado")
        
        #informacoes do sistema
        system_frame = ttk.LabelFrame(advanced_frame, text="Informacoes do Sistema")
        system_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.system_info_text = scrolledtext.ScolledText(system_frame, height=8, wrap=tk.WORD,
                                                         font=('Consolas', 9))
        self.system_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        #ferramentas de diagnostico
        diag_frame = ttk.LabelFrame(advanced_frame, text="Ferramentas de Diagnostico")
        diag_frame.pack(fill=tk.X, padx=10, pady=5)
        
        diag_buttons = ttk.Frame(diag_frame)
        diag_buttons.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(diag_buttons, text="Verificar Sistemas",
                   command=self.run_system_check).pack(side=tk.LEFT, padx=2)
        ttk.Button(diag_buttons, text="Estatisticas",
                   command=self.show_hid_stats).pack(side=tk.LEFT, padx=2)
        ttk.Button(diag_buttons, text="Teste de Performace",
                   command=self.run_performance_test).pack(side=tk.LEFT, padx=2)
        
        #log de atividades
        log_frame = ttk.LabelFrame(advanced_frame, text="Log de Atividades")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD,
                                                  font=('Consolas', 8))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        #bootes do log
        log_buttons = ttk.Frame(log_frame)
        log_buttons.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(log_buttons, text="Limpar Log",
                   command=self.clear_log).pack(side=tk.LEFT, padx=2)
        ttk.Button(log_buttons, text="Salvar Log",
                   command=self.save_log).pack(side=tk.LEFT, padx=2)
        
    def setup_about_tab(self):
        """Configura a aba sobre"""
        about_frame = ttk.Frame(self.notebook)
        self.notebook.add(about_frame, text="Sobre")
        
        #titulo e versao
        title_frame = ttk.Frame(about_frame)
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(title_frame, text="Mouse Manager MPV",
                  font=('Arial', 16, 'bold')).pack()
        ttk.Label(title_frame, text="Versao 1.0.0",
                  font=('Arial', 12)).pack(pady=5)
        ttk.Label(title_frame, text="Software Universal apra gerenciamento de Mouses Genericos",
                  font=('Arial', 10)).pack()
        
        #informacoes
        info_text = """
Funcionalidades:
- Deteccao automatica de mouses HID
- Configuracao de velocidade e aceleracao
- Contole de duplo Clique e scroll
- Backup e restauracao de configuracoes
- Interface moderna e intuitiva

Tecnologias:
- Python
- TKinter
- HIDAPI
- ctypes

Requisitos:
- Windows 10/11
- Python 3.7 ou superior
- Biblioteca hidapi

Desenvolvido como MVP
para demonstracao de capacidades de deteccao
e configuracao de mouses genericos.

Seguranca:
- Apenas le informacoes de dispositivos HID
- Modifica apenas configuracoes padrao do Windows
- Nao instala drivers ou altera arquivos do sistema
        """
        
        info_label = ttk.LAbel(about_frame, text=info_text, justify=tk.LEFT,
                               font=('Arial', 9))
        info_label.pack(padx=20, pady=10, anchor=tk.W)
    
    def setup_status_bar(self, parent):
        """Configura a barra de status"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5,0))
        
        #status principal
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var,
                                      rlief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        #indicador de admin
        self.admin_label = ttk.Label(status_frame, text="", relief=tk.SUNKEN, width=15)
        self.admin_label.pack(side=tk.RIGHT, padx=(2, 0))
        
        #atualiza status de admin
        self.update_admin_status()
        
    def load_initial_data(self):
        """Carrega dados inicais"""
        def load_in_thread():
            try:
                self.status_var.set("Carregando configuracoes...")
                self.load_current_settings()
                
                self.status_var.set("Detectando mouses...")
                self.refresh_mice_list()
                
                self.status_var.set("Carregando informacoes do sistema...")
                self.load_system_info()
                
                self.status_var.set("Pronto")
                self.log_message("sistema inicializado com sucesso")
                
            except Exception as e:
                self.satus_var.set(f"Erro na inicializacao: {e}")
                self.lof_message(f"Erro na inicializacao: {e}", "ERRO")
                
                threading.Thread(target=load_in_thread, daemon=True).start()
                
    def refresh_mice_list(self):
        """Atualiza a lista de mouses detectados"""
        def update_in_thread():
            try:
                self.status_var.set("detectando mouses...")
                
                mice = self.mouse_detector.get_connected_mice(force_refresh=True)
                
                #Atualiza a interface na thread principal
                self.root.after(0, self._update_mice_display, mice)
                
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"Erro ao detectar mouses: {e}"))
                self.log_message(f"Erro ao detectar mouses: {e}", "ERROR")
                
        threading.Thread(target=update_in_thread, deamo=True).start()
        
    def _update_mice_display(self, mice: List[MouseInfo]):
        """Atualiza a exibicao dos mouses na interface"""
        try:
            #limpa a arvore
            for item in self.mice_tree.get_children():
                self.mice_tree.delete(item)
                
            #adicione os mouses detectados
            for mouse in mice:
                self.mice_tree.insert('', tk.END, values=(
                    mouse.name,
                    mouse.manufacturer,
                    mouse.vendor_id,
                    mouse.product_id,
                    mouse.connection_type,
                    mouse.serial_number,
                    mouse.release_number
                ))
                
            #atualiza contadores
            count = len(mice)
            self.mice_count_var.set(f"{count} mouse(s) detectados(s)")
            
            #atualiza resumo de conexoes 
            summary = self.mouse_detector.get_mouse_summary()
            summary_text = f"USB: {summary['usb']} | Bluetooth: {summary['bluetooth']} | Outro: {summary['outros']}"
            self.connection_summary_label.config(text=summary_text)
            
            self.status_var.set(f"Detectados {count} mouse(s)")
            self.log_message(f"Detectados {count} mouses(s)")
            
        except Exception as e:
            self.status_var.set(f"Erro ao ataulizar lista: {e}")
            self.log_message(f"Erro ao atualizar lista: {e}", "ERROR")
            
    def on_mouse_select(self, event):
        """Callback para selecao de mouse na arvore"""
        try:
            selection = self.mice_tree.selection()
            if not selection:
                return
            
            item = self.mice_tree.item(selection[0])
            values=item['values']
            
            if len(values) < 4:
                return
            
            #encontra o mouse correspondente
            mice = self. mouse_detector.mice_info
            selected_mouse = None
            
            for mouse in mice:
                if (mouse.name == values[0] and
                    mouse.vendor_id == values[2] and
                    mouse.product_id == values[3]):
                    select_mouse = mouse
                    break
                
            if selected_mouse:
                self.show_mouse_details(selected_mouse)
                
        except Exception as e:
            self.log_message(f"Erro ao selecionar mouse: {e}", "ERROR")
            
    def on_mouse_double_click(self, event):
        """Callback para duplo clique no mouse"""
        try:
            selection = self.mice_tree.selection()
            if selection:
                self.show_detailed_info()
        except Exception as e:
            self.log_message(f"Erro no duplo clique: {e}", "ERROR")
            
    def show_mouse_details(self, mouse: MouseInfo):
        """Mostra detalhes do mouse selecionado"""
        try:
            details = ''
        except Exception as e:
            pass
            
    def load_current_settings(self):
        """Carrega as configuracoes atuais do sistema"""
        def load_in_thread():
            try:
                self.current_settings = self.system_settings.get_current_settings()
                
                # atualiza a interface na thread principal
                self.root.after(0, self._update_settings_display)
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro ao carregar configuracoes:\n{e}"))
                self.log_message(f"Erro ao carregar configuracoes: {e}", "ERROR")
                
        threading.Thread(target=load_in_thread, daemon=True).start()
        
    def _update_settings_display(self):
        """Atualiza a exibicao das configuracoes na interface"""
        if not self.current_settings:
            return
        
        try:
            #atualiza variaveis sem disparar callbacks
            self.speed_var.set(self.current_settings.speed)
            self.accel_vat.set(self.current_settings.acceleraion_enable)
            self.dclick_var.set(self.current_settings.double_click_speed)
            self.swap_buttons_var.set(self.current_settings.swap_buttons)
            self.wheel_lines_vat.set(self.current_settings.wheel_scroll_lines)
            self.hover_time_vat.set(self.current_settings.hover_time)
            
            #atualiza labels
            self.speed_label.config(text=str(self.current_settings.speed))
            self.dclick_label.config(text=f"{self.current_settings.double_click_speed} ms")
            self.wheel_label.config(text=str(self.current_settings.wheel_scroll_lines))
            self.hover_label.config(text=f"{self.current_settings.hover_time} ms")
            
            self.status_var.set("Configuracoes carregadas")
            self.log_message("Configuracoes carregadas com sucesso")
            
        except Exception as e:
            self.log_message(f"Erro ao atualizar interface: {e}", "ERROR")
            
    #callbacks para mudancas nas configuracoes
    def on_speed_change(self, value):
        """Callback para mudanca na velocidade"""
        speed = int(float(value))
        self.speed_label.config(test=str(speed))
        
    def on_acceleration_change(self):
        """Callback para mudanca na aceleracao"""
        self.log_message(f"Aceleracao {'habilitada' if self.accel_var.get() else 'desabilitada'}")
        
    def on_dclick_change(self, value):
        """Callback para mudanca na velocidade do dublo clique"""
        speed = int(float(value))
        self.dclick_label.config(text=f"{speed} ms")
        
    def on_button_swap_change(self):
        """Callback para mudanca na troca de botoes"""
        self.log_message(f"Botoes {'trocados' if self.swap_buttons_vat.get() else 'normais'}")
        
    def on_wheel_change(self, value):
        """Callback para mudanca nas linhas de scroll"""
        lines = int(float(value))
        self.wheel_label.config(text=str(lines))
        
    def on_hover_change(self, value):
        """Callback para mudanca no tempo de hover"""
        time_ms = int(float(value))
        self.hover_label.config(text=f"{time_ms} ms")
    
    def on_settings_change(self, *args):
        """Callback generico para mudancas nas configuracoes"""
        #usar futuramente para auto-aplicar configuracoes
        pass
    
    #metodos de acao
    def apply_settings(self):
        """Aplica as confoiguracoes selecionadas"""
        def apply_in_thread():
            try:
                self.status_var.set("Aplicando configuracoes...")
                
                #cria objeto com as configuracoes atuais da interface
                new_settings = MouseSettings(
                    speed=self.speed_var.get(),
                    acceleration_enable=self.accel_var.get(),
                    acceleration_threshold1=6 if self.accel_var.get() else 0,
                    acceleration_threshold2=10 if self.accel_var.get() else 0,
                    acceleration_factor=1 if self.accel_var.get() else 0,
                    double_click_speed=self.dclick_var.get(),
                    swap_buttons=self.swap_buttons_var.get(),
                    wheel_scroll_lines=self.wheel_lines_var.get(),
                    hover_time=self.hover_time_vat.get(),
                    drag_width=4, #valor padrao
                    drag_height=4
                )
                
                #aplica as configs
                results = self.system_settings.apply_settings(new_settings)
                
                #verifica resultados
                success_count = sum(1 for success in results.value() if success)
                total_count = len(results)
                
                if success_count == total_count:
                    message = "Todas as configuracoes foram aplicadas com sucesso."
                    self.root.after(0, lambda: messagebox.showinfo("Sucesso", message))
                    self.root.after(0, lambda: self.status_var.set("Configuracoes aplicadas com sucesso."))
                    self.log_message("Configuracoes aplicadas com sucesso.", "INFO")
                else:
                    failed = [key for key, success in results.items() if not success]
                    message = f"Algumas configuracoes falharam: {', '.join(failed)}"
                    self.root.after(0, lambda: messagebox.showwarning("Aviso", message))
                    self.root.after(0, lambda: self.status_var.set("Aplicacao parcial"))
                    self.log_message(f"Aplicacaoo parcial: {message}", "WARNING")
                    
            except Exception as e:
                error_msg = f"Erro ao aplicar onfiguracoes: {e}"
                self.root.after(0, lambda: messagebox.showerror("Erro", error_msg))
                self.root.after(0, lambda: self.status_var.set("erro na aplicacao"))
                self.log_message(error_msg, "ERROR")
                
        threading.Thread(target=apply_in_thread, daemon=True).start()
        
    def restore_defaults(self):
        """Restaura configuracoes padrao"""
        if messagebox.askyesno("Confirmar", "Deseja restaurar todas as configuracoes para os valores padrao?"):
            def restore_in_thread():
                try:
                    self.status_var.set("Restaurando padroes...")
                    
                    results = self.system_settings.restore_defaults()
                    success_count = sum(1 for success in results.values() if success)
                    
                    if success_count > 0:
                        self.root.after(0, self.load_current_settings)
                        self.root.after(0, lambda: messagebox.showinfo("Sucesso", "Configuracoes padrao restauradas!"))
                        self.log_message("COnfiguracoes padrao restauradas")
                    else:
                        self.root.after(0, lambda: messagebox.showerror("Erro", "Falha ao restaurar configuracoes padrao"))
                        self.log_message("Falha ao restaurar configuracoes padrao", "ERROR")
                        
                except Exception as e:
                    error_msg = f"Erro ao restaurar configuracoes: {e}"
                    self.root.after(0, lambda: messagebox.showerror("Erro", error_msg))
                    self.log_message(error_msg, "ERROR")
                    
            threading.Thread(target=restore_in_thread, daemon=True).start()
            
    def create_backup(self):
        """Cria um backup das confoiguracoes atuais"""
        try:
            self.settings_backup = self.system_settings.backup_settings()
            messagebox.showinfo("Backup", "BAckup das configuracoes criado com sucesso!")
            self.log_message("Backup das configuracoes criado")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar backup:\n{e}")
            self.log_message(f"Erro ao criar backup: {e}", "ERROR")
            
    def restore_backup(self):
        """Restaura configuracoes a partir do backup"""
        if not self.settings_backup:
            messagebox.showwarning("Aviso", "nenhum backup disponivel. Crie um backup antes de utilizar essa funcao")
            return
        
        if messagebox.messagebox.askyesno("Confirmar", "Deseja resturar as configuracoes do backup?"):
            def restore_in_thread():
                try:
                    self.status_var.set("restaurando backup...")
                    
                    results = self.system_settings.restore_from_backup(self.settings_backup)
                    success_count = sum(1 for success in results.values() if success)
                    
                    if success_count > 0:
                        self.root.after(0, self.load_current_settings)
                        self.root.after(0, lambda: messagebox.showinfo("sucesso", "Backup restaurado com sucesso!"))
                        self.log_message("Backup restaurado com sucesso")
                    else:
                        self.root.after(0, lambda: messagebox.showerror("Erro", "falha ao restaurar backup"))
                        self.log_message("falha ao restaurar backup", "ERROR")
                    
                except Exception as e:
                    error_msg = f"Erro ao restaurar backup: {e}"
                    self.root.after(0, lambda: messagebox.showerror("Erro", error_msg))
                    self.log_message(error_msg, "ERROR")
                    
            threading.Thread(target=restore_in_thread, daemon=True).start()
            
    #metodos utilitarios
    def set_acceleration_level(self, level: MouseAcceleration):
        """Define o nivel de aceleracao"""
        try:
            self.accel_var.set(True)
            success = self.system_settings.enable_mouse_acceleration(level)
            
            if success:
                self.load_current_settings()
                level_names = {MouseAcceleration.LOW: "Baixo", MouseAcceleration.MEDIUM: "Médio", MouseAcceleration.HIGH: "Alto"}
                self.log_message(f"Aceleracao definida para nivel {level_names.get(level, 'Desconhecido')}")
            else:
                messagebox.showerror("Erro", "Falha ao definir o nível de aceleração")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao definir o nível de aceleração:\n{e}")
            self.log_message(f"Erro ao definir o nível de aceleração: {e}", "ERROR")
    
    def test_double_click(self):
        """Testa a velocidade do duplo clique"""
        messagebox.showinfo("Teste de Duplo CLique",
                            f"Velocidade atual: {self.dclick_vat.set()}ms\n\n"
                            "Teste fazendo duplo clique em qualquer lugar da interface.\n"
                            "Se for muito lento ou rapido, ajuste o valor e aplique.")
        
    def show_settings_summary(self):
        """Mostra um resumo das configuracoes atuais"""
        try:
            summary = self.system_settings.get_settings_summary()
            
            summary_text = "Resumo das configuracoes atuais:\n\n"
            for key, value in summary.items():
                key_formatted = key.replace('_', '').title()
                summary_text += f"{key_formatted}: {value}\n"
                
            messagebox.showinfo("Resumo das Configurações", summary_text)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao obter resumo:\n{e}")
            
    def refresh_all_data(self):
        """Atualiza todos os dados da aplicacao"""
        self.status_var.set("Atualizando todos os dados...")
        self.load_current_settings()
        self.refresh_mice_list()
        self.load_system_info()
        self.log_message("Todos os dados foram atualizados")
        
    #metodos da aba avancada
    def load_system_info(self):
        """Carrega informacoes do sistema"""
        def load_in_thread():
            try:
                system_info = self.system_settings.get_system_info()
                
                info_text = "Informacoes do Sistema:\n\n"
                
                if 'windows_version' in system_info:
                    version = system_info['windows_version']
                    info_text += f"Windows: {version.major}.{version.minor} Build {version.build}\n"
                    
                info_text += f"Privilegios Admin: {'Necessarios' if system_info.get('admin_required', True) else 'Nao necessario'}\n"
                info_text += f"Suporte Troca Botoes: {'Sim' if system_info.get('swap_button_support', False) else 'Nao'}\n"
                info_text += f"DPI Aware: {'Sim' if system_info.get('system_dpi_aware', False) else 'Nao'}\n"
                
                if 'double_click_area' in system_info:
                    area = system_info['double_click_area']
                    info_text += f"Area Duplo Clique: {area[0]}x{area[1]}pixels\n"
                    
                self.root.after(0, lambda: self._update_system_info_display(info_text))
                
            except Exception as e:
                error_text = f"Erro ao carregar informacoes do sistema:\n{e}"
                self.root.after(0, lambda: self._update_system_info_display(error_text))
                self.log_message(error_text, "ERROR")
                
        threading.Thread(target=load_in_thread, daemon=True).start()
        
    def _update_system_info_display(self, text: str):
        """Atualiza a exibicao das informacoes do sistema"""
        self.system_info_text.delete(1.0, tk.END)
        self.system_info_text.insert(1.0, text)
        
    def run_system_check(self):
        """Executa verificacao do sistema"""
        def check_in_thread():
            try:
                self.status_var.set("Executando verificação do sistema...")
                
                check_results = []
                
                #verifica deteccao de mouses
                mice_count = self.mouse_detector.get_mouse_count()
                check_results.append(f"Mouses detectados: {mice_count}")
                
                #verifica configuracoes
                try:
                    current_speed = self.system_settings.get_mouse_speed()
                    check_results.append(f"COnfiguracoes: velocidade atual {current_speed}")
                except:
                    check_results.append("Erro ao obter configuracoes de velocidade do mouse")
                
                #verifica privilegios
                admin_required = self.system_settings.is_admin_required()
                check_results.append(f"{'ixiii' if admin_required else 'daleee'} Privilegios: {'Admin necessario' if admin_required else 'Suficiente'}")
                
                result_text = "Verificacao do Sistema:\n\n" + "\n".join(check_results)
                
                self.root.after(0, lambda: messagebox.showinfo("Verificacao do Sistema", result_text))
                self.root.after(0, lambda: self.status_var.set("verificacao concluida"))
                
            except Exception as e:
                error_msg = f"Erro na verificacao: {e}"
                self.root.after(0, lambda: messagebox.showerror("Erro", error_msg))
                self.log_message(error_msg, "ERROR")
                
        threading.Thread(target=check_in_thread, daemon=True).start()
        
    def show_hid_stats(self):
        """Mostra estatisticas do dispositivos HID"""
        try:
            summary = self.mouse_detector.get_mouse_summary()
            
            stats_text = f"""Estastiticas HID:
            
Total de Mouses: {summary['total']}
• USB: {summary['usb']}
• Bluetooth: {summary['bluetooth']}
• Outros: {summary['outros']}

Última Atualização: {time.strftime('%H:%M:%S')}
Cache Ativo: {'Sim' if hasattr(self.mouse_detector, '_cache_valid') else 'Não'}
"""

            messagebox.showinfo("Estatisticas HID", stats_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Erro ao obter estatisticas:\n{e}")
            
    def run_performance_test(self):
        """Executa testes de performance"""
        def test_in_thread():
            try:
                self.status_var.get("executando teste de performance...")
                
                #teste de deteccao
                start_time = time.time()
                self.mouse_detector.get_connected_mice(force_refresh=True)
                detection_time = time.time() - start_time
                
                #teste de configuracoes
                start_time = time.time()
                self.system_settings.get_current_settings()
                settings_time = time.time() - start_time
                
                results = f"""Teste de Performance:

Detecção de Mouses: {detection_time:.3f}s
Carregamento de Configurações: {settings_time:.3f}s

Performance: {'Excelente' if detection_time < 0.5 else 'Boa' if detection_time < 1.0 else 'Lenta'}
"""

                self.root.after(0, lambda: messagebox.showinfo("teste de performance", results))
                self.root.after(0, lambda: self.status_var.set("Teste concluido"))
                
            except Exception as e:
                error_msg = f"Erro durante o teste de performance: {e}"
                self.root.after(0, lambda: messagebox.showerror("Erro", error_msg))
                self.log_message(f"error_msg, {e}")
                
        threading.Thread(target=test_in_thread, daemon=True).start()
        
    #metodos de log e utilitarios
    def log_message(self, message: str, level: str = "INFO"):
        """Adiciona mensagem ao log"""
        try:
            timestamp = time.strtime('%H:%M:%S')
            log_entry = f"[{timestamp}] {level}: {message}\n"
            
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
            
            #limite o tamanho do log
            lines = self.log_text.delete(1.0, f"{len(lines)-500}.0")
            if len(lines) > 1000:
                self.log_text.delete(1.0, f"{len(lines)-500}.0")
            
        except Exception:
            pass #isso teoricamente vai evitar loops de erro no log (euespero)
        
    def clear_log(self):
        """Limpa o log"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("Log limpo")
        
    def save_log(self):
        """salva o log em arquivo"""
        try:
            from tktinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt", 
                filetypes=[("Arquivos de texto", "*.txt"), ("All files", "*.*")],
                title="Salvar Log"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    filename.write(self.log_text.get(1.0, tk.END))
                    
                messagebox.showinfo("Sucesso", f"Log salvo em:\n{filename}")
                self.log_message(f"Log salvo em: {filename}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar o log:\n{e}")
            
    #metodos de exportacao e detlahes
    def show_deatuled_info(self):
        """Mostra informacoes detalhadas dos mouses"""
        try:
            mice = self.mouse_detector.mice_info
            
            if not mice:
                messagebox.showinfo("Informacao", "Nenhum mouse detectado.")
                return
            
            #cria janela de detalhes
            detail_window = tk.Toplevel(self.root)
            detail_window.title("Informacoes detalhadas dos Mouses")
            detail_window.geometry("800x600")
            
            #texto com scroll
            text_widget = scrolledtext.ScrolledText(detail_window, wrap=tk.WORD, font=('Consolas', 9))
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            #gera texto detalhado
            detailed_text = "🖱️ INFORMAÇÕES DETALHADAS DOS MOUSES\n"
            detailed_text += "=" * 80 + "\n\n"
            
            for i, mouse in enumerate(mice, 1):
                detailed_text += f"MOUSE {i}:\n"
                detailed_text += f"  Nome: {mouse.name}\n"
                detailed_text += f"  Fabricante: {mouse.manufacturer}\n"
                detailed_text += f"  Vendor ID: {mouse.vendor_id}\n"
                detailed_text += f"  Product ID: {mouse.product_id}\n"
                detailed_text += f"  Conexão: {mouse.connection_type}\n"
                detailed_text += f"  Serial: {mouse.serial_number}\n"
                detailed_text += f"  Release: {mouse.release_number}\n"
                detailed_text += f"  Interface: {mouse.interface_number}\n"
                detailed_text += f"  Usage Page: {mouse.usage_page}\n"
                detailed_text += f"  Usage: {mouse.usage}\n"
                detailed_text += f"  Path: {mouse.path}\n"
                detailed_text += "-" * 80 + "\n\n"
                
            text_widget.insert(1.0, detailed_text)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao exibir informações detalhadas:\n{e}")
            
    def export_mice_info(self):
        """Exporta informacoes dos mouses para arquivos"""
        try:
            from tkinter import filedialog
            import json
            
            mice = self.mouse_detector.mice_info
            
            if not mice:
                messagebox.showinfo("Informacao", "Nenhum mouse para exportar.")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON", "*.json"), ("Texto", "*.txt"), ("All files", "*.*")],
                title="Exportar Informacoes dos Mouses"
            )
            
            if filename:
                #converte para dicionario (json)
                mice_data = [asdict(mouse) for mouse in mice]
                
                if filename.endswith('.json'):
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(mice_data, f, indent=2, ensure_ascii=False)
                else:
                    with open(filename, 'w', encoding='utf-8') as f:
                        for mouse in mice:
                            f.write(f"Nome: {mouse.name}\n")
                            f.write(f"Fabricante: {mouse.manufacturer}\n")
                            f.write(f"VID: {mouse.vid}\n")
                            f.write(f"PID: {mouse.pid}\n")
                            f.write(f"Conexao: {mouse.connection_type}\n")
                            f.write(f"Serial: {mouse.serial_number}\n")
                            f.write("-" * 50 + "\n")
                            
                messagebox.showinfo("Sucesso", f"Informacoes exportadas para:\n{filename}")
                self.log_message(f"Informacoes exportadas para: {filename}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar:\n{e}")
            
    def sort_treeview(self, column):
        """Ordena o treeview por coluna"""
        try:
            items = [(self.mice_tree.set(item, column), item) for item in self.mice_tree.get_children('')]
            item.sort()
            
            for index, (val, item) in enumerate(items):
                self.mice_tree.move(item, '', index)
                
        except Exception as e:
            self.log_message(f"Erro ao ordenar o treeview: {e}", "ERROR")
            
    #Auto-refresh
    def start_auto_refresh(self):
        """Inicia o refresh automático"""
        if self.auto_refresh_enable.get():
            self.refresh_job = self.root.after(self.refresh_interval, self.auto_refresh_callback)
            
    def auto_refresh_callback(self):
        """Callback do refresh automatico"""
        if self.auto_refresh_enable.get():
            self.refresh_mice_list()
            self.refresh_job = self.root.after(self.refresh_interval, self.auto_refresh_callback)
            
        def toggle_auto_refresh(self):
            """Liga/desliga o refresh automático"""
            if self.auto_refresh_enable.get():
                self.start_auto_refresh()
                self.log_message("Auto-refresh habilitado")
            else:
                if self.refresh_job:
                    self.root.after_cancel(self.refresh_job)
                    self.refresh_job = None
                self.log_message("Auto-refresh desabilitado")
                
    def update_admin_status(self):
        """Atualiza o status de administrador"""
        try:
            admin_required = self.system_settings.is_admin_required()
            if admin_required:
                self.admin_label.config(text="Admin Req.", style='Warning.TLabel')
            else:
                self.admin_label.config(text="Privilegios OK", style='Success.TLabel')
        except:
            self.admin_label.config(text='Desconhecido', style='Error.TLabel')
            
    def on_closing(self):
        """Callback para fechamento da janela"""
        try:
            #cancela refresh automatico
            if self.refresh_job:
                self.root.after_cancel(self.refresh_job)
                
            #salva log se necessario
            self.log_message("Aplicacao encerrada")
            
            #fecha a janela
            self.root.destroy()
            
        except Exception:
            self.root.destroy()
              
    def run(self):
        """Inicia a aplicação"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
        except Exception as e:
            messagebox.showerror("Erro Fatal", f"Erro fatal na aplicação:\n{e}")
            self.root.destroy()
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
        """Configura a aba de deteccao de mouses"""
        detection_frame = ttk.Frame(self.notebook)
        self.notebook.add(detection_frame, texto="Mouses Detectados")
        
        #Frame superior com informacoes e controles
        top_frame = ttk.Frame(detection_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        #informacoes de contagem
        info_frame = ttk.LabelFrame(top_frame, text="Resumo")
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        
        self.mice_count_label = ttk.Label(into_frame, textvariable=self.mice_count_var,
                                          style='Subtitle.TLabel')
        self.mice_count_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.connection_summary_label = ttk.Label(info_frame, text="",
                                                  style='Info.TLabel')
        self.connection_summary_label.pack(anchor=tk.W, padx=5, pady=2)
        
        #botoes de controle
        control_frame = ttk.Frame(top_frame)
        control_frame.pack(side.RIGHT)
        
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
        
        for col in columns:
            self.mice_tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c))
            self.mice_tree.column(col, width=column_widths.get(col, 100), minwidth=60)
            
        # scrollbars para o treeview
        tree_scoll_frame = ttk.Frame(tree_frame)
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
        
        canvas.create_windoe((0, 0), window=scollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scollbar.set)
        
        #configuracoes principais
        self.setup_speed_settings(scollable_frame)
        self.setup_acceleration_settings(scrollable_frame)
        self.setup_click_settings(scollable_frame)
        self.setup_advanced_settings(scollable_frame)
        
        #botao de acao
        self.setup_action_buttons(scollable_frame)
        
        #pack canvas e scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        #bind mouse whell
        canvas.bind_all("<MouseWheel">, lambda e: canvas.yview_scoll(int(-1*(e.delta/120)), "units"))
        
    def setup_speed_settings(self, parent):
        """Configura controles de velocidade"""
        speed_frame = ttk.LabelFrame(parent, text="Velocidade do Mouse")
        speed_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(speed_frame, text="Velodidade (1-20):").pack(anchor=tk.W, padx=5, pady=2)
        
        speed_control_frame = ttk.Frame(speed_frame)
        speed_control_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.speed_scale = ttk.Scale(speed_contro_frame, from_=1, to=20, orient=tk.HORIZONTAL,
                                     variable=self.speed_var, command=self.on_speed_change)
        self.speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.speed_label = ttk.Label(speed_control_frame, text="10", width=3)
        self.speed_label.pack(side=tk.RIGHT, padx=(5,0))
        
        #botoes de preset
        preset_frame = ttk.Frame(speed_frame)
        preset_frame.pack(fill=tk.X, padx-5, pady=2)
        
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
        click_frame = ttkLabelFrame(parent, text="Configuracoes de Clique")
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
        shell_subframe.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(wheel_subframe, text="Linhas por scroll da roda (1-100):").pack(anchor=tk.W)
        
        wheel_control_frame = ttk.Frame(wheel_subframe)
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
        row1 = ttk.Frame(buton_frame)
        row1.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(row1, text="Aplicar configuracoes", 
                   command=self.apply_settings).pack(side=tk.LEFT, padx=2)
        ttk.Button(row1, text="Atualizar",
                   command=self,load_current_settings).pack(side=tk.LEFT, padx=2)
        ttk.Button(row1, text="Restaurar Padroes",
                   command=self.restore_defaults).pack(side=tk.LEFT, padx=2)
        
        #segunda linha de butoes
        row2 = ttk.Frame(buton_frame)
        row2.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(row2, text="Criar Backup",
                   command=self,create_backup).pack(side=tk.LEFT, padx=2)
        ttk.Button(row2, text="Restaurar Backup",
                   command=self.restore_backup).pack(side=tk.LEFT, padx=2)
        ttk.Button(row2, text="Ver Resumo",
                   command=self.show_settings_summary).pack(side=tk.LEFT, padx=2)
        
    def setup_advanced_tab(self):
        """Configura a aba de configuracoes avancadas"""
        advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(advanced_frame, text="Avancado")
        
        #informacoes do sistema
        system_frame = ttkLabelFrame(advanced_frame, text="Informacoes do Sistema")
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
                   command=self.run_performance)_test.pack(side=tk.LEFT, padx=2)
        
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
        title_frame = ttk.Frame(about_time)
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(title_frame, text="Mouse Manager MPV",
                  font('Arial', 16, 'bold')).pack()
        ttk.Label(title_frame, text="Versao 1.0.0",
                  font('Arial', 12)).pack(pady=5)
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
                               font('Arial', 9))
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
        self.admin_label = ttk.Label(status_frame, text="", relief=/tk.SUNKEN, width=15)
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
        def update_in_thread()
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
            
            
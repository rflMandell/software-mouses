"""
Mouse Manager - Universal Mouse Management Software
Main entry point for the application

Author: Rafael Mandel
Version: 1.0.0
"""

from ntpath import exists
import sys
import os
import tkinter as tk
from tkinter import messagebox 
import logging
from pathlib import Path
from typing import Required
from unittest import result

#Add the projetct root to python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root)) #trocar depois

try:
    from views.main_window import MouseManagerGUI
    from modules.mouse_detector import MouseDetector
    from modules.system_settings import system_settings
except ImportError as e:
    print(f"Import error: {e}")
    print("Certifique-se de que todos os arquios estao no local certo")
    sys.exit(1)
    

class MouseManagerApp:
    
    def __init__(self):
        self.root = None
        self.gui = None
        self.setup_logging()
        self.check_requirements()
        
    def setup_logging(self):
        """Configura o sistema de logging da aplicacao"""
        try:
            #criar diretorio de logs se nao existir
            log_dir = project_root / "logs"
            log_dir.mkdir(exist_ok=True)
            
            #configura logging
            log_file = log_dir / "mouse_manager.log"
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file, encoding='utf-8'),
                    logging.StreamHandler(sys.stdout)
                ]
            )
            
            self.logger = logging.getLogger(__name__)
            slef.logger.info("MOuse manager Iniciador!!! uwu")
            
        except Exception as e:
            print(f"Erro ao configurar logging: {e}")
            #configuracao basica de fallback
            logging.basicCOnfig(level=logging.INFO)
            self.logger = loggin.getLogger(__name__)
            
    def check_requirements(self):
        """Verifica se todos os reuisitos estao atenditos"""
        try:
            #verificar se esta rodando no windows certo"""
            if sys.platform != "win32":
                self.logger.warning("Esta aplicacao foi otimizada para o Windows")
                
            #verifica se os modulos necessarios estao disponiveis
            required_modules = ['ctypes', 'tkinter', 'threading']
            missing_modules = []
            
            for module in required_modules:
                try:
                    __import__(module)
                except ImportError:
                    missing_modules.append(module)
                    
            if missing_modules:
                error_msg = f"Modulos necessarios nao encontrados: {', '.join(missing_modules)}"
                self.logger.error(error_msg)
                raise ImportError(error_msg)
            
            #verifica permissoes
            self.check_permissions()
            
            self.logger.info("Todos os requisitos estão atendidos.")
            
        except Exception as e:
            self.logger.error(f"Erro na verificacao de requisitos: {e}")
            raise
        
    def check_permissions(self):
        """Verifica se a aplicação tem as permissões necessárias"""
        try:
            #testar acesso aos modulos principais
            detector = MouseDetector()
            settings = SystemSettings()
            
            #testar operacoes basicas
            detector.get_connected_mice()
            settings.get_mouse_speed()
            
            self.logger.info("Permissoes verificadas com sucesso")
            
        except Exception as e:
            self.logger.warning(f"Possivel problema de permissoes: {e}")
            #nao interromper a execucao, apenas avisar
            
    def create_gui(self):
        """Cria e configura a interface grafica"""
        try:
            self.root = tk.Tk()
            
            #configuracoes basicas da janela principal
            self.root.title("Mouse Manager - Universal Mouse Management Software")
            self.root.geometry("900x700")
            self.root.minsize(800, 600)
            
            #configura icone (ainda nao tem mas jaja coloco)
            self.set_window_icon()
            
            #configurar tema e estilo
            self.setup_theme()
            
            #cria a gui princiapl
            self.gui = MouseManagerGUI(self.root)
            
            #configura eventos de fechamento
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)
            
            self.logger.info("Interface grafica criada com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao criar interface grafica: {e}")
            raise
        
    def set_window_icon(self):
        """Define o icone da janela (se disponivel)"""
        try:
            icon_path = project_root / "assets" / "icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
                self.logger.info("Icone da aplicacao carregando")
        except Exception as e:
            self.logger.debug(f"Erro ao definir o icone da janela: {e}")
            
    def setup_theme(self):
        """COnfigura o tema da aplicacao"""
        try:
            #configuracoes basicas de aparencia
            self.root.configure(bg='#f0f0f0')
            
            #configurar fonte padrao
            default_font = ('Segoe UI', 9)
            self.root.option_add("*Font", default_font)
            
            self.logger.debug("tema configurado")
            
        except Exception as e:
            self.logger.debug(f"Erro ao configurar tema: {e}")
            
    def run(self):
        """Executa a aplicacao"""
        try:
            self.logger.info("Inicando Mouse Manager...")
            
            #criar interface grafica
            self.create_gui()
            
            #mostrar splash screen ou mensagem de boas vindas
            self.show_welcome_message()
            
            #iniciar loop principal
            self.logger.info("Entrando no loop principal da aplicacao")
            self.root.mainloop()
            
        except KeyboardInterrupt:
            self.logger.info("Aplicacao encerrada pelo usuario")
            self.cleanup()
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            self.show_error_dialog("Erro fatal", 
                                   f"Ocorreu um erro fatal:\n{e}\n\nA aplicacao sera fechada")
            self.cleanup()
            sys.exit(1)
            
    def show_welcome_message(self):
        """Mostra mensagem de boas vindas (fica legal e vai criar a porra toda se ja nao tiver criado)"""
        try:
            #verificar se a primeira execucao
            config_file = project_root / "config" / "first_run.flag"
            
            if not config_file.exists():
                #criar diretorio de configuracao
                config_file.parent.mkdir(exist_ok=True)
                
                #mostrar mensagem de boas vindas
                welcome_msg = (
                    "Bem vindo ao mouse manager!\n\n"
                    "Esta aplicacao permite gerenciar e configurar "
                    "todos os mouses conectados ao seu sistema.\n\n"
                    "Recursos principais:\n"
                    "• Detecção automática de mouses\n"
                    "• Configuração de sensibilidade e aceleração\n"
                    "• Backup e restauração de configurações\n"
                    "• Informações detalhadas dos dispositivos\n\n"
                    "Clique em 'Atualizar Lista' para começar!"
                )
                
                messagebox.showinfo("Bem-vindo ao Mouse Manager", welcome_msg)
                
                #criar arquivo de flag
                config_file.touch()
                
                self.logger.info("primeira execucao - mensagem de boas vindas exibida")
                
        except Exception as e:
            self.logger.debug(f"Erro ao mostrar mensagem de boas vindas: {e}")
            
    def show_error_dialog(self, title, message):
        """Mostra dialogo de error"""
        try:
            if self.root:
                messagebox.showerror(title, message)
            else:
                print(f"ERRO - {title}: {message}")
        except:
            print(f"ERRO - {title}: {message}")
            
    def on_closing(self):
        """Manipula o fechamento da aplicacao"""
        try:
            self.logger.info("Fechando aplicacao...")
            
            #salvar configuracoes se necessario
            if self.gui:
                self.gui.save_settings_on_exit()
                
            #confirmar fechamento se houver alterracoes nao salvas
            if self.confirm_exit():
                self.cleanup()
                self.root.destroy()
                
        except Exception as e:
            self.logger.error(f"Erro ao fechar aplicacao: {e}")
            self.root.destroy()
            
    def confirm_exit(self):
        """Confirma se o user deseja sair"""
        try:
            if self.gui.has_unsaved_changes():
                result = messagebox.askyesno(
                    "Confirmar Saída", 
                    "Você tem alterações não salvas.\n\n", 
                    "Deseja sair?"
                )
                
                if result is True: #sim ne burrao - salvar e sair
                    self.gui.save_all_settings()
                    return True
                elif result is False: #não - apenas sair
                    return False
                else: #cancelar
                    return False
                
            return True
        
        except Exception as e:
            self.logger.error(f"Erro ao confirmar saida: {e}")
            return True
        
    def cleanup(self):
        """limpa recursos antes de fechar"""
        try:
            self.logger.info("Limpando recursos...")
            
            #parar threads se preciso
            if self.gui:
                self.gui.cleanup()
                
            #salvar logs finais
            self.logger.info("Mouse Manager finalizado")
            
        except Exception as e:
            self.logger.error(f"Erro durante limpeza: {e}")
            
    
def main():
    "funcao principal"
    try:
        #verificar se ja existe uma instancia rodando
        # (ta bem simples, em breve deixar mais robusta e sem chance de foder alguma coisa do windows ou outro sistema operacional :))
        
        #criar e executar a aplicacao
        app = MouseManagerApp()
        app.run()
        
    except Exception as e:
        print(f"Erro fatal ao iniciar aplicacao: {e}")
        
        #tentar mostrar erro em gui (se eu conseguir)
        try:
            root = tk.Tk()
            root.withdraw() #para esconder a janel
            messagebox.showerror(
                "Erro Fatal", 
                f"Erro ao iniciar o mouse manager:\n\n{e}\n\n"
                f"Verifique os logs para mais detalhes."
            )
            root.destroy()
        except:
            pass
        
        sys.exit(1)


if __name__ == "__main__":
    main()
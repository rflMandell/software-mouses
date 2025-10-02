    """
    Modulo para gerenciar configuracoes do mouse do Windows
    Utiliza ctypes para acessar APIs do Windows de forma segura
    Versao: 1.0.0
    """
    
import ctypes
from ctypes import wintypes, byref, c_int, c_uint, c_bool, Structure, POINTER
import winreg
import sys
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import IntEnum

class MouseAcceleration(IntEnum):
    """Niveis de aceleracao do mouse"""
    DISABLE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    
@dataclass
class MouseSettings:
    """Classe de dados para configuracoes do mouse"""
    speed: int                     
    acceleration_enable: bool      
    acceleration_threshold1: int   
    acceleration_threshold2: int   
    acceleration_factor: int       
    double_click_speed: int        
    swap_buttons: bool             
    wheel_scroll_lines: int    
    hover_time: int 
    drag_width: int 
    drag_height: int 
    
class SystemMouseSettings
    """
    Gerenciador de configuracoes do mouse no Windows
    Utilizar APIs nativas do Windows para maxima compatibilidade
    """    
    
    #Constantes do Windows para SystemParametersInfo
    SPI_GETMOUSESPEED = 0x0070
    SPI_SETMOUSESPEED = 0x0071
    SPI_GETMOUSE = 0x0003
    SPI_SETMOUSE = 0x0004
    SPI_GETMOUSEBUTTONSWAP = 0x0016
    SPI_SETMOUSEBUTTONSWAP = 0x0021
    SPI_GETWHEELSCROLLLINES = 0x0068
    SPI_SETWHEELSCROLLLINES = 0x0069
    SPI_GETMOUSEHOVERTIME = 0x0066
    SPI_SETMOUSEHOVERTIME = 0x0067
    SPI_GETDRAGFULLWINDOWS = 0x0026
    SPI_SETDRAGFULLWINDOWS = 0x0025
    
    #Flags para SystemParametersInfo
    SPIF_UPDATEFILE = 0x01
    SPIF_SENDCHANGE = 0x02
    SPIF_SENDWININICHANGE = 0x02
    
    #Constantes para GetSystemMetrics
    SM_CXDRAG = 68
    SM_CYDRAG = 69
    SM_SWAPBUTTON = 23
    
    def __init__ (self):
        """Inicializa o gerenciador de configuracoes do mouse"""
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        
        #verifica se esta no windows
        if sys.platform != "win32":
            raise OSError("Este modulo funciona apenas no Windows")
        
        #Cache das configuracoes atuais
        self._settings_cache: Optional[MouseSettings] = None
        self._cache_valid = False
        
        #Configuracao padrao do Windows
        self.default_settings = MouseSettings(
            speed=10,
            acceleration_enable=True,
            acceleration_threshold1=6,
            acceleration_threshold2=10,
            acceleration_factor=1,
            double_click_speed=500,
            swap_buttons=False,
            wheel_scroll_lines=3,
            hover_time=400,
            drag_width=4,
            drag_height=4,
        )
        
    def get_mouse_speed(self) -> int:
        """ 
        Obtem a velocidade atual do mouse (1-20)
        
        Returns:
            int: Velocidade do mouse (1-20)
        """
        try:
            spped = c_int()
            result = self.user32.SystemParametersInfoW(
                self.SPI_GETMOUSESPEED,
                0,
                byref(speed),
                0
            )
            
            if result:
                #Garante que esta no range valido
                return max(1, min(20, speed.value))
            else:
                return self.default_settings.speed
            
        except Exception as e:
            print(f"Erro ao obter velocidade do mouse: {e}")
            return self.default_settings.speed
        
    def set_mouse_speed(self, speed: int) -> bool:
        """ 
        Define a velocidade do mouse (1-20)
        
        Args:
            speed(int): Nova velocidade(1-20)
            
        Returns:
            bool: True se bem-sucedido
        """
        try:
            #valida e limita o valor
            speed = max(1, min(20, int(speed)))
            
            result = self.user32.SystemParametersInfoW(
                self.SPI_SETMOUSESPEED,
                0,
                speed,
                self.SPIF_UPDATEINIFILE | self.SPIF_SENDCHANGE
            )
            
            if result:
                self._invalidate_cache()
                return True 
            else:
                return False
            
        except Exception as e:
            print(f"Erro ao definir velocidade do mouse: {e}")
            return False
        
    def get_mouse_acceleration(self) -> Tuple[int, int, int]:
        """ 
        Obtem as configuracoes de aceleracao do mouse
        
        Returns:
            TUple[int, int, int]: (threshold1, threshold2, acceleration)
        """
        try:
            mouse_params = (c_int * 3)()
            result = self.user32.SystemParametersInfoW(
                self.SPI_GETMOUSE,
                0,
                mouse_params,
                0
            )
            
            if result:
                return tuple(mouse_params)
            else:
                return (
                    self.default_settings.acceleration_threshold1,
                    self.default_settings.acceleration_threshold2,
                    self.default_settings.acceleration_factor
                )
                
        except Exception as e:
            print(f"Erro ao obter aceleracao do mouse: {e}")
            return(6,10,1)
        
    def set_mouse_acceleration(self, threshold1: int, threshold2: int, acceleration: int) -> bool:
        """ 
        Define as configuracoes de aceleracao do mouse
        
        Args:
            threshold1(int): Primeiro limiar de aceleracao (0-20)
            threshold2(int): Segundo Limiar de aceleracao (0-20)
            acceleration(int): Fator de aceleracao (0-3)
            
        Returns:
            bool: True se bem-sucedido
        """
        try:
            #valida os parametros
            threshold1 = max(0, min(20, int(threshol1)))
            threshold2 = max(0, min(20, int(threshol2)))
            acceleration = max(0, min(3, int(acceleration)))
            
            mouse_params = (c_int * 3)(threshold1, threshold2, acceleration)
            result = self.user32.SystemParametersInfoW(
                self.SPI_SETMOUSE,
                0,
                mouse_params,
                self.SPIF_UPDATEINIFILE | self.SPIF_SENDCHANGE
            )
            
            if result:
                self._invalidate_cache()
                return True 
            else:
                return False
        
        except Exception as e:
            print(f"Erro ao definir aceleracao do mouse: {e}")
            return False
        
    def enable_mouse_acceleration(self, level: MouseAcceleration = MouseAcceleration.MEDIUM) -> bool:
        """ 
        Habilita a aceleracao do mouse com nivel especificado
        
        Args:
            level (MouseAcceleration): Nivel de aceleracao
            
        Returns:
            bool: True se bem-sucedido
        """
        acceleration_configs = {
            MouseAcceleration.LOW: (4,8,1),
            MouseAcceleration.MEDIUM: (6,10,1),
            MouseAcceleration.HIGH: (8,12,2)
        }
        
        threshold1, threshold2, factor = acceleration_config.get(
            level, acceleration_configs[MouseAcceleration.MEDIUM]
        )
        
        return self.set_mouse_acceleration(threshold1, threshold2, factor)
    
    def disable_mouse_acceleration(self) -> bool:
        """ 
        Desabilita a aceleracao do mouse
        
        Returns:
            bool: True se bem sucedido
        """
        return self.set_mouse_acceleration(0,0,0)
    
    def is_acceleration_enable(self) -> bool:
        """ 
        Verifica se a aceleracao do mouse esta habilitada
        
        Returns:
            bool: True se habilitada
        """
        threshol1, thresold2, acceleration = self.get_mouse_acceleration()
        return acceleration > 0
    
    def get_double_click_speed(self) -> int:
        """ 
        Obtem a velocidade do duplo clique em milissegundos
        
        Returns:
            int: Velocidade do duplo clique em ms
        """
        try:
            return self.user32.GetDoubleClickTime()
        except Exception as e:
            print(f"Erro ao obter velocidade do duplo clique: {e}")
            return self.default_settings.double_click_speed
        
    def set_double_click_speed(self, speed_ms: int) -> bool:
        """ 
        Define a velocidade do duplo clique
        
        Args:
            speed_ms (int): Velocidade em milissegundos (100-900)
            
        Returns:
            bool: True se bem-sucedido
        """
        try:
            #valida e limita o valor
            speed_ms = max(100, min(900, int(speed_ms)))
            result = self.user32.SetDoubleClickTime(speed_ms)
            
            if result:
                self._invalidate_cache()
                return True 
            else:
                return False 
            
        except Exception as e:
            print(f"Erro ao definir velocidade do duplo clique: {e}")
            return False
        
    def get_button_swap(self) -> bool:
        """ 
        Verifica se os botoes dom ouse estao trocados
        
        Returns:
            bool: True se os otoes estao trocados
        """
        try:
            swap = c_bool()
            result = self.user32.SystemParametersInfoW(
                self.SPI_GETMOUSEBUTTONSWAP,
                0,
                byref(swap),
                0
            )
            
            if result:
                return swap.value
            else:
                return self.default_settings.swap_buttons
            
        except exception as e:
            print(f"Erro ao obter troca de botoes: {e}")
            return False
        
    def set_button_swap(self, swap: bool) -> bool:
        """ 
        Define se os botoes do mouse devem ser trocados
        
        Args:
            swap (bool): True para trocar os botoes
            
        Returns:
            bool: True se bem-sucedido
        """
        try:
            result = self.user32.SystemParametersInfoW(
                self.SPI_SETMOUSEBUTTONSWAP,
                1 if swap else 0,
                None,
                self.SPIF_UPDATEINIFILE | self.SPIF_SENDCHANGE
            )
            
            if result:
                self._invalidate_cache()
                return True 
            else:
                return False
            
        except Exception as e:
            print(f"Erro ao definir troca de botoes: {e}")
            return False
        
    def get_wheel_scroll_lines(self) -> int:
        """ 
        Obtem o numero de linhas por scroll da roda
        
        Returns:
            int: Numero de linhas por scroll
        """
        try:
            lines = c_uint()
            result = self.user32.SystemParametersInfoW(
                self.SPI_GetWHEELSCROLLLINES,
                0,
                byref(lines),
                0
            )
            
            if result:
                return max(1, min(100, lines.value))
            else:
                return self.default_settings.wheel_scroll_lines
            
        except Exception as e:
            print(f"Erro ao obter linhas de scroll: {e}")
            return 3
        
    def set_wheel_scroll_lines(self, lines: int) -> bool:
        """ 
        Define o numero de linhas por scroll da roda
        
        Args:
            lines (int): numero de linhas (1-100)
            
        Returns:
            bool: True se bem-sucedido
        """
        try:
            #valida e limita o valor
            lines = max(1, min(100, int(lines)))
            
            result = self.user32.SystemParametersInfoW(
                self.SPI_SETWHEELSCROLLLINES,
                lines,
                None,
                self.SPIF_UPDATEINIFILE | self.SPIF_SENDCHANGE
            )
            
            if result:
                self._invalidate_cache()
                return True 
            else:
                return False
            
        except Exception as e:
            print(f"Erro ao definir linhas de scroll: {e}")
            return False
        
    def get_hover_time(self) -> int:
        """ 
        Obtem o tempo de hover em milissegundos
        
        Returns:
            int: Tempo de hover em ms
        """
        try:
            hover_time = c_uint()
            result = self.user32.SystemParamantersInfoW(
                self.SPI_GETMOUSEHOVERTIME,
                0,
                byref(hover_time),
                0
            )
            
            if result:
                return hover_time.value
            else:
                return self.default_settings.hover_time
            
        except Exception as e:
            print(f"Erro ao obter tempo de hover: {e}")
            return 400
    
    def set_hover_time(self, time_ms: int) -> bool:
        """ 
        Define o tempo de hover
        
        Args:
            time_ms(int): Tempo em milissegundos (100-2000)
            
        Returns:
            bool: True se bem-sucedido
        """
        try:
            #valida e limita o valor
            time_ms = max(100, min(2000, int(time_ms)))
            
            result = self.user32.SystemParametersInfoW(
                self.SPI_SETMOUSEHOVERTIME,
                time_ms,
                None,
                self.SPIF_UPDATEINIFILE | self.SPIF_SENDCHANGE
            )
            
            if result:
                self._invalidate_cache()
                return True 
            else:
                return False
            
        except Exception as e:
            print(f"Erro ao definir tempo de hover: {e}")
            return False
        
    def get_drag_dimensions(self) -> Tuple[int, int]:
        """ 
        Obtem as dimensoes da area de drag
        
        Returns:
            Tuple[int, int]: (largura, altura) em pixels
        """
        try:
            width = self.user32.GetSystemMetrics(self.SM_CXDRAG)
            height = self.user32.GetSystemMetrics(self.SM_CYDRAG)
            return (width, height)
        except Exception as e:
            print(f"Erro ao obter dimensoes de drag: {e}")
            return (4, 4)
        
    def get_current_settings(self) -> MouseSettings:
        """ 
        Obtem todas as configuracoes atuais do mouse
        
        Returns:
            MouseSettings: objeto com todas as configuracoes
        """
        if self._cache_valid and self._settings_cache:
            return self._settings_cache
        
        try:
            threshold1, threshold2, acceleration = self.get_mouse_acceleration()
            drag_widht, drag_height = self.get_drag_dimensions()
            
            seetings = MouseSettings(
                speed= self.get_mouse_speed(),
                acceleration_enable = self.is_acceleration_enable(),
                acceleration_threshold1=threshold1,
                acceleration_threshold2=threshold2,
                acceleration_factor=acceleration,
                double_click_speed=self.get_double_click_speed(),
                swap_buttons=self.get_button_swap(),
                wheel_scroll_lines=self.get_whell_scroll_lines(),
                hover_time=self.get_hover_time(),
                drag_width=drag_width,
                drag_height=drag_height
            )
            
            #atualiza o cache
            self._settings_cache = settings 
            self._cache_valid = True 
            
            return settings 
        
        except Exception as e:
            print(f"Erro ao obter configuracoes: {e}")
            return self.default_settings
        
    def apply_settings(self, settings: MouseSettings) -> Dict[str, bool]:
        """ 
        Aplica um conjunto completo de configuracoes
        
        Args:
            settings (MouseSettings): Configuracoes a serem aplicadas
            
        Returns:
            Dict[str, bool]: Resultado de cada configuracao aplicada
        """
        results: {}
        
        try:
            results['speed'] = self.set_mouse_speed(settings.speed)
            results['acceleration'] = self.set_mouse_acceleration(
                settings.acceleration_threshold1,
                settings.acceleration_threshold2,
                settings.acceleration_factor
            )
            results['double_click'] = self.set_double_click_speed(settings.double_click_speed)
            result['button_swap'] = self.set_button_swap(settings.swap_button)
            result['wheel_scroll'] = self.set_wheel_scrool_lines(settings.wheel_scroll_lines)
            results['hover_time'] = self.set_hover_time(settings.hover_time)
            
        except Exception as e:
            print(f"Erro ao aplicar configuracoes: {e}")
            #marca todas as configuracoes como falhadas
            for key in results:
                if key not in results:
                    results[key] = False
        
        return results
    
    def restore_defaults(self) -> Dict[str, bool]:
        """ 
        Restaura todas as cofniguracoes para os valores padrao
        
        Return:
            Dict[str, bool]: resultado da restauracao de cada configuracao
        """
        return self.apply_settings(self.default_settings)
    
    def backup_settings(self) -> MouseSettings:
        """ 
        Cria um backup das configuracoes atuais
        
        Returns:
            MouseSettings: backup das configuracoes atuais
        """
        return self.get_current_settings()
    
    def restore_from_backup(self, backup: MouseSettings) -> Dict[str,bool]:
        """ 
        Restaura configuracoes a partir de um backup
        
        Args:
            backup (MouseSettings): Backup das configuracoes
            
        Returns:
            Dict[str,bool]: resultado da restauracao
        """
        return self.apply_settings(backup)
    
    def get_settings_summary(self) -> Dict[str, Any]:
        """ 
        retorna um resumo das configuracoes atuais
        
        Returns:
            Dict[str, Any]: resumo das configuracoes
        """
        settings = self.get_current_settings()
        
        return {
            'velocidade': f"{settings.speed}/20",
            'aceleracao': "Habilitada" if settings.acceleration_enable else "Desabailitada",
            'duplo_clique': f"{settings.double_click_speed}ms",
            'botoes_trocados': "sim" if settings.swap_buttons else "Nao",
            'linhas_scroll': f"{settings.wheel_scroll_lines}linhas",
            'tempo_hover': f"{settings.hover_time}ms",
            'area_drag': f"{settings.drag_width}x{settings.drag_height}px"
        }
        
    def _invalidate_cache(self):
        """Invalida o cache de configuracoes"""
        self._cache_valid = False
        self._settings_cache = None
        
    def is_admin_required(self) -> bool:
        """ 
        Verifica se privilegios administrativos sao necessarios
        
        Returns:
            bool: True se admin e necessario
        """
        try:
            #tenta um operacao que pode requerer admin
            return not bool(ctypes.windll.shell32.IsUserAnAdmin())
        except:
            return True 
        
    def get_system_info(self) -> Dict[str, Any]:
        """ 
        Obtem informacoes do sistema relacionadas ao mouse
        
        Returns:
            Dict[str, Any]: informacoes do sistema
        """
        try:
            return{
                'windows_version': sys.getwindowsversion(),
                'admin_required': self.is_admin_required(),
                'swap_button_support': bool(self.user32.GetSystemMetrics(self.SM_SWAPBUTTON)),
                'double_click_area': self.get_drag_dimensions(),
                'system_dpi_aware': bool(self.user32.IsProcessDPIAware())
            }
        except Exception as e:
            print(f"Erro ao obter informacoe do sistema: {e}")
            return {}
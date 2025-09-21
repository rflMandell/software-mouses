"""
Modulo para detectar mouses conectados via HID
Ira ser utilizada o hidapi para detectar HID
Versao: 1.0.0
"""

import hid
import re
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class MouseInfo:
    """Classe de dados para informacoes do mouse"""
    name: str
    manufacturer: str
    vendor_id: str
    product_id: str
    connection_type: str
    serial_number: str
    path: str
    interface_number: str
    release_number: str
    usage_page: int
    usage: int
    
class MouseDetector:
    """
    Detector de mouses conectados via HID
    Suporta deteccao de mouses genericos USB e Bluetooth
    """
    
    #Constantes HID para mouses
    GENERIC_DESKTOP_PAGE = 0x01
    MOUSE_USAGE = 0x02
    
    #palavras-chave para identificacao de mouses
    MOUSE_KEYWORDS = [
        'mouse', 'mice', 'pointing', 'cursor', 'optical', 'wireless',
        'gaming', 'trackball', 'touchpad', 'pointer'
    ]
    
    # VIDs conhecidos de fabricantes de mouses
    KNOWN_MOUSE_VENDORS = {
        0x046D: 'Logitech',
        0x1532: 'Razer',
        0x0458: 'KYE Systems',
        0x093A: 'Pixart Imaging',
        0x275D: 'Pixart Imaging',
        0x1BCF: 'Sunplus Innovation',
        0x248A: 'Maxxter',
        0x18F8: 'Elecom',
        0x062A: 'MosArt Semiconductor',
        0x0E8F: 'GreenAsia',
        0x1EA7: 'SHARKOON Technologies',
        0x25A7: 'Areson Technology',
        0x04F2: 'Chicony Electronics',
        0x413C: 'Dell Computer',
        0x17EF: 'Lenovo',
        0x045E: 'Microsoft'
    }
    
    def __init__(self):
        """Inicializa o detector de mouses"""
        self.mice_info: List[MouseInfo] = []
        self.last_scan_time: float = 0
        self.scan_cache_duration: float = 2.0 #cache por 2 secs
        
    def get_connected_mice(self, force_refresh: bool = False) -> List[MouseInfo]:
        """
        Detecta todos os mouses conectados ao sistema
        
        Args:
            force_refresh (bool): forca uma nova varredura ignorando cache
            
        Return:
            List[MouseInfo]: Lista com informacoes dos mouses detectados
        """
        current_time = time.time()
        
        # Usa cache se n forcar refresh e estuver dentro do tempo
        if not force_refresh and (current_time - self.last_scan_time) < self.scan_cache_duration:
            return self.mice_info
        
        self.mice_info = []
        
        try:
            #enumera todos os dispositivos HID
            devices = hid.enumerate()
            
            for device in devices:
                #filtra apenas dispositivos que sao mouses
                if self._is_mouse_device(device):
                    mouse_info = self._extract_mouse_info(device)
                    if mouse_info:
                        self.mice_info.append(mouse_info)
            
            #remove duplicatas baseado no path
            self.mice_info = self._remove_duplicates(self.mice_info)
            
            #ordena por nome para consistencia
            self.mice_info.sort(key=lambda x: x.name.lower())
            
            self.last_scan_time = current_time
            
        except Exception as e:
            print(f"Erro ao detectar mouses: {e}")
            # Em caso de erro, retorna lista vazia mas nao quebra
            self.mice_info = []
            
        return self.mice_info


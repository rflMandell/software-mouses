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

    def _is_mouse_is_device(self, device: Dict) -> bool:
        """
        Verific se o dispositivo e um mouse usando multiplos criterios
        
        Args:
            device (Dict): Informacoes do dispositivo HID
            
        Returns:
            bools: True se for um mouse
        """
        #Criterio 1: Usage Page e um Usage padrao HID
        usage_page = device.get('usage_page', 0)
        usage = device.get('usage', 0)
        
        if usage_page == self.GENERIC_DESKTOP_PAGE and usage == self.MOUSE_USAGE:
            return True
        
        #criterio 2: verifica pelo nome do produto
        product_string: device.get('product_string', '').lower()
        if any(keyword in product_string for keyword in self.MOUSE_KEYWORDS):
            return True
        
        #criterio 3: verifica VID de fabricantes conhecidos de mouses
        vendor_id = device.get('vendor_id', 0)
        if vendor_id in self.KNOWN_MOUSE_VENDORS:
            #para VIDs conhecidos, verifica se nao e teclado ou outro dispositovo
            if not any(exclude in product_string for exclude in ['keyboard', 'headset', 'webcam']):
                return True
        
        #criterio 4: interface especifica de mouse (interface 0 geralmente e um mouse)
        interface_number = device.get('interface_number', -1)
        if interface_number == 0 and usage_page == self.GENERIC_DESKTOP_PAGE:
            return True
        
        return False
    
    def _extract_mouse_info(self, device: Dict) -> Optional[MouseInfo]:
        """
        Extrai informacoes relevantes do mouse
        
        Args:
            device (Dict): informacoes do dispositivo HID
            
        Returns:
            Optional[MouseInfo]: informacoe formatadas do mouse
        """
        try:
            vendor_id = device.get('vendor_id', 0)
            product_id = device.get('product_id', 0)
            
            #nome do produto com fallback inteligente
            name = self._get_device_name(device, vendor_id, product_id)
            
            #fabricante com fallback para VIDs conhecidos
            manufacturer = self._get_manufacturer(device, vendor_id)
            
            #determina o tipo de conexao
            connection_type = self._get_connection_type(device.get('path', b''))
            
            #numero serial com tratamento especial
            serial_number = self._get_serial_number(device)
            
            #release number formatado
            release_number = self._format_release_number(device.get('release_number', 0))
            
            mouse_info = MouseInfo(
                name=name,
                manufacturer=manufacturer,
                vendor_id=f"0x{vendor_id:04X}",
                product_id=f"0x{product_id:04X}",
                connection_type=connection_type,
                serial_number=serial_number,
                path=device.get('path', b'').decode('utf-8', errors='ignore'),
                interface_number=device.get('interface_number', -1),
                release_number=release_number,
                usage_page=device.get('usage_page', 0),
                usage=device.get('usage', 0)
            )
            
            return mouse_info
        
        except Exception as e:
            print(f"Erro ao extrair informacoes do mouse: {e}")
            return None
        
    def _get_device_name(self, device: Dict, vendor_id: int, product_id: int) -> str:
        """Obtem o nome do dispositivo com fallback inteligentes"""
        name = device.get('product_string', '').strip()
        
        if name:
            return name
        
        #fallback para VIDs conhecidos
        if vendor_id in self.KNOWN_MOUSE_VENDORS:
            manufacturer = self.KNOWN_MOUSE_VENDORS[vendor_id]
            return f"{manufacturer} Mouse (PID: 0x{product_id:04X})"
        
        #fallback generico
        return f"Mouse generico (VID: 0x{vendor_id:04X}, PID: 0x{product_id:04X})"
    
    def _get_manufacturer_name(self, device: Dict, vendor_id: int) -> str:
        """Obtem o nome do fabricante com fallback para VIDs conhecidos"""
        manufacturer = device.get('manufacturer_string', '').strip()
        
        if manufacturer:
            return manufacturer
        
        #fallback para VIDs conhecidos
        if vendor_id in self.KNOWN_MOUSE_VENDORS:
            return self.KNOWN_MOUSE_VENDORS[vendor_id]
        
        return f"Fabricante Desconhecido (VID: 0x{vendor_id:04X})"
    
    def _get_connection_type(self, path: byts) -> str:
        """
        Determina o tipo de conexao baeasdo no path do dispositivo
        
        Args:
            path(bytes): Path do dispositivo
            
        Returns:
        str: tipo de conexao detalhado
        """
        try:
            path_str = path.decode('utf-8', errors='ignore').lower()
            
            #analise mais detalhada do path
            if 'usb' in path_str:
                if 'vid_' in path_str and 'pid' in path_str:
                    return 'USB'
                else:
                    return 'USB (Generico)'
            elif any(bt_indicator in path_str for bt_indicator in ['bluetooth', 'bth', 'bthle']):
                return 'Bluetooth'
            elif 'hid' in path_str:
                if 'i2c' in path_str:
                    return 'I2C HID'
                else:
                    return 'HID'
            elif 'ps2' in path_str or 'ps/2' in path_str:
                return 'PS/2'
            else:
                return 'Desconhecido'
            
        except Exception:
            return 'Erro na Deteccao'
        
    def _get_serial_number(self, device: Dict) -> str:
        """Obtem o numero serial com tratamento especial"""
        serial = device.get('serial_number', '')
        
        if not serial or serial.strip() == '':
            return 'N/A'
        
        #remove caracteres espediais e espacos extras
        serial = serial.strip()
        
        #se for muito longo trunca
        if len(serial) > 50:
            serial = serial[:47] + '...'
            
        return serial
    
    def _format_release_number(self, release_number: int) -> str:
        """Formatar o numero de release em formate legivel"""
        if release_number == 0:
            return 'N/A'
        
        #converte para formato BCD se necessario
        major = (release_number >> 8) & 0xFF
        minor = release_number & 0xFF
        
        return f"{major}.{minor:02d}"
    
    def _remove_duplicates(self, mice_list: List[MouseInfo]) -> List[MouseInfo]:
        """Remove mouses duplicados baseado no path"""
        seen_paths = set()
        unique_mice = []
        
        for mouse in mice_list:
            if mouse.path not in seen_paths:
                seen_paths.add(mouse.path)
                unique_mice.append(mouse)
                
            return unique_mice
        
    def get_mouse_count(self) -> int:
        """
        Retorna o numero de mouses detectados
        
        Returns:
            int: numero de mouses unicos
        """
        return len(self.mice_info)
    
    def refresh_mice_list(self) -> List[MouseInfo]:
        """
        Forca uma atualizacao da lista de mouses conectados
        
        Returns:
            List[MousesINfo]: lista atualizada de mouses
        """
        return self.get_connected_mice(force_refresh=True)
    
    def get_mice_by_connection_type(self, connection_type: str) -> List[MouseInfo]:
        """
        Filtra mouses por tipo de conexao
        
        Args:
            connection_type (str): tipo de conexao (USB, Bluetooth, etc.)
            
        Returns:
            List[MouseInfo]: Mouses do tipo especifico
        """
        return [mouse for mouse in self.mice_info
                if mouse.connection_type.lower() == connection_type.lower()]
    
    
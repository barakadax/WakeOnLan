import re
import socket
import binascii
import ipaddress

class WOL(object):
    '''
        Class that creates Wake On Lan massages and broadcasts.\n
        Method to run: Execute(mac addresses list, IP addresses list) 
    '''
    def __init__(self) -> None:
        self.port = 9
        self.socket = None
        self.ip_list = []
        self.mac_list = []
        self.broadcast = 'ff' * 6
        self.mac_address_regex = "^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"

    def Execute(self, mac_addresses: list, ip_addresses: list) -> dict:
        '''
            Function creates the wake on lan messages and broadcasts.\n
            First parameter list of mac addresses.\n
            Second parameter list of IP addresses.\n
            Returns all mac & IP addresses that couldn't be used.
        '''
        self.__validate_ip_addresses(ip_addresses)
        self.__validate_mac_addresses(mac_addresses)
        self.__open_socket()
        self.__internal_execute()
        self.__close_socket_and_clean_lists()
        return {"mac" : [set(mac_addresses) - set(self.mac_list)], "IP" : [set(ip_addresses) - set(self.ip_list)]}
    
    def __validate_ip_addresses(self, ip_addresses: list) -> None:
        for ip in ip_addresses:
            try:
                self.ip_list.append(ipaddress.ip_address(ip).compressed)
            except ValueError:
                pass

    def __validate_mac_addresses(self, mac_addresses: list) -> None:
        self.mac_list =  [mac for mac in mac_addresses if re.match(self.mac_address_regex, mac)]

    def __open_socket(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def __close_socket_and_clean_lists(self) -> None:
        self.ip_list = []
        self.mac_list = []
        self.socket.close()

    def __internal_execute(self) -> None:
        for ip_address in self.ip_list:
            for mac_address in self.mac_list:
                self.__wake_on_lan(mac_address, ip_address)

    def __wake_on_lan(self, mac: str, ip: str) -> None:
        wake_on_lan_message = self.__generate_message(mac)
        self.socket.sendto(wake_on_lan_message, (ip, self.port))

    def __generate_message(self, mac: str) -> bytes:
        normalized_mac = mac.replace(':', '').replace('-', '')
        mac_message = normalized_mac * 16
        return binascii.unhexlify(self.broadcast + mac_message)

import csv
import requests
import socket
import time
from scapy.all import ARP, Ether, srp
import nmap
from .os_detector import OSDetector  # Assurez-vous que le chemin d'importation est correct

class NetworkTools:
    def __init__(self):
        self.discovered_macs = set()
        self.last_api_request_time = 0
        self.api_request_interval = 4  # seconds between API requests
        self.scanner = nmap.PortScanner()
        self.os_detector = OSDetector()
        self.mac_address_file = 'discovered_macs.csv'  # Nom du fichier pour les adresses MAC

    def scan_network(self, target_range):
        print(f"Scanning network range: {target_range}")
        self.scanner.scan(hosts=target_range, arguments='-sn')
        hosts_up = []
        for host in self.scanner.all_hosts():
            if self.scanner[host].state() == 'up':
                hostname = self.resolve_hostname(host)  # Utilisation de la résolution explicite
                hosts_up.append({'ip': host, 'hostname': hostname, 'status': 'up'})
        return hosts_up

    def resolve_hostname(self, ip_address):
        try:
            # Tentative de résolution du nom d'hôte via socket
            hostname = socket.gethostbyaddr(ip_address)[0]
            return hostname
        except socket.herror:
            # Si la résolution échoue, retourner "Unknown"
            return "Unknown"

    def resolve_mac_and_company(self, ip_address):
        arp_request = ARP(pdst=ip_address)
        broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast/arp_request
        answered, unanswered = srp(arp_request_broadcast, timeout=1, verbose=False)
        if answered:
            mac_address = answered[0][1].hwsrc
            company_name = self.get_company_from_csv(mac_address)
            if company_name == 'Unknown':
                company_name = self.lookup_vendor(mac_address)
                self.save_to_csv(mac_address, company_name)
            return mac_address, company_name
        return None, None

    def is_printer(self, ip_address):
        print_ports = [9100, 515]
        for port in print_ports:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                result = sock.connect_ex((ip_address, port))
                if result == 0:
                    return True
        return False

    def lookup_vendor(self, mac_address):
        # Attendre si nécessaire avant de faire une nouvelle requête API
        if time.time() - self.last_api_request_time < self.api_request_interval:
            time.sleep(self.api_request_interval - (time.time() - self.last_api_request_time))
        self.last_api_request_time = time.time()
        # Faire la requête à l'API
        return self.fetch_company_name_from_api(mac_address)

    def fetch_company_name_from_api(self, mac_address):
        api_url = f"https://api.macvendors.com/{mac_address}"
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                return response.text.strip()
            return 'Unknown'
        except Exception:
            return 'Unknown'

    def save_to_csv(self, mac_address, company_name):
        with open(self.mac_address_file, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([mac_address, company_name])

    def get_company_from_csv(self, mac_address):
        try:
            with open(self.mac_address_file, newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row[0] == mac_address:
                        return row[1]
        except FileNotFoundError:
            # Si le fichier n'existe pas, retourner 'Unknown'
            pass
        return 'Unknown'

    def detect_os_for_network(self, ip_addresses):
        return self.os_detector.detect_os_threaded(ip_addresses)

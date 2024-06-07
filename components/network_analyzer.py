import json
import os
from datetime import datetime
from threading import Thread
from .network_tools import NetworkTools  # Assurez-vous que le chemin d'importation est correct

class NetworkAnalyzer:
    def __init__(self, target_range):
        self.target_range = target_range
        self.network_tools = NetworkTools()

    def analyze_network_and_save_results(self):
        active_hosts = self.network_tools.scan_network(self.target_range)
        detailed_hosts_info = []

        def analyze_host(host):
            ip_address = host['ip']
            hostname = host.get('hostname', 'Unknown')
            mac_address, company_name = self.network_tools.resolve_mac_and_company(ip_address)
            is_printer = self.network_tools.is_printer(ip_address)

            # Affichage des informations recueillies pour chaque hôte
            print(f"Host: {ip_address}, Hostname: {hostname}, MAC: {mac_address}, Manufacturer: {company_name}, Is Printer: {is_printer}")

            host_info = {
                "ip_address": ip_address,
                "hostname": hostname,
                "mac_address": mac_address,
                "manufacturer": company_name,
                "is_printer": is_printer,
                "os_info": "Pending Detection"
            }
            detailed_hosts_info.append(host_info)

        threads = [Thread(target=analyze_host, args=(host,)) for host in active_hosts]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.detect_os_in_parallel(detailed_hosts_info)
        self.save_results_to_json(detailed_hosts_info)

    def detect_os_in_parallel(self, hosts_info):
        def detect_os(host_info):
            ip_address = host_info["ip_address"]
            os_info = self.network_tools.detect_os_for_network([ip_address]).get(ip_address, "Unknown")
            host_info["os_info"] = os_info

        os_threads = [Thread(target=detect_os, args=(host_info,)) for host_info in hosts_info]
        for thread in os_threads:
            thread.start()
        for thread in os_threads:
            thread.join()

        print("OS detection completed.")

    def save_results_to_json(self, results):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        directory = 'results'
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, f"network_analysis_results_{timestamp}.json")
        with open(file_path, 'w') as file:
            json.dump(results, file, indent=4)
        print(f"Network analysis results saved to {file_path}")


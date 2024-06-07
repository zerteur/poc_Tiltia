# components/os_detector.py

import threading
import nmap

class OSDetector:
    def __init__(self):
        self.scanner = nmap.PortScanner()

class OSDetector:
    def __init__(self):
        self.scanner = nmap.PortScanner()

    def detect_os(self, ip_address):
        # Combinaison des options pour un scan approfondi
        scan_options = "-O --fuzzy -sV"
        try:
            self.scanner.scan(ip_address, arguments=scan_options)
            if 'osmatch' in self.scanner[ip_address]:
                for osmatch in self.scanner[ip_address]['osmatch']:
                    if osmatch['name']:
                        return osmatch['name']
            return "Unknown"
        except nmap.PortScannerError:
            return "Scan Error"
        except KeyError:
            return "Not Detected"

    def detect_os_threaded(self, ip_addresses):
        print(f"Starting OS detection for {len(ip_addresses)} IP addresses...")
        os_results = {}
        threads = []

        def detect_and_store(ip_address):
            os_info = self.detect_os(ip_address)
            os_results[ip_address] = os_info
            print(f"OS detected for {ip_address}: {os_info}")

        for ip_address in ip_addresses:
            thread = threading.Thread(target=detect_and_store, args=(ip_address,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        print("OS detection completed.")
        return os_results

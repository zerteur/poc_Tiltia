import subprocess
import re
import logging
import threading
import json
from datetime import datetime
import socket
import os
import argparse

# Configurer le logging
logging.basicConfig(filename='network_scan.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Limite le nombre de threads actifs à 50
max_threads = 50
semaphore = threading.Semaphore(max_threads)
scan_results = []


def run_command(command):
    logging.info(f"Running command: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        logging.info(f"Command output: {result.stdout}")
    else:
        logging.error(f"Command failed with error: {result.stderr}")
    return result.stdout


def scan_network(ip_range):
    command = f"nmap -sP -R {ip_range}"
    result = run_command(command)
    return parse_hosts(result)


def parse_hosts(nmap_output):
    hosts = []
    lines = nmap_output.split('\n')
    for line in lines:
        if "Nmap scan report for" in line:
            current_host = {"ip": "Unknown", "hostname": "Unknown"}
            if '(' in line and ')' in line:
                current_host["hostname"] = line.split('(')[-1].split(')')[0]
                current_host["ip"] = line.split(' ')[-1].split('(')[0]
            else:
                current_host["ip"] = line.split(' ')[-1]
            if current_host not in hosts:
                hosts.append(current_host)
            logging.debug(f"Host found: {current_host}")
    return hosts


def resolve_hostname(ip):
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        logging.info(f"Hostname resolved using socket for {ip}: {hostname}")
        return hostname
    except (socket.herror, socket.gaierror):
        logging.warning(f"Hostname resolution failed using socket for {ip}")

    command = f"nslookup {ip}"
    result = run_command(command)
    match = re.search(r"Name:\s*(.*)", result)
    if match:
        hostname = match.group(1).strip()
        logging.info(f"Hostname resolved using nslookup for {ip}: {hostname}")
        return hostname

    return "Unknown"


def detect_os_and_ports(ip):
    ports = "21,22,23,25,53,80,110,139,143,443,445,515,587,631,8080,9100,3389"
    command = f"nmap -O -p {ports} {ip}"
    result = run_command(command)
    return parse_os_and_ports(result)


def parse_os_and_ports(nmap_output):
    os_details = {'os_info': 'Unknown', 'details': 'Unknown', 'ports': [], 'mac_address': 'Unknown',
                  'manufacturer': 'Unknown', 'is_printer': False}

    os_match = re.search(r"Running: (.*)", nmap_output)
    if os_match:
        os_details['os_info'] = os_match.group(1)
        logging.debug(f"OS detected: {os_match.group(1)}")

    kernel_match = re.search(r"OS details: (.*)", nmap_output)
    if kernel_match:
        os_details['details'] = kernel_match.group(1)
        logging.debug(f"OS details: {kernel_match.group(1)}")

    ports = re.findall(r"(\d{1,5})/tcp open", nmap_output)
    if ports:
        os_details['ports'] = ports
        logging.debug(f"Ports detected: {ports}")

    mac_match = re.search(r"MAC Address: ([0-9A-F:]+) \((.*)\)", nmap_output)
    if mac_match:
        os_details['mac_address'] = mac_match.group(1)
        os_details['manufacturer'] = mac_match.group(2)
        logging.debug(f"MAC Address: {mac_match.group(1)}, Manufacturer: {mac_match.group(2)}")

    # Check if it's a printer
    os_details['is_printer'] = any(port in ['515', '631', '9100'] for port in os_details['ports'])

    return os_details


def analyze_host(host):
    with semaphore:
        ip_address = host['ip']
        hostname = resolve_hostname(ip_address)
        host['hostname'] = hostname if hostname else host['hostname']
        print(f"Analyzing {ip_address} with hostname {hostname}...")
        os_info = detect_os_and_ports(ip_address)
        host_info = {
            "ip_address": ip_address,
            "hostname": host["hostname"],
            **os_info
        }
        print(f"Information for {ip_address}: {host_info}")
        logging.info(f"Information for {ip_address}: {host_info}")
        scan_results.append(host_info)


def save_results_to_json(filename):
    # Create results directory if it doesn't exist
    if not os.path.exists('C:/Users/lproudhom/Documents/Web/Alt/results'):
        os.makedirs('results')

    filepath = os.path.join('C:/Users/lproudhom/Documents/Web/Alt/results', filename)
    with open(filepath, 'w') as json_file:
        json.dump(scan_results, json_file, indent=4)
        logging.info(f"Results saved to {filepath}")


def main(ip_range=None):
    if not ip_range:
        ip_range = input("Enter the IP range to scan (e.g., 192.168.1.0/24): ")

    logging.info(f"Starting network scan for IP range: {ip_range}")
    print("Scanning the network...")
    hosts = scan_network(ip_range)
    print("Hosts found:", [host['ip'] for host in hosts])

    threads = []
    for host in hosts:
        thread = threading.Thread(target=analyze_host, args=(host,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Generate a filename based on the current date and time
    filename = f"network_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    # Save results to JSON
    save_results_to_json(filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Network scanner script")
    parser.add_argument("ip_range", nargs='?', help="IP range to scan (e.g., 192.168.1.0/24)")
    args = parser.parse_args()
    main(args.ip_range)

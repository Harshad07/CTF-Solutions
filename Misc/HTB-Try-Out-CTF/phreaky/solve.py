import dpkt
import re
import base64
import pyzipper

complete_data = []
passwords = []
def data_connect(data):
    pattern1 = r'>([^-]+)-'
    data = data.decode() 
    if "Password: " in data:
        data = data.split("Password: ")[1]  
        passwords.append(data[:12]) 
        matches = re.findall(pattern1, data)  
        if not matches:
            data_seg =  data.split(">")[-1]
        else: 
            data_seg = matches[0]
        complete_data.append(data_seg)  
    elif  "--=-=" in data:
        data_seg =  data.split("--=-=")[0]
        complete_data[-1] = complete_data[-1] + data_seg 
 

def reconstruct_smtp_messages(pcap_file):
    with open(pcap_file, 'rb') as f:
        pcap = dpkt.pcap.Reader(f)
        connections = {}  # To store ongoing TCP connections
        for ts, buf in pcap:
            eth = dpkt.ethernet.Ethernet(buf)
            if isinstance(eth.data, dpkt.ip.IP):
                ip = eth.data
                if isinstance(ip.data, dpkt.tcp.TCP):
                    tcp = ip.data
                    if tcp.dport == 80 or tcp.dport == 443 or tcp.sport == 80 or tcp.sport == 443:
                        continue  # Skip HTTP/HTTPS packets

                    # Define a tuple to represent the connection (src_ip, src_port, dst_ip, dst_port)
                    connection = (ip.src, tcp.sport, ip.dst, tcp.dport)
                    
                    # Check if we've seen this connection before
                    if connection not in connections:
                        connections[connection] = b''  # Initialize buffer for this connection
                    
                    # Append TCP payload to the connection buffer
                    connections[connection] += tcp.data
                    
                    # Check if we have a complete SMTP message (example: ending with '\r\n\r\n')
                    smtp_data = connections[connection]
                    if b'\r\n\r\n' in smtp_data: 
                        data_connect(smtp_data) 
                        del connections[connection]

def unzip_file_with_password(zip_file_path, extract_to_dir, password):
    with pyzipper.AESZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.pwd = password.encode('utf-8')
        zip_ref.extractall(extract_to_dir)
        print(f"Extracted {zip_file_path} to {extract_to_dir}")

def create_zip(zip_content, zip_file_path):
    zip_data = base64.b64decode(zip_content)  
    with open(zip_file_path, 'wb') as zip_file:
        zip_file.write(zip_data) 
     
pcap_file = 'phreaky.pcap'
reconstruct_smtp_messages(pcap_file) 
extract_to_dir = "./zips_extracted/" 
for count, (zip_content, password) in enumerate(zip(complete_data, passwords)):
    count+=1
    zip_file_path = f"./zips/{count}_{password}.zip.{str(count).zfill(3)}" 
    create_zip(zip_content, zip_file_path)
    unzip_file_with_password(zip_file_path, extract_to_dir, password)

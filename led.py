from __future__ import print_function
from __future__ import division
import socket
import numpy as np
from state import default_config as config

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
WLED_TIMEOUT_S = 10

def send_pixels(pixels):
    m = np.ndarray([config['N_PIXELS'], 3], np.uint8);
    for i in range(config['N_PIXELS']):
        r, g, b = pixels[0][i], pixels[1][i], pixels[2][i]
        m[i][0] = r
        m[i][1] = g
        m[i][2] = b



    data_to_send = bytes([2, WLED_TIMEOUT_S]) + bytes(m.flatten())
    cfg_udp_ip = config['UDP_IP']
    udp_ips = [cfg_udp_ip] if not isinstance(cfg_udp_ip, list) else cfg_udp_ip
    for ip in udp_ips:
        udp_socket.sendto(data_to_send, (ip, config['UDP_PORT']));

def update(output):
    pixels = output[2].astype(int)
    return send_pixels(pixels)
    

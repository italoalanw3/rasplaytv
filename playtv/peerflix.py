# -*- coding: utf-8 -*-
import pexpect

from time import sleep
from threading import Thread

"""
Primeiro executar o peerflix:
peerflix "magnet:?xt=urn:btih:8CB386A17D7B4FF6ACFC467AE8811F658D1032B6&dn=pretty+little+liars+s06e12+720p+hdtv+x264+dimension+rartv&tr=udp%3A%2F%2Ftracker.publicbt.com%2Fannounce&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce" --subtitles /home/italo/Documents/LEGENDAS/Seriados/Pretty_Little_Liars_span_HDTV_720p_1080p_span_span_S06E06_span_/Pretty.Little.Liars.S06E06.720p.HDTV.X264-DIMENSION.srt --port 50000 

peerflix "magnet:?xt=urn:btih:014DC152DC7EAE348B40D33E0821672DD41CBB43&dn=pretty+little+liars+s06e15+720p+hdtv+x264+dimension+rartv&tr=udp%3A%2F%2Ftracker.publicbt.com%2Fannounce&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce" --subtitles /home/durval/rasplaytv/rasplaytv/media/legendas/Pretty.Little.Liars.S06E15.720p.HDTV.X264-DIMENSION.srt
Segundo executar o omxplayer:
omxplayer -o hdmi http://192.168.0.12:50000/ --subtitles /home/pi/rasplaytv/LEGENDAS/Seriados/Pretty_Little_Liars/Pretty.Little.Liars.S06E06.720p.HDTV.X264-DIMENSION.srt --align center --no-ghost-box
"""

import os
import socket
if os.name != "nt":
    import fcntl
    import struct

class Peerflix(object):

    __ESCREVER_LOG = True
    __OBTER_IP = True
    __IP = '192.168.0.50'
    __STOP = False

    __diretorio_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def __init__(self, legendado, torrent, legenda):        
        print('Comando Peerflix chegou...')
        cmd = 'peerflix "{0}"'.format(torrent)
        if legendado:
            cmd = 'peerflix "{0}" --subtitles {1}'.format(torrent, '{0}{1}'.format(self.__diretorio_raiz, legenda))

        print cmd
        self._processo = pexpect.spawn(cmd)
        print('Comando Peerflix executado...')
        self.porta = self.obter_porta()
        print('Comando Peerflix porta obtida...')
        self.ip = self.get_lan_ip()
        print('Peerflix iniciado em http://{0}:{1}/'.format(self.ip, self.porta))

        self._saida_console_thread = Thread(target=self._saida_console)
        self.__STOP = False
        self._saida_console_thread.start()

    def parar(self):
        self._processo.terminate(force=True)
        self.__STOP = True
        self._saida_console_thread.join()

    def _saida_console(self):
        try:
            saida = self._processo.readline()
            while len(saida) > 0 and not self.__STOP:
                if self.__ESCREVER_LOG:
                    print 'Saida PEERFLIX [http://{0}:{1}/]: {2}'.format(self.ip, self.porta, saida)
                saida = self._processo.readline()
                sleep(0.001)
        except Exception, e:
            print('Erro ao ler saida do peerflix: '+str(e))


    def obter_porta(self):
        host = 'http://{}:'.format(self.get_lan_ip())
        print(host)
        while True:
            try:
                saida = self._processo.readline().split(host)
                if len(saida) > 1:
                    return saida[1].split('/')[0]
            except Exception, e:
                print('Erro ao obter porta: '+str(e))

    def get_interface_ip(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
                                ifname[:15]))[20:24])

    def get_lan_ip(self):
        if self.__OBTER_IP:
            ip = socket.gethostbyname(socket.gethostname())
            if ip.startswith("127.") and os.name != "nt":
                interfaces = [
                    "eth0",
                    "eth1",
                    "eth2",
                    "wlan0",
                    "wlan1",
                    "wifi0",
                    "ath0",
                    "ath1",
                    "ppp0",
                    ]
                for ifname in interfaces:
                    try:
                        ip = self.get_interface_ip(ifname)
                        break
                    except IOError:
                        pass
            return ip
        else: 
            return self.__IP
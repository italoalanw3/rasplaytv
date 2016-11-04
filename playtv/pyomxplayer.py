
# -*- coding: utf-8 -*-
from pexpect import pxssh

from time import sleep

"""
Primeiro executar o peerflix:
peerflix "magnet:?xt=urn:btih:8CB386A17D7B4FF6ACFC467AE8811F658D1032B6&dn=pretty+little+liars+s06e12+720p+hdtv+x264+dimension+rartv&tr=udp%3A%2F%2Ftracker.publicbt.com%2Fannounce&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce" --subtitles /home/italo/Documents/LEGENDAS/Seriados/Pretty_Little_Liars_span_HDTV_720p_1080p_span_span_S06E06_span_/Pretty.Little.Liars.S06E06.720p.HDTV.X264-DIMENSION.srt --port 50000 


Segundo executar o omxplayer:
omxplayer -o hdmi http://192.168.0.12:50000/ --subtitles /home/pi/rasplaytv/LEGENDAS/Seriados/Pretty_Little_Liars/Pretty.Little.Liars.S06E06.720p.HDTV.X264-DIMENSION.srt --align center --no-ghost-box
"""

class OMXPlayer(object):

	_PAUSE_CMD = 'p'
	_DEVAGAR_CMD = '1'
	_RAPIDO_CMD = '2'
	_VOLTAR_CMD = 'i'
	_AVANCAR_CMD = 'o'
	_NEXT_SUBTITLE_CMD = 'm'
	_TOGGLE_SUB_CMD = 's'

	def __init__(self, ip, ip_executando, porta_executando, usuario, legendado, senha, legenda):
		self.logado = False
		try:
			s = pxssh.pxssh()
			self.logado = s.login(ip, usuario, senha)
			self.ssh = s

			self.reininiciar(ip_executando, porta_executando, legendado, legenda)

		except pxssh.ExceptionPxssh as e:
			print('pxssh nao conseguiu logar no ip {0} com usuario {1} e senha {2}'.format(ip, usuario, senha))
			print(str(e))

	def reininiciar(self, ip_executando, porta_executando, legendado, legenda):
		cmd = 'omxplayer -o hdmi http://{0}:{1}/ --align center --no-ghost-box'.format(ip_executando, porta_executando)
		if legendado:
			cmd = 'omxplayer -o hdmi http://{0}:{1}/ --subtitles {2} --align center --no-ghost-box'.format(ip_executando, porta_executando, legenda)

		self.ssh.sendline(cmd)

	def stop(self):
		self.ssh.logout()

	def toggle_pause(self):        
		self.ssh.sendline(self._PAUSE_CMD)        

	def devagar(self):
		self.ssh.sendline(self._DEVAGAR_CMD)
        
	def rapido(self):
		self.ssh.sendline(self._RAPIDO_CMD)

	def voltar(self):
		self.ssh.sendline(self._VOLTAR_CMD)

	def avancar(self):
		self.ssh.sendline(self._AVANCAR_CMD)
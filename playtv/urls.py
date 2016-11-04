# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url, handler404, handler500
from django.views.generic import TemplateView	

handler404 = 'playtv.page_not_found'
handler500 = 'playtv.server_error'

from .views import *

urlpatterns = [
	#url(r'^$', IndexView.as_view(), name='home'),	
	url(r'^$', process_request, name='index'),	

	# DESKTOP
	url(r'^filmes/$', TemplateView.as_view(template_name="desktop/filmes.html"), name='filmes'),
	url(r'^seriados/$', TemplateView.as_view(template_name="desktop/seriados.html"), name='seriados'),
	url(r'^play-online/$', TemplateView.as_view(template_name="desktop/play.html"), name='play_online'),			

	#REST
	url(r'filmes/todos/$', filmes, name='todos_filmes'), # Funcionando
	url(r'filmes/links-filme/$', links_filme, name='links_filmes'), # Funcionando
	url(r'seriados/todos/$', seriados, name='todos_seriados'),
	url(r'seriados/temporadas/$', temporadas, name='todas_as_temporadas'),
	url(r'seriados/episodios-dessa-temporada/$', episodios_dessa_temporada, name='episodios_dessa_temporada'),
	url(r'seriados/links-episodio/$', links_episodio_seriado, name='links_episodio_seriado'),	

	url(r'stream/iniciar/$', play_peerflix, name='stream'), # Funcionando	
	url(r'stream/parar/$', stop_peerflix, name='stream'), # Funcionando	
	
	url(r'video/play/$', play, name='play'), # Funcionando	
	url(r'video/play_pause/$', play_pause, name='play_pause'), # Funcionando
	url(r'video/voltar/$', voltar, name='voltar'),
	url(r'video/avancar/$', avancar, name='avancar'),
	url(r'video/rapido/$', rapido, name='rapido'),
	url(r'video/devagar/$', devagar, name='devagar'),
	url(r'video/stop/$', stop, name='stop'), # Funcionando
	url(r'categorias/todas/$', categorias, name='todas_categorias'),
	url(r'categorias/filmes-dessa-categoria/$', filmes_dessa_categoria, name='filmes_dessa_categoria'),	
	url(r'play-online/play/$', executar_play_online, name='executar_play_online'),			
]
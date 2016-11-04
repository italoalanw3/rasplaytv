# -*- coding: utf-8 -*-
"""
WSGI config for rasplaytv project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rasplaytv.settings")
application = get_wsgi_application()


import time
from threading import Thread
from playtv.models import Filme, Episodio, Importacao, Execucao
from sincronizador import Sincronizador

def resetar_status_reproducao_todos_os_objetos():
	try:	
		print('Atualizando os filmes e episodios que estiverem em execucao')
		Filme.objects.all().update(status_execucao=0)	
		Episodio.objects.all().update(status_execucao=0)
		Execucao.objects.all().update(status_execucao=0, ip_executando='0.0.0.0', porta_executando=0000)
		
		time.sleep(1)
		print('Filmes e series resetados os staus para PARADO!')
	except Exception, e:
		print('Nao foi possivel resetar os status dos filmes e episodios de seriado. Erro: {}'.format(e))

def sincronizar_com_repositorio_externo():
	while True:
		try:
			print('Sincronizador de filmes e series iniciado...')		
			links_importar = []		
			diretorio_projeto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
			links_importar.append(criar_dict_importacao("{0}/importacao/categorias.txt".format(diretorio_projeto), 0))			
			links_importar.append(criar_dict_importacao("{0}/importacao/filmes.txt".format(diretorio_projeto), 1))
			links_importar.append(criar_dict_importacao("{0}/importacao/seriados.txt".format(diretorio_projeto), 2))
			for link in links_importar:
				importacao = Importacao()
				try:
					importacao = Importacao.objects.get(link=link)
					if importacao.importacao_concluida:
						print('Sincronizador de filmes e series ja realizado para url: {}'.format(link))
						continue
				except Exception, e:
					importacao = Importacao.objects.create(link=link, detalhe='Importacao de arquivo de um link para o banco local')		
				
				sinc = Sincronizador(link['arquivo'], link['tipo'])
				if sinc.sincronizado:
					importacao.importacao_concluida = False #Em Producao modificar para True
				importacao.save()
			print('Sincronizador de filmes e series concluido!')
		except Exception, e:
			print('Nao foi possivel criar sincronizador de filmes e series. Erro: {}'.format(e))

		print('Aguardando {} minutos para nova verificacao...'.format(30))
		time.sleep(int(60*30))

def criar_dict_importacao(arquivo, tipo):
	try:
		link_dict = dict()
		link_dict['arquivo'] = arquivo
		link_dict['tipo'] = tipo
		return link_dict
	except Exception, e:
		print('Nao foi possivel criar dicionario do arquivo. Erro: {}'.format(e))

try:
	#t1 = Thread(target=resetar_status_reproducao_todos_os_objetos, args=(i,))
	t1 = Thread(target=resetar_status_reproducao_todos_os_objetos)
	t2 = Thread(target=sincronizar_com_repositorio_externo)

	t1.start()
	t2.start()
except Exception, e:
	print('Falha ao criar/iniciar threads')
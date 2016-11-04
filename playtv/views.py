# -*- coding: utf-8 -*-
from django.views.defaults import page_not_found as default_page_not_found
from django.views.defaults import server_error as default_server_error
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.core import serializers		
from django.http import HttpResponse

from pyomxplayer import OMXPlayer
from peerflix import Peerflix

import commands
from rasplaytv import settings
from .models import *
import time
import socket
import json

# Redirecionar de acordo com o dispositivo
import re
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

execucoes = []

# Use custom 404 and 500 handlers, just to override templates names
def page_not_found(request, template_name='404.html'):
    return default_page_not_found(request, template_name=template_name)

def server_error(request, template_name='500.html'):
    return default_server_error(request, template_name=template_name)

def obter_url_youtube(url_youtube):
	return commands.getoutput('youtube-dl -g "{0}"'.format(url_youtube))			

def simular_omx_player():
	return socket.gethostname() == 'raspberrypi'

def play_peerflix(request):
	global execucoes
	execucao = dict()
	omx = None

	dados_post = json.loads(request.body)
	print(dados_post)

	execu = None
	try:
		if dados_post['tipo_video'] == 0:
			execu = LinksFilme.objects.get(pk=dados_post['pk_link'], execucao__token=request.COOKIES['csrftoken']).execucao
		else:
			execu = LinksEpisodioSeriado.objects.get(pk=dados_post['pk_link'], execucao__token=request.COOKIES['csrftoken']).execucao
	except Exception, e:		
		execu = Execucao.objects.create(status_execucao=3, endereco_ip_solicitante=request.META['REMOTE_ADDR'], nome_maquina_solicitante=request.META['REMOTE_HOST'], token=request.COOKIES['csrftoken'])

	peerflix = None
	# Coloca o escolhido com o status de reproduzindo.
	resposta = None
	link = None
	if dados_post['tipo_video'] == 0:
		link = LinksFilme.objects.get(pk=dados_post['pk_link'])			
		filme = Filme.objects.get(pk=link.filme.pk)
		filme.status_execucao=3
		filme.save()

	else:
		link = LinksEpisodioSeriado.objects.get(pk=dados_post['pk_link'])	
		episodio = Episodio.objects.get(pk=link.episodio.pk)
		episodio.status_execucao=3
		episodio.save()

	peerflix = Peerflix(not link.dublado, link.link, link.legenda)
	execu.ip_executando = peerflix.ip
	execu.porta_executando = peerflix.porta
	execu.status_execucao = 3
	link.execucao = execu
	link.save()
	execu.save()

	execucao['peerflix'] = peerflix
	execucao['omxplayer'] = omx
	execucao['token'] = request.COOKIES['csrftoken']
	execucao['pk_link'] = dados_post['pk_link']

	execucoes.append(execucao)

	data = serializers.serialize('json', [execu,])

	return HttpResponse(data, content_type='application/json')

def stop_peerflix(request):

	retorno = dict()	
	retorno['resposta'] = False
	tokenAceito = False
	for execu in execucoes:
		if request.COOKIES['csrftoken'] == execu['token']:
			tokenAceito = True
			break

	if not tokenAceito:
		retorno['objeto'] = 'Somente quem iniciou é quem pode interromper!!!'
		return HttpResponse(json.dumps(retorno), content_type='application/json')

	dados_post = json.loads(request.body)

	for execu in execucoes:
		if execu['pk_link'] == dados_post['pk_link'] and execu['token'] == request.COOKIES['csrftoken']:
			execu['peerflix'].parar()
			row = LinksFilme.objects.get(pk=dados_post['pk_link'])			
			row.execucao.status_execucao = 0
			row.execucao.ip_executando = '0.0.0.0'
			row.execucao.porta_executando = 0000
			row.execucao.save()
			link_retorno = ({'status_execucao': row.execucao.status_execucao, 'ip_executando':row.execucao.ip_executando, 'porta_executando': row.execucao.porta_executando, 'link': row.link, 'pk': row.pk, 'qualidade': row.qualidade, 
				'dublado': row.dublado, 'fonte': row.fonte, 'torrent': row.torrent, 'legenda': row.legenda, 'seeds': row.seeds, 'peers': row.peers})

			retorno['resposta'] = True			
			retorno['objeto'] = link_retorno

	return HttpResponse(json.dumps(retorno), content_type='application/json')

def play_omx(request, link):
	global execucoes
	dados_post = json.loads(request.body)

	endereco_ip = dados_post['endereco_ip']
	usuario = dados_post['usuario']
	senha = dados_post['senha']

	omxplayer = None
	for execu in execucoes:
		if execu['token'] == request.COOKIES['csrftoken']:
			if execu['omxplayer'] == None:
				omxplayer = OMXPlayer(endereco_ip, link.execucao.ip_executando, link.execucao.porta_executando, usuario, not link.dublado, senha, link.legenda)		
				execu['omxplayer'] = omxplayer	
			else:				
				execu['omxplayer'].reininiciar(link.execucao.ip_executando, link.execucao.porta_executando, not link.dublado, link.legenda)

def executar_play_online(request):
	global execucoes
	print('Play chegou')
	print(request.method)
	print(request.body)

	dados_post = json.loads(request.body)
	print(dados_post)
	# Coloca todo mundo como status de parado.
	filmes = Filme.objects.all().update(status_execucao=0)
	# Coloca todo mundo como status de parado.
	episodios = Episodio.objects.all().update(status_execucao=0)

	resposta = dict()
	print('SIMULAR OMX View: {}'.format(simular_omx_player()))	
	if simular_omx_player():
		print('Simulando OMXPlayer...')		
		if dados_post['youtube']:		
			print('URL do youtube')	
		else:
			print('URL normal')	
		time.sleep(2)				
	else:
		play_omx(True, dados_post['url'], dados_post['youtube'])
	
	resposta['resposta'] = True
	# Coloca o escolhido com o status de reproduzindo.	
	print('Play efetuado')
	return HttpResponse(serializers.serialize('json', dict()), content_type='application/json')

def play(request):	
	global execucoes
	print('Play chegou')
	print(request.method)
	print(request.body)

	dados_post = json.loads(request.body)
	print(dados_post)
	# Coloca todo mundo como status de parado.
	filmes = Filme.objects.all().update(status_execucao=0)
	# Coloca todo mundo como status de parado.
	episodios = Episodio.objects.all().update(status_execucao=0)
	
	link = None
	print(dados_post['tipo_video'])
	if dados_post['tipo_video'] == 0:
		link = LinksFilme.objects.get(pk=dados_post['pk_link'])		
	else:
		link = LinksEpisodioSeriado.objects.get(pk=dados_post['pk_link'])		

	print('SIMULAR OMX View: {}'.format(simular_omx_player()))	
	if simular_omx_player():
		time.sleep(2)		
	else:
		play_omx(request, link)

	# Coloca o escolhido com o status de reproduzindo.
	resposta = None
	if dados_post['tipo_video'] == 0:
		link = LinksFilme.objects.get(pk=dados_post['pk_link'])	
		filme = Filme.objects.get(pk=link.filme.pk)
		filme.status_execucao=1
		filme.save()

		resposta = Filme.objects.all()
	else:
		link = LinksEpisodioSeriado.objects.get(pk=dados_post['pk_link'])	
		episodio = Episodio.objects.get(pk=link.episodio.pk)
		episodio.status_execucao=1
		episodio.save()

		resposta = Episodio.objects.all()
	
	print('Play efetuado')
	return HttpResponse(serializers.serialize('json', resposta), content_type='application/json')

def play_pause(request):
	global execucoes
	global omx
	print('Pause chegou')

	print(request.body)
	dados_post = json.loads(request.body)

	resposta = None
	if dados_post['tipo_video'] == 0:
		filme = Filme.objects.get(pk=dados_post['pk_video'])
		if filme.status_execucao == 1:
			filme.status_execucao = 2
		elif filme.status_execucao == 2:
			filme.status_execucao = 1
		filme.save()
		resposta = filme
	else:
		episodio = Episodio.objects.get(pk=dados_post['pk_video'])
		if episodio.status_execucao == 1:
			episodio.status_execucao = 2
		elif episodio.status_execucao == 2:
			episodio.status_execucao = 1
		episodio.save()
		resposta = episodio

	if simular_omx_player():
		print request.POST
	else:
		if omx != None:
			omx.toggle_pause()
			print('Pause efetuado')
		else: 
			print('OMX nao inicializado')
	data = serializers.serialize('json', [resposta,])
	return HttpResponse(data, content_type='application/json')

def stop(request):
	global execucoes
	global omx
	print('Stop chegou')

	print(request.body)

	dados_post = json.loads(request.body)
	if dados_post['tipo_video'] == 0:
		filme = Filme.objects.get(pk=dados_post['pk_video'])
		filme.status_execucao = 0
		filme.save()
	else:
		episodio = Episodio.objects.get(pk=dados_post['pk_video'])
		episodio.status_execucao = 0
		episodio.save()

	if simular_omx_player():
		print('Stop efetuado')
	else:
		if omx != None:
			omx.stop()
			omx = None
			print('Stop efetuado')
		else:
			print('OMX nao inicializado')
	return HttpResponse(serializers.serialize('json', dict()), content_type='application/json')

def voltar(request):
	global execucoes
	global omx
	print('Voltar chegou')

	if simular_omx_player():
		print('Voltar efetuado')
	else:
		if omx != None:
			omx.voltar()
			print('Voltar efetuado')
		else:
			print('OMX nao inicializado')
	return HttpResponse(serializers.serialize('json', dict()), content_type='application/json')

def avancar(request):
	global execucoes
	global omx
	print('Avancar chegou')

	if simular_omx_player():
		print('Avancar efetuado')
	else:
		if omx != None:
			omx.avancar()
			print('Avancar efetuado')
		else:
			print('OMX nao inicializado')
	return HttpResponse(serializers.serialize('json', dict()), content_type='application/json')

def devagar(request):
	global execucoes
	global omx
	print('Devagar chegou')

	if simular_omx_player():
		print('Devagar efetuado')
	else:
		if omx != None:
			omx.devagar()
			print('Devagar efetuado')
		else:
			print('OMX nao inicializado')
	return HttpResponse(serializers.serialize('json', dict()), content_type='application/json')

def rapido(request):
	global execucoes
	global omx
	print('Rapido chegou')

	if simular_omx_player():
		print('Rapido efetuado')
	else:
		if omx != None:
			omx.rapido()
			print('Rapido efetuado')
		else:
			print('OMX nao inicializado')
	return HttpResponse(serializers.serialize('json', dict()), content_type='application/json')

def filmes(request):
	global execucoes	
	filmes = Filme.objects.order_by('data_atualizacao').order_by('data_criacao', '-titulo')
	data = serializers.serialize('json', filmes)
	print(request.COOKIES['csrftoken'])
	return HttpResponse(data, content_type='application/json')

def links_filme(request):
	global execucoes
	print(request.body)
	links = LinksFilme.objects.filter(filme__pk=request.body)

	links_list = []
	for row in links:
		print(row)
		print('ROW execucao')
		if row.execucao != None:
			links_list.append({'ip_executando':row.execucao.ip_executando, 'status_execucao': row.execucao.status_execucao, 'porta_executando': row.execucao.porta_executando, 'link': row.link, 'pk': row.pk, 'qualidade': row.qualidade, 
				'dublado': row.dublado, 'fonte': row.fonte, 'torrent': row.torrent, 'legenda': row.legenda, 'seeds': row.seeds, 'peers': row.peers})
		else:
			links_list.append({'ip_executando':'0.0.0.0', 'status_execucao': 0, 'porta_executando': '0000', 'link': row.link, 'pk': row.pk, 'qualidade': row.qualidade, 
				'dublado': row.dublado, 'fonte': row.fonte, 'torrent': row.torrent, 'legenda': row.legenda, 'seeds': row.seeds, 'peers': row.peers})


	return HttpResponse(json.dumps(links_list), content_type='application/json')

def categorias(request):
	global execucoes
	categorias = Categoria.objects.order_by('titulo')
	categorias_filmes = []	
	for categoria in categorias:
		categorias_filmes_dict = dict()
		categorias_filmes_dict['quantidade_filmes'] = CategoriasFilme.objects.filter(categoria__pk=categoria.pk).count()
		categorias_filmes_dict['categoria'] = serializers.serialize('json', [ categoria, ])
		print(categoria.titulo)
		categorias_filmes.append(categorias_filmes_dict)

	for c in categorias_filmes:
		print(str(c))
	return HttpResponse(json.dumps(categorias_filmes), content_type='application/json')

def filmes_dessa_categoria(request):
	global execucoes
	dados_post = json.loads(request.body)
	print('Corpo da requisicao: {}'.format(dados_post))
	categorias_filmes = CategoriasFilme.objects.filter(categoria__pk=dados_post['id']).order_by('-filme__titulo')	
	filmes = []
	for categoria_filme in categorias_filmes:
		filmes.append(categoria_filme.filme)
	data = serializers.serialize('json', filmes)
	return HttpResponse(data, content_type='application/json')

def seriados(request):
	global execucoes
	seriados = Seriado.objects.order_by('titulo')
	data = serializers.serialize('json', seriados)
	return HttpResponse(data, content_type='application/json')

def temporadas(request):
	global execucoes
	print(request.body)
	todos_episodios_seriado = Episodio.objects.filter(seriado__pk=request.body).order_by('-temporada')	

	temporadas = [0]
	print(str(len(todos_episodios_seriado)))
	for episodio in todos_episodios_seriado:
		if not episodio.temporada in temporadas:
			temporadas.append(episodio.temporada)

	for tem in temporadas:
		print('Temporadas : '+str(tem))
	temporadas.remove(0)
	return HttpResponse(json.dumps(temporadas), content_type='application/json')

def episodios_dessa_temporada(request):
	global execucoes
	dados_post = json.loads(request.body)
	print('Corpo da requisicao: {}'.format(dados_post))
	links = Episodio.objects.filter(seriado__pk=dados_post['id'], temporada=dados_post['temporada']).order_by('episodio', 'data_atualizacao')	
	data = serializers.serialize('json', links)
	return HttpResponse(data, content_type='application/json')

def links_episodio_seriado(request):
	global execucoes
	print(request.body)
	links = LinksEpisodioSeriado.objects.filter(episodio__pk=request.body)

	links_list = []
	for row in links:
		print(row)
		print('ROW execucao')
		if row.execucao != None:
			links_list.append({'ip_executando':row.execucao.ip_executando, 'status_execucao': row.execucao.status_execucao, 'porta_executando': row.execucao.porta_executando, 'link': row.link, 'pk': row.pk, 'qualidade': row.qualidade, 
				'dublado': row.dublado, 'fonte': row.fonte, 'torrent': row.torrent, 'legenda': row.legenda, 'seeds': row.seeds, 'peers': row.peers})
		else:
			links_list.append({'ip_executando':'0.0.0.0', 'status_execucao': 0, 'porta_executando': '0000', 'link': row.link, 'pk': row.pk, 'qualidade': row.qualidade, 
				'dublado': row.dublado, 'fonte': row.fonte, 'torrent': row.torrent, 'legenda': row.legenda, 'seeds': row.seeds, 'peers': row.peers})

	return HttpResponse(json.dumps(links_list), content_type='application/json')

# Ported by Matt Sullivan http://sullerton.com/2011/03/django-mobile-browser-detection-middleware/

reg_b = re.compile(r"(android|bb\\d+|meego).+mobile|avantgo|bada\\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\\.(browser|link)|vodafone|wap|windows ce|xda|xiino", re.I|re.M)
reg_v = re.compile(r"1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\\-(n|u)|c55\\/|capi|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\\-|_)|g1 u|g560|gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit|hd\\-(m|p|t)|hei\\-|hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\\/)|klon|kpt |kwc\\-|kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|\\-[a-w])|libw|lynx|m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\\-2|po(ck|rt|se)|prox|psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2-7]|i\\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\\-|oo|p\\-)|sdk\\/|se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-|shar|sie(\\-|m)|sk\\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\\-|v\\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\\-|tdg\\-|tel(i|m)|tim\\-|t\\-mo|to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9|up(\\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\\-|your|zeto|zte\\-", re.I|re.M)

def process_request(request):
    global execucoes
    request.mobile = False
    if request.META.has_key('HTTP_USER_AGENT'):
        user_agent = request.META['HTTP_USER_AGENT']
        b = reg_b.search(user_agent)
        v = reg_v.search(user_agent[0:4])
        if b or v:
            #return render_to_response("mobile/index.html")
            return render_to_response("desktop/index.html")

    return render_to_response("desktop/index.html")
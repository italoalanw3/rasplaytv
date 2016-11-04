import os
from datetime import datetime
import requests
import codecs
import time
#import goslate
#from microsofttranslator import Translator
import omdb
import urllib

from playtv.models import *

class Sincronizador(object):

	__CATEGORIAS = 0
	__FILMES = 1
	__SERIADO = 2

	_HORA_ATUALIZAR_LIMITE_INICIAL = 0
	_HORA_ATUALIZAR_LIMITE_FINAL = 23
	__QUANTIDADE_FALHAS_PERMITIDA_TRADUCAO = 20
	__erros_imdb = 0
	#__translator = Translator('italoTXhkINb4ns','HrXMPdckkJF5AbfkjNZ/6fOaHWbMA2LfSSrYFuCbn1E=')
	__link = None

	def __init__(self, link, tipo_importacao):

		print('----------------------------------------------------------------------')
		print('----------------------------------------------------------------------')
		print('----------------------------------------------------------------------')
		print('----------------------------------------------------------------------')
		self.__link = link

		self.__lines = []
		self.__lista_dicionarios_de_arquivo_txt = []
		self.__filmes_seriados_full = []

		self.sincronizado = False
		if self.hora_de_importar():
			self.__lines = self.carregar_lista_linhas_txt()				
			
			if tipo_importacao == self.__CATEGORIAS:				
				self.criar_lista_validando_link()
				self.extrair_categorias_arquivo()
			elif tipo_importacao == self.__FILMES:	
				self.criar_lista_validando_link()
				# Passo 2: percorrer a lista de filmes/series lidas para traduzir o titulo para realizar
				# busca no IMDB (omdb)
				for movie in self.__lista_dicionarios_de_arquivo_txt:
					# Passo 3: Traduzir o nome para ingles
					#nomeOriginal = movie_serie['nome']
					#nome_em_ingles = self.traduzir_nome_para_ingles_para_busca_imdb(movie_serie['nome'])
					# Passo 4: Buscar no IMDB filme/serie com o nome convertido
					if self.filme_nao_cadastrado(movie['nome_filme_original']):					
						self.buscar_no_imdb(movie['nome_filme'], movie['nome_filme_original'], movie['url'], movie['legenda'], movie['ehtorrent'], 0, 0)

				# Passo 5: Salvar a lista
				self.salvar_filmes_importados_para_local()

				self.sincronizado = True
			elif tipo_importacao == self.__SERIADO:
				self.criar_lista_validando_link_episodios_seriado()
				# Passo 2: percorrer a lista de filmes/series lidas para traduzir o titulo para realizar
				# busca no IMDB (omdb)
				for serie in self.__lista_dicionarios_de_arquivo_txt:
					# Passo 3: Traduzir o nome para ingles
					#nomeOriginal = movie_serie['nome']
					#nome_em_ingles = self.traduzir_nome_para_ingles_para_busca_imdb(movie_serie['nome'])
					# Passo 4: Buscar no IMDB filme/serie com o nome convertido
					self.buscar_no_imdb(serie['nome_seriado'], serie['nome_seriado_original'], serie['url'], serie['legenda'], serie['ehtorrent'], serie['temporada'], serie['episodio'])

				# Passo 5: Salvar a lista
				self.salvar_episodios_serie_importados_para_local()

				self.sincronizado = True
			else:
				print('Tipo de importacao nao informado')

			time.sleep(1)
		else:
			print('Nao esta dentro do horario de sincronizar')

	def hora_de_importar(self):
		hora = datetime.now().hour
		print(datetime.now())
		print('Verificando hora de importar filmes: Hora para atualizar entre= {0} e {1}| Hora atual= {2}'.format(self._HORA_ATUALIZAR_LIMITE_INICIAL, self._HORA_ATUALIZAR_LIMITE_FINAL, hora))
		if hora >= self._HORA_ATUALIZAR_LIMITE_INICIAL and hora <= self._HORA_ATUALIZAR_LIMITE_FINAL:
			return True
		return False

	def filme_nao_cadastrado(self, titulo):
		try:
			Filme.objects.get(titulo_ingles=titulo)
			print('Filme ja cadastrado')
			return False
		except Exception, e:
			print('Filme nao cadastrado')
			return True

	def extrair_categorias_arquivo(self):		
		try:
			for categoria_dict in self.__lista_dicionarios_de_arquivo_txt:
				print('Extraindo categoria de arquivo: {}'.format(categoria_dict))
				try:
					categoria = Categoria.objects.get(titulo_ingles=categoria_dict['nome'])
				except Exception, e:
					categoria = Categoria.objects.create(titulo_ingles=categoria_dict['nome'], titulo=categoria_dict['nome'], imagem=categoria_dict['url'])
				print('Categoria: {} | Inserida no banco local'.format(categoria_dict['nome']))
		except Exception, e:
			print('Nao foi possivel extrair categoria: '+str(e))

	def upload_imagem(self, url_imagem_imdb, nome_arquivo):
		try:
			diretorio_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
			extensao = url_imagem_imdb[-3:]
			caminho_retorno = '/media/imdb/{0}.{1}'.format(nome_arquivo, extensao)
			caminho_completo = '{0}/media/imdb/{1}.{2}'.format(diretorio_raiz, nome_arquivo, extensao)
			urllib.urlretrieve(url_imagem_imdb, caminho_completo)
			return caminho_retorno
		except Exception, e:
			print('Erro ao extrair imagem do imdb: '+str(e))		

	def extrair_categorias(self, filme_serie):
		try:
			categorias_split = filme_serie['imdb'].genre.split(',')
			categorias = []

			categoria = Categoria()
			if filme_serie['imdb'].genre == 'N/A':
				try:
					categoria = Categoria.objects.get(nome='Nao informado')			
				except Exception, e:		
					categoria = Categoria.objects.create(titulo='Nao informado', titulo_ingles='Nao informado', imagem='http://www.aldo.com.br/Images/semImagem.jpg')
				categorias.append(categoria)
				return categorias

			for categoria_nome in categorias_split:
				try:
					categoria = Categoria.objects.get(titulo_ingles=categoria_nome.lstrip())
				except Exception, e:
					categoria = Categoria.objects.create(titulo_ingles=categoria_nome.lstrip(), titulo=categoria_nome.lstrip(), imagem='http://www.aldo.com.br/Images/semImagem.jpg')
				categorias.append(categoria)

			return categorias
		except Exception, e:
			print('Nao foi possivel extrair categorias: '+str(e))

	def carregar_lista_linhas_txt(self):
		try:
			#LinksFilme.objects.filter(filme__carga_automatica=True).delete()
			#Filme.objects.filter(carga_automatica=True).delete()				
			print('Carregar linhas de arquivo')		
			#r = requests.get(self.__link)
			#r.encoding = 'utf-8'	

			#file = codecs.open("filmes.txt", "w", "utf-8")
			#file.write(r.text)
			lines = [line.rstrip('\n') for line in open(self.__link)]	
			return lines
		except Exception, e:
			print('Falha ao carregar linhas de arquivo: '+str(e))	

	def criar_lista_validando_link(self):
		print('Criando lista para validar links lido de arquivo')
		descartarPrimeiraLinha = 0
		for linha in self.__lines:
			if descartarPrimeiraLinha > 0:
				try:
					splitLinha = linha.split('::::')
					if len(splitLinha) >= 4:
						arquivo = dict()
						arquivo['nome_filme'] = splitLinha[0].replace('-', ' ').replace('_', ' ').replace(':', '')
						arquivo['nome_filme_original'] = splitLinha[1].replace('-', ' ').replace('_', ' ').replace(':', '')
						arquivo['url'] = '{0}'.format(splitLinha[2])	
						arquivo['legenda'] = '/media/legendas/{0}'.format(splitLinha[3])											
						arquivo['ehtorrent'] = bool(splitLinha[4])

						print('Adicionando dicionario da linha: {}'.format(arquivo))
						self.__lista_dicionarios_de_arquivo_txt.append(arquivo)			

				except Exception, e:
					print('Falha ao verificar linha: '+str(e))	
			else:
				descartarPrimeiraLinha = 1

	def criar_lista_validando_link_episodios_seriado(self):
		print('Criando lista para validar links lido de arquivo')
		descartarPrimeiraLinha = 0
		for linha in self.__lines:
			if descartarPrimeiraLinha > 0:
				try:
					print(linha)
					splitLinha = linha.split('::::')
					print(splitLinha)
					if len(splitLinha) >= 4:
						arquivo = dict()
						arquivo['nome_seriado'] = splitLinha[0].replace('-', ' ').replace('_', ' ').replace(':', '')
						arquivo['nome_seriado_original'] = splitLinha[1]
						arquivo['temporada'] = int(splitLinha[2])
						arquivo['episodio'] = int(splitLinha[3])
						arquivo['url'] = '{}'.format(splitLinha[4])					
						arquivo['legenda'] = '/media/legendas/{}'.format(splitLinha[5])		
						arquivo['ehtorrent'] = bool(splitLinha[6])			

						print('Adicionando dicionario da linha: {}'.format(arquivo))
						self.__lista_dicionarios_de_arquivo_txt.append(arquivo)
					else:
						print('Falha ao verificar linha')

				except Exception, e:
					print('Falha ao verificar linha: '+str(e))	
			else:
				descartarPrimeiraLinha = 1

	def url_filme_serie_funcionando(self, url):
		print('Verificando status da URL do filme/serie: {}'.format(url))
		try:
			#r = requests.get(url, verify=False, timeout=None)
			#r.encoding = 'utf-8'

			#print('Status: {}'.format(r.status_code))
			#return r.status_code < 400
			return True
		except Exception, e:
			print('Falha ao verificar status: '+str(e))
			return False
		return True

	def buscar_no_imdb(self, nome, nomeOriginal, url, legenda, ehtorrent, temporada, episodio):
		try:
			informacoesSeriadoJaBuscadoIMDB = False
			informacoesSeriadoBuscadasIMDBEEpisodioAdicionado = False
			for movie_serie_full in self.__filmes_seriados_full:
				if movie_serie_full['nome_original'] == nomeOriginal:
					print('O filme/serie ja buscou pelo menos uma vez informacoes do IMDB: {}'.format(nomeOriginal))
					informacoesSeriadoJaBuscadoIMDB = True
					break

			if informacoesSeriadoJaBuscadoIMDB:
				for movie_serie_full in self.__filmes_seriados_full:
					if movie_serie_full['nome_original'] == nomeOriginal and movie_serie_full['temporada'] == temporada and movie_serie_full['episodio'] == episodio:						
						informacoesSeriadoBuscadasIMDBEEpisodioAdicionado = True
						break

			if not informacoesSeriadoBuscadasIMDBEEpisodioAdicionado and informacoesSeriadoJaBuscadoIMDB:				
				
				for movie_serie_full in self.__filmes_seriados_full:
					if nomeOriginal == movie_serie_full['nome_original']:
						print('Seriado no imdb, mas episodio {0} nao adicionado '.format(episodio))						
						episodio_dict = dict()			
						episodio_dict['url'] = url
						episodio_dict['nome'] = nome
						episodio_dict['nome_original'] = nomeOriginal										
						episodio_dict['legenda'] = legenda
						episodio_dict['ehtorrent'] = ehtorrent
						episodio_dict['temporada'] = temporada
						episodio_dict['episodio'] = episodio
						episodio_dict['imdb'] = movie_serie_full['imdb']						
						self.__filmes_seriados_full.append(episodio_dict)								
						break
					

			if not informacoesSeriadoJaBuscadoIMDB and not informacoesSeriadoBuscadasIMDBEEpisodioAdicionado:				
				if self.__erros_imdb < 100:	
					print('Buscando filme: {0}'.format(nomeOriginal))		
					movie_serie_full = dict()			

					if self.url_filme_serie_funcionando(url):
						movie_serie_full['imdb'] = omdb.title(nomeOriginal)
						if len(movie_serie_full['imdb']) > 0:
							print('')
							print(movie_serie_full['imdb'])
							print('')
							movie_serie_full['url'] = url
							movie_serie_full['nome'] = nome
							movie_serie_full['nome_original'] = nomeOriginal											
							movie_serie_full['legenda'] = legenda
							movie_serie_full['ehtorrent'] = ehtorrent
							movie_serie_full['temporada'] = temporada
							movie_serie_full['episodio'] = episodio			
							print('PRINCIPAIS INFORMACOES DO IMDB: NOME: {0} | GENEROS: {1} | IMDB_CLASS.{2}'.format(movie_serie_full['imdb'].title, movie_serie_full['imdb'].genre, movie_serie_full['imdb'].imdb_rating))
							print('POSTER: {}'.format(movie_serie_full['imdb'].poster))
							self.__filmes_seriados_full.append(movie_serie_full)
							time.sleep(0.001)
						else:
							print('FILME NAO ENCONTRADO NO IMDB: {}'.format(nomeOriginal))
					else:
						LinksFilme.objects.filter(link=url).delete()						
						LinksEpisodioSeriado.objects.filter(link=url).delete()						
						Filme.objects.filter(titulo_ingles=nomeOriginal).delete()
						Episodio.objects.filter(titulo='Episodio {0} da {1} temporada'.format(episodio, temporada)).delete()
						print('URL: {0} do FILME {1} inacessivel'.format(url, nomeOriginal))
						# IMPLEMENTAR ATUALIZACAO PARA INVALIDAR O LINK NO BANCO LOCAL
				else:
					time.sleep(0.001)
					print('Falhas consecutivas impedem a busca no IMDB [SINCRONIZACAO COM IMDB SERA REALIZADA EM OUTRO MOMENTO]')
		except Exception, e:
			self.__erros_imdb += 1
			print('{0} Falhas ao buscar filme/seriado no IMDB: {1}'.format(self.__erros_imdb, str(e)))			
			print('Nome do filme utilizado na pesquisa que FALHOU: {}'.format(nomeOriginal))			

	def salvar_filmes_importados_para_local(self):
		try:
			quantidade_filmes = 0
			for filme_serie in self.__filmes_seriados_full:
				if filme_serie['imdb'].type == 'movie' or True: # Remover...
					filme = self.extrair_filme(filme_serie)
					if filme['existe']:
						continue
					else:
						atores = self.extrair_atores(filme_serie)
						categorias =  self.extrair_categorias(filme_serie)
						self.salvar_atores_filme(filme['filme'], atores)
						self.salvar_categorias_filme(filme['filme'], categorias)
						self.salvar_link_filme(filme['filme'], filme_serie['url'], filme_serie['legenda'], filme_serie['ehtorrent'])

			print('TOTAL de {} filmes importado'.format(len(self.__filmes_seriados_full)))
			print('{} filmes cadastrados'.format(quantidade_filmes))
		except Exception, e:
			print('Nao foi possivel salvar_FILMES_importados_para_local: '+str(e))

	def salvar_episodios_serie_importados_para_local(self):
		try:
			quantidade_episodios_seriados = 0
			for serie in self.__filmes_seriados_full:
				if serie['imdb'].type == 'series' or serie['imdb'].type == 'episode':
					seriado = self.extrair_seriado(serie)						
					episodio = self.extrair_episodio_seriado(seriado, serie)
					if episodio['existe']:
						continue
					else:
						atores = self.extrair_atores(serie)
						categorias =  self.extrair_categorias(serie)					
						self.salvar_atores_seriado(seriado, atores)
						self.salvar_categorias_seriado(seriado, categorias)							

						self.salvar_link_episodios_seriado(episodio['episodio_seriado'], serie['url'], serie['legenda'], serie['ehtorrent'])

						quantidade_episodios_seriados += 1

			print('TOTAL de {} episodios/series importado'.format(len(self.__filmes_seriados_full)))
			print('{} episodios desprezados'.format(quantidade_episodios_seriados))
		except Exception, e:
			print('Nao foi possivel salvar_episodios_serie_importados_para_local: '+str(e))


	def extrair_atores(self, filme_serie):
		try:
			atores_split = filme_serie['imdb'].actors.split(',')
			
			atores = []			

			ator = Ator()
			if filme_serie['imdb'].actors == 'N/A':				
				try:
					ator = Ator.objects.get(nome='Nao informado')			
				except Exception, e:		
					ator = Ator()
					ator.nome = 'Nao informado'
					ator.save()
				atores.append(ator)
				return atores

			for ator_nome in atores_split:
				try:
					ator = Ator.objects.get(nome=ator_nome.lstrip())			
				except Exception, e:
					ator = Ator()
					ator.nome = ator_nome.lstrip()
					ator.save()
				atores.append(ator)
			return atores
		except Exception, e:
			print('Nao foi possivel extrais atores: '+str(e))

	def extrair_categoria(self, filme_serie):
		try:
			categorias_split = filme_serie['imdb'].genre.split(',')
			categorias = []

			categoria = Categoria()
			if filme_serie['imdb'].genre == 'N/A':
				try:
					categoria = Categoria.objects.get(nome='Nao informado')			
				except Exception, e:		
					categoria = Categoria.objects.create(titulo='Nao informado', titulo_ingles='Nao informado', imagem='http://www.aldo.com.br/Images/semImagem.jpg')
				categorias.append(categoria)
				return categorias

			for categoria_nome in categorias_split:
				try:
					categoria = Categoria.objects.get(titulo_ingles=categoria_nome.lstrip())
				except Exception, e:
					categoria = Categoria.objects.create(titulo_ingles=categoria_nome.lstrip(), titulo=categoria_nome.lstrip(), imagem='http://www.aldo.com.br/Images/semImagem.jpg')
				categorias.append(categoria)

			return categorias
		except Exception, e:
			print('Nao foi possivel extrais categorias: '+str(e))

	def extrair_filme(self, filme):
		try:
			imdb = filme['imdb']
			filmeDict = dict()
			try:
				filmeExistente = Filme.objects.get(titulo_ingles=filme['nome_original'])
				filmeDict['filme'] = filmeExistente
				filmeDict['existe'] = True
				print('Filme com o titulo {0} ja estah cadastrado'.format(filme['nome_original']))
			except Exception, e:
				classificacao = 0
				if imdb.imdb_rating == 'N/A':
					classificacao = 0 
				else:
					classificacao = float(imdb.imdb_rating.replace(',', '.'))

				votos = 0
				if imdb.imdb_votes == 'N/A':
					votos = 0			
				else:
					votos = float(imdb.imdb_votes.replace(',', '.'))

				if imdb.poster == 'N/A':
					imdb.poster = 'http://cdn.123i.com.br/img/sem-foto-vertical.jpg'


				imdb.poster = self.upload_imagem(imdb.poster, filme['nome'].replace(' ', '_'))

				filme_instancia = Filme()
				filme_instancia.titulo=filme['nome']
				filme_instancia.titulo_ingles=filme['nome_original']				
				filme_instancia.sinopse=imdb.plot
				filme_instancia.imagem=imdb.poster
				filme_instancia.carga_automatica=True
				filme_instancia.classificacao_imdb = classificacao
				filme_instancia.votos_imdb=votos
				filme_instancia.save()
		
				filmeDict['filme'] = filme_instancia
				filmeDict['existe'] = False
				
			return filmeDict		
		except Exception, e:
			print('Nao foi possivel extrais filme: '+str(e))		

	def extrair_seriado(self, serieParam):	
		try:
			imdb = serieParam['imdb']
			try:
				seriado = Seriado.objects.get(titulo_ingles=serieParam['nome_original'])
				return seriado
			except Exception, e:
				classificacao = 0
				if imdb.imdb_rating == 'N/A':
					classificacao = 0 
				else:
					classificacao = float(imdb.imdb_rating.replace(',', '.'))

				votos = 0
				if imdb.imdb_votes == 'N/A':
					votos = 0			
				else:
					votos = float(imdb.imdb_votes.replace(',', '.'))

				if imdb.poster == 'N/A':
					imdb.poster = 'http://cdn.123i.com.br/img/sem-foto-vertical.jpg'


				imdb.poster = self.upload_imagem(imdb.poster, serieParam['nome_original'].replace(' ', '_'))

				seriado = Seriado()
				seriado.titulo=serieParam['nome']
				seriado.titulo_ingles=serieParam['nome_original']				
				seriado.sinopse=imdb.plot
				seriado.imagem=imdb.poster
				seriado.carga_automatica=True
				seriado.classificacao_imdb = classificacao
				seriado.votos_imdb=votos
				seriado.save()
				
				return seriado
		except Exception, e:
			print('Nao foi possivel extrair seriado: '+str(e))	

	def extrair_episodio_seriado(self, seriado, serieParam):	
		try:
			episodio_dict = dict()
			try:
				print(serieParam)
				episodio_existente = Episodio.objects.get(seriado__titulo_ingles__icontains=serieParam['nome_original'], temporada=serieParam['temporada'], episodio=serieParam['episodio'])
				episodio_dict['episodio_seriado'] = episodio_existente
				episodio_dict['existe'] = True
				print('Episodio {0} da temporada {1} do seriado {2} ja estah cadastrado'.format(serieParam['episodio'], serieParam['temporada'], serieParam['nome']))
			except Exception, e:
				print('Episodio seriado nao encontrado: '+str(e))					

				episodio_seriado = Episodio()
				episodio_seriado.seriado = seriado
				episodio_seriado.titulo = 'Episodio {0} da {1} temporada'.format(serieParam['episodio'], serieParam['temporada'])
				episodio_seriado.episodio = serieParam['episodio']
				episodio_seriado.temporada = serieParam['temporada']
				episodio_seriado.carga_automatica = True
				episodio_seriado.save()
		
				episodio_dict['episodio_seriado'] = episodio_seriado
				episodio_dict['existe'] = False
				
			return episodio_dict		
		except Exception, e:
			print('Nao foi possivel extrair episodio do seriado: '+str(e))	

	def extrair_episodio(self, filme_serie):
		pass

	def salvar_atores_filme(self, filme, atores):
		try:
			for ator in atores:	
				AtoresFilme.objects.create(filme=filme, ator=ator)
		except Exception, e:
			print('Nao foi possivel extrais atores para filme: '+str(e))

	def salvar_atores_seriado(self, seriado, atores):
		try:
			for ator in atores:	
				AtoresSeriado.objects.create(seriado=seriado, ator=ator)
		except Exception, e:
			print('Nao foi possivel extrais atores para seriado: '+str(e))

	def salvar_categorias_filme(self, filme, categorias):
		try:
			for categoria in categorias:			
				CategoriasFilme.objects.create(filme=filme, categoria=categoria)
		except Exception, e:
			print('Nao foi possivel extrais categorias para filme: '+str(e))

	def salvar_categorias_seriado(self, seriado, categorias):
		try:
			for categoria in categorias:			
				CategoriasSeriado.objects.create(seriado=seriado, categoria=categoria)
		except Exception, e:
			print('Nao foi possivel extrais categorias para filme: '+str(e))

	def salvar_link_filme(self, filme, link, legenda, ehtorrent):
		try:		

			dublado = True
			if legenda != '-':
				dublado = False

			LinksFilme.objects.create(filme=filme, link=link, legenda=legenda, qualidade='480p', dublado=dublado, fonte=0, torrent=ehtorrent)
		except Exception, e:
			print('Nao foi possivel salvar link para filme: '+str(e))

	def salvar_link_episodios_seriado(self, episodio, link, legenda, ehtorrent):
		try:		
			dublado = True
			if legenda != '-':
				dublado = False

			LinksEpisodioSeriado.objects.create(episodio=episodio, link=link, legenda=legenda, dublado=dublado, qualidade='480p', fonte=0, torrent=ehtorrent)
		except Exception, e:
			print('Nao foi possivel salvar link para episodio: '+str(e))
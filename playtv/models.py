# -*- coding: utf-8 -*-
from django.db import models

STATUS_EXECUCAO = (
	(0, 'PARADO'),
	(1, 'REPRODUZINDO'),
	(2, 'PAUSADO'),
	(3, 'STREAM'),
)

class LinkStream(models.Model):
	QUALIDADE = (
		('480p', 'HDTV'),
		('720p', 'HD'),
		('1080p', 'FULLHD'),
	)
	FONTE_URL = (
		(0, 'INTERNET'),
		(1, 'YOUTUBE'),
	)
	link = models.TextField()
	qualidade = models.CharField(max_length=5, choices=QUALIDADE, default='720p')
	dublado = models.BooleanField(default=True)
	fonte = models.SmallIntegerField(choices=FONTE_URL, default=0)	
	torrent = models.BooleanField(default=False)
	legenda = models.CharField(max_length=500)
	seeds = models.PositiveIntegerField(default=0)
	peers = models.PositiveIntegerField(default=0)
	
	class Meta:
		abstract = True

class Ator(models.Model):
	nome = models.CharField(max_length=50, unique=True)

	class Meta:
		verbose_name = 'Ator'
		verbose_name_plural = 'Atores'

	def __unicode__(self):
		return u"{0}".format(self.nome)


class Categoria(models.Model):
	titulo = models.CharField(max_length=50, unique=True)
	titulo_ingles = models.CharField(max_length=50, unique=True)
	imagem = models.URLField(max_length=500, verbose_name='Endereço para miniatura')

	class Meta:
		verbose_name = 'Categoria'
		verbose_name_plural = 'Categorias'

	def __unicode__(self):
		return u"{0}".format(self.titulo)

# Create your models here.
class Filme(models.Model):	
	titulo = models.CharField(max_length=50, unique=True)
	titulo_ingles = models.CharField(max_length=50, unique=True)
	sinopse = models.TextField(verbose_name='Sinopse/Enredo') # enredo
	imagem = models.URLField(max_length=500, verbose_name='Endereço para miniatura')
	status_execucao = models.SmallIntegerField(choices=STATUS_EXECUCAO, default=0)
	
	carga_automatica = models.BooleanField(verbose_name='Carga automatica', default=False)

	classificacao_imdb = models.DecimalField(max_digits=5, decimal_places=2)
	votos_imdb = models.DecimalField(max_digits=10, decimal_places=3)
	tipo = models.CharField(max_length=20, default='movie')

	data_criacao = models.DateTimeField('Data de cadastro', auto_now_add=True)
	data_atualizacao = models.DateTimeField('Data de ultima atualizacao', auto_now=True)

	class Meta:
		verbose_name = 'Filme'
		verbose_name_plural = 'Filmes'

	def __unicode__(self):
		return self.titulo

class CategoriasFilme(models.Model):
	categoria = models.ForeignKey('Categoria')
	filme = models.ForeignKey('Filme')

	class Meta:
		verbose_name = 'Categoria do filme'
		verbose_name_plural = 'Categorias do filme'

	def __unicode__(self):
		return self.filme.titulo

class AtoresFilme(models.Model):
	filme = models.ForeignKey('Filme')
	ator = models.ForeignKey('Ator')

	class Meta:
		verbose_name = 'Ator do filme'
		verbose_name_plural = 'Atores do filme'

	def __unicode__(self):
		return self.ator.nome


class LinksFilme(LinkStream):
	filme = models.ForeignKey('Filme')
	execucao = models.ForeignKey('Execucao', null=True)

	class Meta:
		verbose_name = 'Link para assistir o filme'
		verbose_name_plural = 'Links do filme'

	def __unicode__(self):
		return self.filme.titulo

class Seriado(models.Model):
	titulo = models.CharField(max_length=50, unique=True)
	titulo_ingles = models.CharField(max_length=50, unique=True)
	sinopse = models.TextField(verbose_name='Sinopse/Enredo')
	imagem = models.URLField(max_length=500, verbose_name='Endereço para miniatura')

	carga_automatica = models.BooleanField(verbose_name='Carga automatica', default=False)

	classificacao_imdb = models.DecimalField(max_digits=5, decimal_places=2)
	votos_imdb = models.DecimalField(verbose_name='Quantidade de votos no imdb', max_digits=10, decimal_places=3)
	tipo = models.CharField(max_length=20, default='series')

	data_criacao = models.DateTimeField('Data de cadastro', auto_now_add=True)
	data_atualizacao = models.DateTimeField('Data de ultima atualizacao', auto_now=True)

	class Meta:
		verbose_name = 'Seriado'
		verbose_name_plural = 'Seriados'

	def __unicode__(self):
		return self.titulo

class CategoriasSeriado(models.Model):
	seriado = models.ForeignKey('Seriado')
	categoria = models.ForeignKey('Categoria')

	class Meta:
		verbose_name = 'Categoria do seriado'
		verbose_name_plural = 'Categorias do seriado'

	def __unicode__(self):
		return self.seriado.titulo

class AtoresSeriado(models.Model):
	seriado = models.ForeignKey('Seriado')
	ator = models.ForeignKey('Ator')

	class Meta:
		verbose_name = 'Ator do seriado'
		verbose_name_plural = 'Atores do seriado'

	def __unicode__(self):
		return self.ator.nome

class Episodio(models.Model):
	seriado = models.ForeignKey('Seriado')
	titulo = models.CharField(max_length=50)
	episodio = models.SmallIntegerField(default=1)
	temporada = models.SmallIntegerField(default=1)
	status_execucao = models.SmallIntegerField(choices=STATUS_EXECUCAO, default=0)	
	carga_automatica = models.BooleanField(verbose_name='Carga automatica', default=False)

	data_criacao = models.DateTimeField('Data de cadastro', auto_now_add=True)
	data_atualizacao = models.DateTimeField('Data de ultima atualizacao', auto_now=True)

	class Meta:
		verbose_name = 'Episodio seriado'
		verbose_name_plural = 'Episodios seriado'

	def __unicode__(self):
		return 'Episodio {0} da temporada {1}'.format(self.episodio, self.temporada)

class LinksEpisodioSeriado(LinkStream):
	episodio = models.ForeignKey('Episodio')
	execucao = models.ForeignKey('Execucao', null=True)

class Importacao(models.Model):
	link = models.URLField(max_length=500)
	detalhe = models.CharField(max_length=200)

	importacao_concluida = models.BooleanField(default=False)

	data_atualizacao = models.DateTimeField('Data de ultima atualizacao', auto_now=True)

	class Meta:
		verbose_name = 'Importacao'
		verbose_name_plural = 'Importacoes'

	def __str__(self):
		if self.importacao_concluida:
			return 'Exportacao concluida'
		else:
			return 'Exportacao nao concluida'	


class Execucao(models.Model):
	""" Controlar quantas execucoes existem e em qual ip e porta esta disponivel a reproducao"""

	# REMOTE_ADDR
	endereco_ip_solicitante = models.CharField(max_length=100)
	# REMOTE_HOST
	nome_maquina_solicitante = models.CharField(max_length=100)
	# TOKEN
	token = models.CharField(max_length=255)
	# IP para peerfl
	ip_executando = models.CharField(max_length=100)
	# Porta para Peerflixix
	porta_executando = models.PositiveIntegerField(default=0)
	# Status execucao
	status_execucao = models.SmallIntegerField(choices=STATUS_EXECUCAO, default=0)

	class Meta:
		verbose_name = 'Em execucao'
		verbose_name_plural = 'Em execucao'

	def __str__(self):
		return 'Disponivel em http://{0}:{1}/'.format(self.ip_executando, self.porta_executando)
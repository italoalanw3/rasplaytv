# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import *

class LinkStreamInline(admin.StackedInline):
	extra = 1
	list_display = ('qualidade', 'dublado')

	class Meta:
		abstract = True

class CategoriasSeriadoInline(admin.StackedInline):
	model = CategoriasSeriado
	extra = 1

class CategoriasFilmeInline(admin.StackedInline):
	model = CategoriasFilme
	extra = 1

class AtoresSeriadoInline(admin.StackedInline):
	model = AtoresSeriado
	extra = 1

class AtoresFilmeInline(admin.StackedInline):
	model = AtoresFilme
	extra = 1

class LinkInline(LinkStreamInline):
	model = LinksFilme

class LinkEpisodioInline(LinkStreamInline):
	model = LinksEpisodioSeriado

class CategoriaAdmin(admin.ModelAdmin):	
	list_display = ('titulo','titulo_ingles',)
	search_field = ['titulo','titulo_ingles']
	ordering = []
	ordering += list_display

class ImportacaoAdmin(admin.ModelAdmin):	
	list_display = ('link','detalhe','importacao_concluida','data_atualizacao',)
	search_field = ['link','detalhe','importacao_concluida','data_atualizacao']
	ordering = []
	ordering += list_display

class AtorAdmin(admin.ModelAdmin):	
	list_display = ('nome',)
	search_field = ['nome']
	ordering = []
	ordering += list_display

class FilmeAdmin(admin.ModelAdmin):
	inlines = [
		LinkInline,
		CategoriasFilmeInline,
		AtoresFilmeInline
	]
	list_display = ('titulo', 'status_execucao','sinopse',)
	search_field = ['titulo', 'status_execucao','sinopse']
	ordering = []
	ordering += list_display

class SeriadoAdmin(admin.ModelAdmin):	
	inlines = [
		CategoriasSeriadoInline,
		AtoresSeriadoInline
	]
	list_display = ('titulo', 'sinopse',)
	search_field = ['titulo', 'sinopse']
	ordering = []
	ordering += list_display

class EpisodioSeriadoAdmin(admin.ModelAdmin):
	inlines = [
		LinkEpisodioInline
	]
	list_display = ('seriado', 'titulo', 'episodio', 'temporada', 'status_execucao',)
	search_field = ['seriado', 'titulo', 'episodio', 'temporada', 'status_execucao']
	ordering = []
	ordering += list_display	

# Register your models here.
admin.site.register(Filme, FilmeAdmin)
admin.site.register(Importacao, ImportacaoAdmin)
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Ator, AtorAdmin)
admin.site.register(Seriado, SeriadoAdmin)
admin.site.register(Episodio, EpisodioSeriadoAdmin)
admin.site.register(Execucao)
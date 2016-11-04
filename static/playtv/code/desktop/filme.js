$(document).ready(function(){
    console.log('Carregou JQuery 2.2.0 filmes.js');
    
    setTimeout(function(){
    	initTable = function () {
			var table = $('#filmes');

	        /* Table tools samples: https://www.datatables.net/release-datatables/extras/TableTools/ */

	        /* Set tabletools buttons and button container */

	        $.extend(true, $.fn.DataTable.TableTools.classes, {
	            "container": "btn-group tabletools-dropdown-on-portlet",
	            "buttons": {
	                "normal": "btn btn-sm default",
	                "disabled": "btn btn-sm default disabled"
	            },
	            "collection": {
	                "container": "DTTT_dropdown dropdown-menu tabletools-dropdown-menu"
	            }
	        });

	        var oTable = table.dataTable({

	            // Internationalisation. For more info refer to http://datatables.net/manual/i18n
	            "language": {
	                "aria": {
	                    "sortAscending": ": ativado ordem crescente",
	                    "sortDescending": ": ativado ordem decrescente"
	                },
	                "emptyTable": "No data available in table",
	                "info": "Mostrando _START_ ate _END_ de _TOTAL_ filmes",
	                "infoEmpty": "Nenhum filme cadastrado",
	                "infoFiltered": "(Filtrado total de _MAX_ filmes)",
	                "lengthMenu": "Mostrando _MENU_ filmes",
	                "search": "Pesquisar:",
	                "zeroRecords": "Nenhum filme encontrado"
	            },

	            // Or you can use remote translation file
	            //"language": {
	            //   url: '//cdn.datatables.net/plug-ins/3cfcc339e89/i18n/Portuguese.json'
	            //},

	            "order": [
	                [0, 'asc']
	            ],
	            
	            "lengthMenu": [
	                [5, 10, 15, 20, -1],
	                [5, 10, 15, 20, "All"] // change per page values here
	            ],
	            // set the initial value
	            "pageLength": 10,

	            "dom": "<'row' <'col-md-12'T>><'row'<'col-md-6 col-sm-12'l><'col-md-6 col-sm-12'f>r><'table-responsive't><'row'<'col-md-5 col-sm-12'i><'col-md-7 col-sm-12'p>>", // horizobtal scrollable datatable

	            // Uncomment below line("dom" parameter) to fix the dropdown overflow issue in the datatable cells. The default datatable layout
	            // setup uses scrollable div(table-scrollable) with overflow:auto to enable vertical scroll(see: assets/global/plugins/datatables/plugins/bootstrap/dataTables.bootstrap.js). 
	            // So when dropdowns used the scrollable div should be removed. 
	            //"dom": "<'row' <'col-md-12'T>><'row'<'col-md-6 col-sm-12'l><'col-md-6 col-sm-12'f>r>t<'row'<'col-md-5 col-sm-12'i><'col-md-7 col-sm-12'p>>",
	        });

	        var tableWrapper = $('#filmes_wrapper'); // datatable creates the table wrapper by adding with id {your_table_jd}_wrapper
	}
 		carregar_videos(0, '/filmes/todos/', 0, 0); 
    },1000);
});

function carregar_videos(tipo_video, url, id, temporada){
	var dadosParaEnvio = {
		id : id
	};	
	$.ajax({
		url: url,
		type: 'POST',
		data: JSON.stringify(dadosParaEnvio),
		dataType: 'json',
		contentType: 'application/json',
		success: function(data){ 			

			console.log(data);
			var conteudo = '';
			var imagem = {};
			var acumuladorTempo = 0;
			$.each(data, function(chave, video){								
				if (tipo_video == tipos_video.filme){
					imagem = {
						altImagem: video.fields.sinopse,
						srcImagem: video.fields.imagem
					};
				} else {
					var seriado = JSON.parse(localStorage.getItem('seriadoEscolhido'));
					imagem = {
						altImagem: 'Episódio',
						srcImagem: seriado.fields.imagem
					};
					console.log(imagem);
					video.fields.titulo = video.fields.episodio+'º episódio - '+video.fields.titulo;					
				}	

				$("#filmes tbody").append('<tr>'+
	                  '<td class="highlight">'+	                                 
	                    '<img src="'+imagem.srcImagem+'" alt="150x180" style="height: 180px; width: 150px; display: block;" title="'+video.fields.titulo+'/'+video.fields.titulo_ingles+'" data-src="holder.js/100%x180">'+
	                  '</td>'+
	                  '<td class="hidden-xs">'+
	                  	'<div class="success">'+
	                    '</div>'+	       
	                  	video.fields.titulo+'/'+video.fields.titulo_ingles+	
	                  '</td>'+
	                  '<td class="hidden-xs">'+
	                  	video.fields.sinopse+
	                  '</td>'+
	                  '<td class="hidden-xs">'+
	                  '<input data-readonly="true" data-default-caption="'+video.fields.votos_imdb + ' votos" class="rating" data-min="0" data-max="10" data-step="0.1" data-size="sm" data-stars=5'+
    					' data-glyphicon="true" data-show-clear="false" data-show-caption="true" value="'+Number(video.fields.classificacao_imdb)+'" >'+
	                  '</td>'+
	                  '<td id="links'+video.pk+'">'+	                    
	                  '</td>'+
	                '</tr>  ');

				localStorage.setItem("video-"+video.pk, JSON.stringify(video));
				carregar_links(tipo_video, video.pk, '/filmes/links-filme/');		
	        	
			});	
			$(".rating").rating({
			    starCaptions: {1: "Muito ruim", 3: "Ruim", 5: "Bom", 7: "Ótimo", 9: "Muiito boM!! :)"},
			    starCaptionClasses: {1: "text-danger", 3: "text-warning", 5: "text-info", 7: "text-primary", 9: "text-success"},
			});			
			initTable();
		}, error: function(a,b,c){
			console.error('Erro: ');
			console.error(a);			
			console.error(b);			
		}
	});
}
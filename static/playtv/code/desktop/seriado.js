$(document).ready(function(){
    console.log('Carregou JQuery 2.2.0 filmes.js');
    
    setTimeout(function(){
    	initTable = function () {
			var table = $('#seriados');

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
	                "info": "Mostrando _START_ ate _END_ de _TOTAL_ seriados",
	                "infoEmpty": "Nenhum seriado cadastrado",
	                "infoFiltered": "(Filtrado total de _MAX_ seriados)",
	                "lengthMenu": "Mostrando _MENU_ seriados",
	                "search": "Pesquisar:",
	                "zeroRecords": "Nenhum seriado encontrado"
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

	        var tableWrapper = $('#seriados_wrapper'); // datatable creates the table wrapper by adding with id {your_table_jd}_wrapper
	}
 		carregar_seriados(); 
    },1000);
});

function carregar_seriados(){	
	$.ajax({
		url: '/seriados/todos/',
		type: 'POST',
		dataType: 'json',
		contentType: 'application/json',
		success: function(data){ 			

			console.log(data);			
			$.each(data, function(chave, seriado){								

				$("#seriados tbody").append('<tr>'+
	                  '<td class="highlight">'+	                                 
	                    '<a href="#" onclick="temporadas('+seriado.pk+')">'+
	                    '<img src="'+seriado.fields.imagem+'" alt="150x180" style="height: 180px; width: 150px; display: block;" title="'+seriado.fields.titulo+'/'+seriado.fields.titulo_ingles+'" data-src="holder.js/100%x180">'+
	                  	'</a>'+
	                  '</td>'+
	                  '<td class="hidden-xs">'+
	                  	'<div class="success">'+
	                    '</div>'+	       
	                  	seriado.fields.titulo+'/'+seriado.fields.titulo_ingles+	
	                  '</td>'+
	                  '<td class="hidden-xs">'+
	                  	seriado.fields.sinopse+
	                  '</td>'+
	                  '<td class="hidden-xs">'+
	                  '<input data-readonly="true" data-default-caption="'+seriado.fields.votos_imdb + ' votos" class="rating" data-min="0" data-max="10" data-step="0.1" data-size="sm" data-stars=5'+
    					' data-glyphicon="true" data-show-clear="false" data-show-caption="true" value="'+Number(seriado.fields.classificacao_imdb)+'" >'+
	                  '</td>'+
	                '</tr>  ');

				localStorage.setItem("seriado-"+seriado.pk, JSON.stringify(seriado));	        	
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

function temporadas(pk_seriado){
	var seriado = JSON.parse(localStorage.getItem('seriado-'+pk_seriado));

	$("#portlet-title").html('<i class="fa fa-film"></i>Exibindo temporadas disponíveis para '+seriado.fields.titulo);

	localStorage.setItem('backup-seriados', $("#seriados").html());

	var oTable = $('#seriados').dataTable();
	oTable.fnDestroy();
	$("#seriados").empty();

	$("#botoes").empty();
	$("#botoes").append('<li><a href="#" onclick="voltar()"><i class="fa fa-angle-left"></i> Voltar para seriados</a></li>');

	$.ajax({
		url: '/seriados/temporadas/',
		type: 'POST',
		data: JSON.stringify(pk_seriado),
		dataType: 'json',		
		contentType: 'application/json',
		success: function(data){ 			

			console.log(data);	
			$("#seriados").html(' <thead>'+
	                '<tr>'+
	                '  <th>'+
	                '    Temporadas de '+seriado.fields.titulo+
	                '  </th>	  '+                
	                '</tr>'+
	                '</thead>'+
	                '<tbody>'+		                             
	                '</tbody>');
			$.each(data, function(chave, temporada){								
				console.log(temporada);							
				$("#seriados tbody").append('<tr><td class="highlight">'+	                                 
	                    '<a href="#" class="btn default btn-xs purple" onclick="ver_episodios_temporadas('+seriado.pk+','+temporada+')">Ver episódios da '+temporada+'ª temporada'+
	                  	'</a>'+
	                  '</td></tr>');
			});							
		}, error: function(a,b,c){
			console.error('Erro: ');
			console.error(a);			
			console.error(b);			
		}
	});
}

function voltar(){
	$("#seriados").empty();
	$("#seriados").html(localStorage.getItem('backup-seriados'));

	initTable();
	$("#botoes").empty();
}

function voltar_temporadas(pk_seriado){
	$("#seriados").empty();
	$("#seriados").html(localStorage.getItem('backup-seriados-temporadas'));

	$("#botoes").empty();
	$("#botoes").append('<li><a href="#" onclick="voltar()"><i class="fa fa-angle-left"></i> Voltar para seriados</a></li>');

	var seriado = JSON.parse(localStorage.getItem('seriado-'+pk_seriado));

	$("#portlet-title").html('<i class="fa fa-film"></i>Exibindo temporadas disponíveis para '+seriado.fields.titulo);
}

function ver_episodios_temporadas(pk_seriado, temporada){

	$("#portlet-title").html('<i class="fa fa-film"></i>Exibindo episódios da '+temporada+'ª temporada');

	$("#botoes").empty();
	$("#botoes").append('<li><a href="#" onclick="voltar_temporadas('+pk_seriado+')"><i class="fa fa-angle-left"></i> Voltar para temporadas</a></li>');

	localStorage.setItem('backup-seriados-temporadas', $("#seriados").html());
	$("#seriados").empty();

	var dadosParaEnvio = {
		id : pk_seriado,
		temporada: temporada
	};
	$.ajax({
		url: '/seriados/episodios-dessa-temporada/',
		type: 'POST',
		data: JSON.stringify(dadosParaEnvio),
		dataType: 'json',		
		contentType: 'application/json',
		success: function(data){ 			

			console.log(data);			

			$("#seriados").html(' <thead>'+
	                '<tr>'+
	                '  <th>Episódio</th>'+                
	                '  <th> '+
	                '  </th>'+                
	                '</tr>'+
	                '</thead>'+
	                '<tbody>'+		                             
	        		'</tbody>');

			$.each(data, function(chave, episodio){								
				console.log(episodio);							
				$("#seriados tbody").append('<tr>'+
					'<td class="highlight">'+episodio.fields.episodio+
	                '</td>'+
	                '<td id="links'+episodio.pk+'">'+	                    
	                '</td>'+
	                '</tr>');

				carregar_links(1, episodio.pk, '/seriados/links-episodio/');			        			
			});				
		}, error: function(a,b,c){
			console.error('Erro: ');
			console.error(a);			
			console.error(b);			
		}
	});
}
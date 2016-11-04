var initTable;
$(document).ready(function(){
    console.log('Carregou JQuery 2.2.0 principal.js'); 
    
});

$('#reproduzir-tv').on('show.bs.modal', function(e) {
	$("#play").attr('data-pk-video', $(e.relatedTarget).data('pk-video'));
	$("#play").attr('data-pk-link', $(e.relatedTarget).data('pk-link'));
	$("#play").attr('data-tipo-video', $(e.relatedTarget).data('tipo-video'));
});

function adicionar_videos(src_video){
	$("#video").empty();
	$("#video").html('<video id="tag-video" autoplay controls preload="acumuladorTempo">'+
                     '  <source id="tag-video-source" media="all and (max-width:480px)" src="'+src_video+'" type="video/mp4">'+
                     '    Your browser does not support the video tag.'+
                     '</video>');
}

$('#reproduzir-aqui').on('show.bs.modal', function(e) {
	if ($("#tag-video-source").attr('src') == $(e.relatedTarget).data('video')) {
		return;
	} else {
		adicionar_videos($(e.relatedTarget).data('video'));
	} 
});

function pausar(){
	var vid = document.getElementById("tag-video"); 
	vid.pause();
}

var tipos_video = {
	'filme' : 0,
	'seriado': 1 
}

function carregar_links(tipo_video, pk_video, url){	
	$.ajax({
		url: url,
		type: 'POST',
		data: JSON.stringify(pk_video),
		dataType: 'json',
		contentType: 'application/json',
		success: function(data){			
			$.each(data, function(chave, link){
				console.log('Link');
				console.log(link);
				if (link.status_execucao == 3){
					var urlVideo = 'http://'+link.ip_executando+':'+link.porta_executando+'/';
					$("#links"+pk_video).html('<span class="label label-success">'+
										 'Executando em: <a target="_blank" href="http://'+link.ip_executando+':'+link.porta_executando+'/">'+urlVideo+
									 '</a></span>');

					$("#links"+pk_video).append('<br><a style="margin-top: 5px;" href="javascript:;" class="btn default btn-xs red" onclick="parar_stream('+link.pk+','+pk_video+','+tipo_video+')">'+
		                    		   '<i class="fa fa-unlink"></i> Interromper stream </a>');

					$("#links"+pk_video).append('<br><a download href="'+urlVideo+'" style="margin-top: 5px;" class="btn default btn-xs blue">'+
		                    		   '<i class="fa fa-download"></i> Baixar </a>');					

					$("#links"+pk_video).append('<br><a data-pk-video="'+pk_video+'" data-pk-link="'+link.pk+'" data-tipo-video="'+tipo_video+'" href="#reproduzir-tv" data-toggle="modal" style="margin-top: 5px;" href="javascript:;" id="link-omxplayer'+link.pk+'" class="btn default btn-xs blue">'+
		                    		   '<i class="fa fa-desktop"></i> Iniciar na TV </a>');					

					$("#links"+pk_video).append('<br><a data-video="'+urlVideo+'" data-pk-video="'+pk_video+'" data-pk-link="'+link.pk+'" data-tipo-video="'+tipo_video+'" href="#reproduzir-aqui" data-toggle="modal" style="margin-top: 3px;" href="javascript:;" id="link-omxplayer'+link.pk+'" class="btn default btn-xs green">'+
		                    		   '<i class="fa fa-film"></i> Iniciar aqui </a>');										

					$("#links"+pk_video).append('<br><br><object classid="clsid:9BE31822-FDAD-461B-AD51-BE1D1C159921" codebase="http://download.videolan.org/pub/videolan/vlc/last/win32/axvlc.cab" id="vlc">'+
	   				   '<embed pluginspage="http://www.videolan.org" controls="true" type="application/x-vlc-plugin" name="VLC" autoplay="yes" loop="no" volume="100" width="480" target="'+urlVideo+'">'+
					   '</object>');

					var vlc = $("#vlc");
					console.log('VLC: ');
					console.log(vlc);
					vlc.subtitle = 1;
					vlc.video.subtitle = 1;
					console.log(vlc.subtitle);
					console.log(vlc.video);
				}
				else {
					if (link.torrent || link == 'undefined'){
						$('#links'+pk_video).append('<a style="margin-top: 10px;" href="javascript:;" id="iniciarStream'+link.pk+'" class="btn default btn-xs purple" onclick="stream('+link.pk+','+pk_video+','+tipo_video+')"">'+
		                    				   		'<i class="fa fa-magnet"></i> Iniciar Stream </a>');

						localStorage.setItem('link-'+link.pk, JSON.stringify(link));
					}
				}

			});			
		}, error: function(a,b,c){
			console.error('Erro: ');
			console.error(a);			
			console.error(b);			
		}
	});
}

<<<<<<< HEAD
function stream_browser(pk_link, pk_video, tipo_video){	

	link = JSON.parse(localStorage.getItem('link-'+pk_link));

	console.log(link.link);

	//magnet:?xt=urn:btih:6a9759bffd5c0af65319979fb7832189f4f3c35d
	client.add(link.link, function(torrent) {
	  // Got torrent metadata!
	  console.log('Client is downloading:', torrent.infoHash)

	  torrent.on('download', function(chunkSize){
		  console.log('chunk size: ' + chunkSize);
		  console.log('total downloaded: ' + torrent.downloaded);
		  console.log('download speed: ' + torrent.downloadSpeed);
		  console.log('progress: ' + torrent.progress);
		  console.log('======');
		})

	  torrent.files.forEach(function (file) {
	    // Display the file by appending it to the DOM. Supports video, audio, images, and
	    // more. Specify a container element (CSS selector or reference to DOM node).
	    file.appendTo('#video-stream')
	  })
	});
}

=======
>>>>>>> b037753c1b191641c5b821eee19cbcf219d0eb99
function stream(pk_link, pk_video, tipo_video){	

	var link = {
		tipo_video: Number(tipo_video),
		pk_link: Number(pk_link)
	};
	$("#iniciarStream"+pk_link).attr('disabled', true);
	$("#iniciarStream"+pk_link).html('<i class="fa fa-gear fa-spin"></i> Bufferizando torrent');
	$.ajax({
		url: '/stream/iniciar/',
		type: 'POST',
		dataType: 'json',
		data: JSON.stringify(link),
		contentType: 'application/json',
		success: function(data){
			console.log('sucesso');			
			console.log(data);
			var urlVideo = "http://"+data[0].fields.ip_executando+":"+data[0].fields.porta_executando+"/";
			$("#links"+pk_video).html('<span class="label label-success">'+
										 'Executando no endereço: <a target="_blank" href="'+urlVideo+'">'+urlVideo+
									 '</a></span>');

			$("#links"+pk_video).append('<br><a id="pararStream'+pk_link+'" style="margin-top: 5px;" href="javascript:;" class="btn default btn-xs red" onclick="parar_stream('+pk_link+','+pk_video+','+tipo_video+')">'+
		                    		   '<i class="fa fa-unlink"></i> Interromper stream </a>');

			$("#links"+pk_video).append('<br><a style="margin-top: 5px;" data-pk-video="'+pk_video+'" data-pk-link="'+pk_link+'" data-tipo-video="'+tipo_video+'" href="#reproduzir-tv" data-toggle="modal" class="btn default btn-xs blue">'+
		                    		   '<i class="fa fa-desktop"></i> Iniciar na TV </a>');

			$("#links"+pk_video).append('<a data-video="'+urlVideo+'" style="margin-top: 5px;" data-pk-video="'+pk_video+'" data-pk-link="'+pk_link+'" data-tipo-video="'+tipo_video+'" href="#reproduzir-aqui" data-toggle="modal" class="btn default btn-xs green">'+
		                    		   '<i class="fa fa-film"></i> Iniciar aqui</a>');

			$("#links"+pk_video).append('<object classid="clsid:67DABFBF-D0AB-41fa-9C46-CC0F21721616" width="320" height="260" codebase="http://go.divx.com/plugin/DivXBrowserPlugin.cab">'+
			'<param name="custommode" value="none" />'+
  			'<param name="previewImage" value="/media/imdb/Pretty_Little_Liars.jpg" />'+
			  '<param name="autoPlay" value="false" />'+
			  '<param name="src" value="'+urlVideo+'" />'+
			'<embed type="video/divx" src="'+urlVideo+'" custommode="none" width="320" height="260" autoPlay="false"  previewImage="/media/imdb/Pretty_Little_Liars.jpg"  pluginspage="http://go.divx.com/plugin/download/">'+
			'</embed>'+
			'</object>'+
			'<br />No video? <a href="http://www.divx.com/software/divx-plus/web-player" target="_blank">Download</a> the DivX Plus Web Player.');

			
			console.log(urlVideo);
			$("#reproduzir-aqui").modal('show');
			adicionar_videos(urlVideo);
			
		}, error: function(a,b,c){
			$("#iniciarStream"+pk_link).attr('disabled', false);
			$("#iniciarStream"+pk_link).html('<i class="fa fa-magnet "></i> Falha, tente novamente');
			console.error('Erro: ');
			console.error(a);			
			console.error(b);
		}
	});
}

function parar_stream(pk_link, pk_video, tipo_video){	
	$(".invalid"+pk_link).empty();
	var link = {
		tipo_video: Number(tipo_video),
		pk_link: Number(pk_link)
	};
	$("#pararStream"+pk_link).attr('disabled', true);
	$("#pararStream"+pk_link).html('<i class="fa fa-gear fa-spin"></i> Interrompendo stream');
	$.ajax({
		url: '/stream/parar/',
		type: 'POST',
		dataType: 'json',
		data: JSON.stringify(link),
		contentType: 'application/json',
		success: function(data){
			console.log('sucesso');			
			console.log(data);			
			if (data.resposta) {
						$('#links'+pk_video).empty();
						$('#links'+pk_video).append('<a id="iniciarStream'+pk_link+'" href="javascript:;" class="btn default btn-xs purple" onclick="stream('+pk_link+','+pk_video+','+tipo_video+')"">'+
		                    				   		'<i class="fa fa-magnet"></i> Iniciar Stream </a>');
			} else {
				$('#links'+pk_video).append('<span style="margin-top: 15px;" class="label label-danger invalid'+pk_link+'">'+data.objeto+
									 		'</a></span>');
			}

			setTimeout(function(){
				$(".invalid"+pk_link).empty();	
			}, 5000);
		}, error: function(a,b,c){
			$("#pararStream"+pk_link).attr('disabled', false);
			$("#pararStream"+pk_link).html('<i class="fa fa-magnet "></i> Falha, tente novamente');
			console.error('Erro: ');
			console.error(a);			
			console.error(b);
		}
	});
}

function play_omx_player(){	

	var tipo_video = Number($("#play").attr('data-tipo-video'));
	var pk_video = Number($("#play").attr('data-pk-video'));
	var pk_link = Number($("#play").attr('data-pk-link'));

	var link = {
		tipo_video: tipo_video,
		pk_link: pk_link,
		endereco_ip: $("#endereco_ip").val(),
		usuario: $("#usuario").val(),
		senha: $("#senha").val()
	};

	$.ajax({
		url: '/video/play/',
		type: 'POST',
		dataType: 'json',
		data: JSON.stringify(link),
		contentType: 'application/json',
		success: function(data){
			console.log('sucesso');			
			console.log(data);		
			$.each(data, function(chave, video){
				
			});						
		}, error: function(a,b,c){
			console.error('Erro: ');
			console.error(a);			
			console.error(b);
		}
	});
}

function play_pause_omx_player(tipo_video, pk_video){
	var link = {
		tipo_video: 0,
		pk_video: 0
	};
	$.ajax({
		url: '/video/play_pause/',
		dataType: 'json',
		data: JSON.stringify(link),
		type: 'POST',
		contentType: 'application/json',
		success: function(data){
			console.log(data);
			if (data[0].fields.status_execucao == 1){				
				
        		console.log('Retomado!');			
			} else if (data[0].fields.status_execucao == 2){				
        		console.log('Pausado!');			
			}
			$("#ligar_parar"+pk_video).show();			
		}, error: function(a,b,c){
			console.error('Erro: ');
			console.error(a);			
			console.error(b);
		}
	});
}

function voltar_omx_player(tipo_video, pk_video){
	var link = {
		tipo_video: 0,
		pk_video: 0
	};
	$.ajax({
		url: '/video/voltar/',
		dataType: 'json',
		data: JSON.stringify(link),
		type: 'POST',
		contentType: 'application/json',
		success: function(data){
			
		}, error: function(a,b,c){
			
			console.error('Erro: ');
			console.error(a);			
			console.error(b);
		}
	});
}

function avancar_omx_player(tipo_video, pk_video){
	var link = {
		tipo_video: 0,
		pk_video: 0
	};
	$.ajax({
		url: '/video/avancar/',
		dataType: 'json',
		data: JSON.stringify(link),
		type: 'POST',
		contentType: 'application/json',
		success: function(data){
			
		}, error: function(a,b,c){			
			console.error('Erro: ');
			console.error(a);			
			console.error(b);
		}
	});
}

function stop_omx_player(tipo_video, pk_video){
	var link = {
		tipo_video: 0,
		pk_video: 0
	};
	$.ajax({
		url: '/video/stop/',
		dataType: 'json',
		type: 'POST',
		data: JSON.stringify(link),
		contentType: 'application/json',
		success: function(data){
			console.log('Parado!');			
		}, error: function(a,b,c){
			console.error('Erro: ');
			console.error(a);			
			console.error(b);
		}
	});
}
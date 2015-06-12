/**
 * show movie info
 */
poster_handler = new Poster();
online_tv_handler = new OnlineTv();
online_movie_handler = new OnlineMovie();
netdisk_handler = new Netdisk();
detail_handler = new Detail();
complete_handler = new Complete();
episode_handler = new Episode();

var add_modtify_commit = function(e){
		e.preventDefault();
		
		var detail = detail_handler.get(), /* 影视简介 */
			image = poster_handler.get(), /* 图片数据 */
			netdisk = netdisk_handler.get(), /* 网盘全集资源 */
			complete = complete_handler.get(), /* 全集资源 */
			episode = episode_handler.get(); /* 分集资源 */
		
		/* 在线分集资源 */
		if (detail.type == 'movie') {
			online = online_movie_handler.get();
		}else{
			online = online_tv_handler.get();
		}
		
		if (image == '' || detail.genre == '' || (online.length==0 && netdisk.length==0 && complete.length == 0 && episode.length == 0)) {
			return false;
		}
		
		detail.image = image;
		var post = {
			oid:$("#match-load").attr('data'), /* 抓取数据库中的附加数据 */
			data:{info:detail, resource:{online:online, netdisk:netdisk, complete:complete, episode:episode}}
		};
		
		$.post(_.sprintf("/admin/%s/save/", collection),
			JSON.stringify(post), 
			function(data){
				if (data.status == 'success') {
					window.location.href = data.redirect;
				}
			}, 
			'json'
		);
		
		return false;
};

function render_search_result(data) {
	var render = function(pattern, out, data){
		if (data.length) {
			console.log(data);
			
			var template = Handlebars.compile($(pattern).html());
			$(out).html(template({item:data}));
		}else{
            $(out).empty();
        }
	},
	fill_content = function(e) {
		var $target = $(this), id = $target.attr('id');
		
		if ( $target.parent().attr("id") == 'douban_result_show' ) {
			var douban_show = true;
		}else{
			var douban_show = false;
		}
		
		/* 基于豆瓣ID进行去重复 */
		if ($("#oid").val() != '') {
			var req_url = _.sprintf("/admin/%s/fill/?direct", collection);
		}else{
			var req_url = _.sprintf("/admin/%s/fill/", collection);
		}
		
		$.getJSON( req_url, {id:id}, function(data){
			if (data['status'] == 'redirect') {
				$('#title').val(data['data']);
				$("#title_check").trigger('click');
			}else if (data['status'] == 'success') {
				console.log(data);
				
				/* 初次从本地数据库中加载需要清理数据 */
				if (douban_show == false) {
					detail_handler.reset();
					online_movie_handler.reset();
					online_tv_handler.reset();
					netdisk_handler.reset();
					complete_handler.reset();
					episode_handler.reset();
				}
				
				poster_handler.reset();
				
				detail_handler.show(data['data']['info'], data['data']['info']['_id']);
				poster_handler.adds(data['data']['info']['image']);
				
				if (data['data']['info']['type'] === 'movie') {
					online_movie_handler.adds(data['data']['resource']['online']);
				}else{
					online_tv_handler.adds(data['data']['resource']['online']);
				}
				
				netdisk_handler.adds(data['data']['resource']['netdisk']);
				complete_handler.adds(data['data']['resource']['complete']);
				episode_handler.adds(data['data']['resource']['episode']);
				
				$("#match-load").trigger('click');
				
				/* 加载成功之后取消加载事件 */
				$('#' + $target.parent().attr("id") + ' li' ).unbind("click");
			}
		});
		return false;
	};
	
	render("#inside_show", '#inside_result_show', data['inside']);
	render("#douban_show", '#douban_result_show', data['douban']);
	
	if (data['inside'].length || data['douban'].length) {
		$('ul#inside_result_show li').click(fill_content);
		$('ul#douban_result_show li').click(fill_content);
	}
}

/* 匹配加载函数 */
function add_resource(complete, online, netdisk, episode, type) {
	if (online.length) {
		if (type == 'movie') {
			online_movie_handler.adds(online);
		}else{
			online_tv_handler.adds(online);
		}
	}
	if (complete.length) {
		complete_handler.adds(complete);
	}
	if (netdisk.length) {
		netdisk_handler.adds(netdisk);
	}
	if (episode.length) {
		episode_handler.adds(episode);
	}
}

function match_load_event_handler(e) {
	e.preventDefault();
	
	var type =  $("type").val();
	var resource = window.match.resource,
		complete = resource.complete,
		online = resource.online,
		netdisk = resource.netdisk,
		episode = resource.episode;
	
	add_resource(complete, online, netdisk, episode, type);
	
	var samesite = $("#samesite").val();
	if (samesite) {
		samesite = samesite + '\n' + window.match.source.join('\n');
	}else{
		if (typeof(window.match.source) == 'string') {
			samesite = window.match.source;
		}else{
			samesite = window.match.source.join('\n');
		}
	}
	
	$("#samesite").val(samesite);
	
	$("#match-load").unbind('click').removeClass('btn-primary');
	return false;
}

$(document).ready(function() {
	_.mixin(_.string.exports());
	
	$($("#add_main li a")[0]).trigger('click');
	
	$('.nav-tabs > li > a').hover( function(){
		$(this).tab('show');
	});
	
	poster_handler.initialize();
	online_movie_handler.initialize();
	online_tv_handler.initialize();
	netdisk_handler.initialize();
	detail_handler.initialize();
	complete_handler.initialize();
	episode_handler.initialize();
	
	/**
	 * query by movie title
	 */
	$("#title-commit").click(add_modtify_commit);
	
	$("#title_check").click(function(e){
		e.preventDefault();
		
		var title = $("#title").val();
		var douban = $("#douban").val();
		
		if (title == '' && douban == '') {
			return false;
		}
		
		if (title) {
			/* 电影名字匹配 */
			$.getJSON(_.sprintf("/admin/%s/query/", collection), {title:title}, render_search_result);
		}else if (douban) {
			/* 直接基于豆瓣ID进行匹配 */
			$.getJSON(_.sprintf("/admin/%s/query/", collection), { douban:douban }, function(e){
				render_search_result(e);
				if (e['inside'].length) {
					$('ul#inside_result_show li').trigger('click');
				}else{
					$('ul#douban_result_show li').trigger('click');
				}
			});
		}
		
		return false;
	});
	
	$.getJSON(_.sprintf("/admin/%s/load/", collection), function(e){
		if (e['status'] == 'success' && e['data'] != null) {
			var data = e['data'];
			window.match = data;
			
			if (typeof(data.source) == 'string') {
				$("#match-desc").val(data.desc + '\n' + data.title + '\n' + data.source);
			}else{
				$("#match-desc").val(data.desc + '\n' + data.title + '\n' + data.source.join('\n'));
			}
			
			$("#match-load").attr('data', data._id.$oid);
			$("#match-block").attr('data', _.sprintf("/admin/%s/block/?oid=%s", collection, data._id.$oid));
			$("#match-reserve").attr('data', _.sprintf("/admin/%s/reserve/?oid=%s", collection, data._id.$oid));
			$("#match-delete").attr('data', _.sprintf("/admin/%s/delete/?oid=%s", collection, data._id.$oid));
			
            $(".match-job").click(function(e){
                $.getJSON($(e.target).attr('data'), function(e){
                    if (e.status == 'success') {
                        location.reload();
                    }
                });
                return false;
            });
            
			if (data.level == 999) {
				$("#douban").val(data.title);
				$.getJSON(_.sprintf("/admin/%s/query/", collection), {douban:data.title}, function(e){
					render_search_result(e);
					$('ul#douban_result_show li').trigger('click');
				});
			}else{
				$("#title").val(data.title);
				$.getJSON(_.sprintf("/admin/%s/query/", collection), {title:$("#title").val()}, render_search_result);
			}
			
			if (data.patch == true) {
				$("#match-load").unbind('click').removeClass('btn-success');
				$.getJSON(_.sprintf("/admin/%s/patch/?oid=%s", collection, data._id.$oid), function(e){
					if (e.status == 'success') {
						window.match.resource = e.data;					
						$("#match-load").addClass('btn-success').click(match_load_event_handler);
					}
				});
			}else{
				$("#match-load").click(match_load_event_handler);
			}
		}
	});
});

/* 一集一个资源，多集对应一个资源 */
/**
 * Episode process class
 */

/* URL 校验函数 */
var validate_url = function( value ) {
	// contributed by Scott Gonzalez: http://projects.scottsplayground.com/iri/
	return /^(https?|s?ftp):\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?)(:\d*)?)(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i.test( value );
};

function Episode() {
	var storage = Array();
	
	var pre_block = Handlebars.compile($("#episode-block-template").html()), /* 抓取站点模板 */
		pre_tab = Handlebars.compile($("#episode-tab-template").html()), /* Tab 模板 */
		pre_detail = Handlebars.compile($("#episode-detail-template").html()),
		pre_button = Handlebars.compile($("#episode-button-template").html()); /* 添加一集按钮 模板 */
	
	/* 资源站点标签显示 */
	var tab_show_eh = function(e){
		
		var site = e.data,
			group_id = $(e.target).attr('data-id'),
			group = _.find(site.resource, function(target){ return target.id == group_id;});
		
		$("#episode-detail-" + site.id).html(pre_detail(group));
		
		/* 注册资源添加处理函数 */
		/* 单集按钮事件 */
		$("#episode-detail-show-" + group_id).click({group:group, gid:group_id}, function(e){
			e.preventDefault();
			var group = e.data.group, gid=e.data.gid, el = $(e.target), current = el.attr('data');
			var episode = _.find(group.episode, function(target){ return target.num == current;});
			
			if (episode != undefined) {
				$("#quality-"+gid).val(episode.quality);
				$("#size-"+gid).val(episode.size);
				$("#name-"+gid).val(episode.name);
				$("#link-"+gid).val(episode.link);
				$("#current-"+gid).val(episode.num);
			}else{
				console.log('current episode from ' + gid + ' not found');
			}
			
			return false;
		});
		/* 重置 */
		$("#episode-add-reset-" + group_id).unbind('click').click({group:group, gid:group_id}, function(e){
			e.preventDefault();
			var group = e.data.group, gid=e.data.gid;
			
			$("#quality-"+gid).val('');
			$("#size-"+gid).val('');
			$("#name-"+gid).val('');
			$("#link-"+gid).val('');
			$("#current-"+gid).val(group.current);
			
			return false;
		});
		/* 1. 手动添加 */
		$("#episode-add-add-" + group_id).unbind('click').click({site:site, gid:group_id}, function(e){
			e.preventDefault();
			var site = e.data.site, gid=e.data.gid,
				group = _.find(site.resource, function(target){ return target.id == gid;}),
				quality = $("#quality-"+gid).val(),
				size = $("#size-"+gid).val(),
				name = $("#name-"+gid).val(),
				current = $("#current-"+gid).val(),
				link = $("#link-"+gid).val();
			
			if (link) {
				if (quality == '') {
					quality = 'DVD';
				}
				
				var episode = _.find(group.episode, function(target){ return target.num == current;});
				if (episode != undefined) {/* change action */
					episode.link = link;
					episode.quality = quality;
					episode.size = size;
					episode.name = name;
				}else{
					var episode = {link:link, quality:quality, size:size, name:name, num:current};
					
					group.episode.push(episode);
					$("#episode-detail-show-" + gid).append(pre_button(episode));
					
					group.current = group.current + 1;
				}
				
				$("#quality-"+gid).val('');
				$("#size-"+gid).val('');
				$("#name-"+gid).val('');
				$("#link-"+gid).val('');
				$("#current-"+gid).val(group.current);
			}
			
			return false;
		});
		/* 电驴、迅雷链接 */
		$("#episode-add-ed2k-" + group_id).unbind('click').click({site:site, gid:group_id}, function(e){
			e.preventDefault();
			
			var site = e.data.site, gid=e.data.gid,
				group = _.find(site.resource, function(target){ return target.id == gid;}),
				current = $("#current-"+gid).val(),
				link = $("#link-"+gid).val();
				
			if (link != '') {
				$.post("/admin/process_ed2k/", {ed2k:link}, function(e){
					if (e.status == 'success') {
						var episode = {quality:e.quality, size:e.size, name:e.name, link:e.link, num:current};
						
						group.episode.push(episode);
						$("#episode-detail-show-" + gid).append(pre_button(episode));
						
						$("#quality-"+gid).val('');
						$("#size-"+gid).val('');
						$("#name-"+gid).val('');
						$("#link-"+gid).val('');
						group.current = group.current + 1;
						$("#current-"+gid).val(group.current);	
					}	
				});
			}
			
			return false;
		});
		/* bt种子 */
		$("#episode-add-bt-" + group_id).fileupload({
			url: '/admin/process_bt/',
			dataType: 'json',
			pre: {site:site, gid:group_id},
			done: function (e, data) {
				var r = data.result,
					site = data.pre.site, gid=data.pre.gid,
					group = _.find(site.resource, function(target){ return target.id == gid;}),
					current = $("#current-"+gid).val();
				
				if (r.status == 'success') {
					var episode = {quality:r.quality, size:r.size, name:r.name, link:r.link, num:current};
					
					group.episode.push(episode);
					$("#episode-detail-show-" + gid).append(pre_button(episode));
					
					$("#quality-"+gid).val('');
					$("#size-"+gid).val('');
					$("#name-"+gid).val('');
					$("#link-"+gid).val('');
					group.current = group.current + 1;
					$("#current-"+gid).val(group.current);	
				}	
			}
		});
	};
	
	/* 新建资源站点事件处理函数 */
	var ng_button_eh = function(e){
		e.preventDefault();
		console.log('add a new resource group');
		
		var el = $(e.target), id = el.attr('data-id') /* crawl site id */,
			group = {current:1, episode:[], id:_.uniqueId()},
			site = _.find(storage, function(target){ return target.id == id;});
		
		if (site != undefined) {
			console.log(site);
			site.resource.push(group);
			
			var render_tab = $("#episode-tab-" + site.id);
			render_tab.find(".episode-tab-items").remove();
			render_tab.append(pre_tab({items:site.resource}));
			
			/* 加载单集资源 */
			$("#episode-tab-" + site.id + ' a[data-toggle="tab"]').on('shown', site, tab_show_eh);
			
			/* 触发首个项目 */
			$("#episode-tab-" + site.id + " .episode-tab-items:last a").trigger('click');
		}else{
			console.log('not found site from storage use ' + id + ', this id');
		}
	};
	
	/* 抓取站点起始事件函数 */
	var es_button_eh = function(e){
		e.preventDefault();
		
		var target_link = $("#episode-crawl-source").val();
		
		if ( validate_url(target_link) ) {
			$("#episode-crawl-source").val('');
			
			/* 抓取站点的URL资源整体模板加载 */
			var site = {from:target_link, resource:[], id:_.uniqueId()};
			
			storage.push(site);
			$("#render-episode-resource").prepend(pre_block(site));
			$("#episode-new-group-" + site.id).click(ng_button_eh);
		}
		
		return false;
	};
	
	this.add = function(site){
		// patch id for data from outside
		site.id = _.uniqueId();
		_.each(site.resource, function(s){
			s.id = _.uniqueId();
			s.current = s.episode.length + 1;
		});
		
		/* 资源存入数组 */
		storage.push(site);
		
		/* 显示抓取站点的整体资源模板 */
		$("#render-episode-resource").prepend(pre_block(site));
		$("#episode-new-group-" + site.id).click(ng_button_eh);
		
		/* 显示单项规格的数据组 */
		var render_tab = $("#episode-tab-" + site.id);
		render_tab.find(".episode-tab-items").remove();
		render_tab.append(pre_tab({items:site.resource}));
		$("#episode-tab-" + site.id + ' a[data-toggle="tab"]').on('shown', site, tab_show_eh);
		$("#episode-tab-" + site.id + " .episode-tab-items:last a").trigger('click');
	};
	
	this.adds = function(scrapy_site_group){
		_.each(scrapy_site_group, this.add);
	};
	
	this.get = function(){
		var ret = $.extend(true, [], storage);
		
		_.each(ret, function(r){
			delete r.id;
			_.each(r.resource, function(s){
				delete s.id;
				delete s.current;
			});
		});
		
		return ret;
	};
	
	this.reset = function(){
		storage = Array();
	};
	
	/* register global button event */
	this.initialize = function(){
		$('#episode-start-button').click(es_button_eh);
	};
}

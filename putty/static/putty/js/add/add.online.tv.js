/**
 * Online process class
 */

/* URL 校验函数 */
var validate_url = function( value ) {
	// contributed by Scott Gonzalez: http://projects.scottsplayground.com/iri/
	return /^(https?|s?ftp):\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?)(:\d*)?)(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i.test( value );
};

function OnlineTv() {
	var storage = Array();
	
	var pre_block = Handlebars.compile($("#online-block-template").html()), /* 抓取站点模板 */
		pre_tab = Handlebars.compile($("#online-tab-template").html()), /* Tab 模板 */
		pre_detail = Handlebars.compile($("#online-detail-template").html()),
		pre_button = Handlebars.compile($("#online-button-template").html()); /* 添加一集按钮 模板 */
	
	/* 资源站点标签显示 */
	var tab_show_eh = function(e){
		
		var target = e.data,
			sid = $(e.target).attr('data-id'),
			site = _.find(target.resource, function(target){ return target.id == sid;});
		
		$("#online-detail-" + target.id).html(pre_detail(site));
		
		/* 单集按钮事件 */
		$("#online-detail-show-" + sid).click({site:site, sid:sid}, function(e){
			e.preventDefault();
			var site = e.data.site, sid=e.data.sid, el = $(e.target), current = el.attr('data');
			var episode = _.find(site.episode, function(target){ return target.num == current;});
			
			if (episode != undefined) {
				$("#link-" + sid).val(episode.link);
				$("#current-" + sid).val(episode.num);
			}else{
				console.log('current online episode from ' + sid + ' not found');
			}
			
			return false;
		});
		
		/* 单集添加事件处理 */
		$('#online-add-add-' + sid).click({target:target, sid:sid}, function(e){
			e.preventDefault();
			
			var target = e.data.target, sid = e.data.sid,
				site = _.find(target.resource, function(target){ return target.id == sid;}),
				link = $("#link-" + sid).val(), current = $("#current-" + sid).val();
			
			if (validate_url(link)) {
				
				var episode = _.find(site.episode, function(target){ return target.num == current;});
				if (episode != undefined) {/* change action */
					episode.link = link;
				}else{
					var episode = {link:link, num:current};
					site.episode.push(episode);
					$("#online-detail-show-" + sid).append(pre_button(episode));
					
					site.current += 1;
				}
				
				$("#link-" + sid).val('');
				$("#current-" + sid).val(site.current);
			}
			
			return false;
		});
	};
	
	/* 新建资源站点事件处理函数 */
	var dm_button_eh = function(e){
		e.preventDefault();
		console.log('add a new resource site');
		
		var el = $(e.target), id = el.attr('data-id') /* scrapy site id */,
			site = {name:el.attr('data-name'), logo:el.attr('data-logo'), current:1, episode:[], id:_.uniqueId()},
			target = _.find(storage, function(target){ return target.id == id;});
		
		target.resource.push(site);
		
		var render_tab = $("#online-tab-" + target.id);
		render_tab.find(".online-tab-items").remove();
		render_tab.append(pre_tab({items:target.resource}));
		
		/* 加载单集资源 */
		$("#online-tab-" + target.id + ' a[data-toggle="tab"]').on('shown', target, tab_show_eh);
		
		/* 触发首个项目 */
		$("#online-tab-" + target.id + " .online-tab-items:first a").trigger('click');
	};
	
	/* 抓取站点事件函数，加载整个模板 */
	var ors_button_eh = function(e){
		e.preventDefault();
		
		var target_link = $("#online-crawl-source").val();
		
		if ( validate_url(target_link) ) {
			$("#online-crawl-source").val('');
			
			/* 抓取站点的URL资源整体模板加载 */
			var target = {from:target_link, resource:[], id:_.uniqueId()};
			
			storage.push(target);
			$("#render-online-resource").prepend(pre_block(target));
			
			$('#dropdown-menu-' + target.id).click(dm_button_eh);
		}
		
		return false;
	};
	
	this.add = function(target){
		// patch id for data from outside
		target.id = _.uniqueId();
		_.each(target.resource, function(s){
			s.id = _.uniqueId();
			s.current = s.episode.length + 1;
		});
		
		storage.push(target);
		
		$("#render-online-resource").prepend(pre_block(target));
		$('#dropdown-menu-' + target.id).click(dm_button_eh);
		
		var render_tab = $("#online-tab-" + target.id);
		render_tab.find(".online-tab-items").remove();
		render_tab.append(pre_tab({items:target.resource}));
		$("#online-tab-" + target.id + ' a[data-toggle="tab"]').on('shown', target, tab_show_eh);
		$("#online-tab-" + target.id + " .online-tab-items:last a").trigger('click');
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
		$('#online-start-button').click(ors_button_eh);
	};
}

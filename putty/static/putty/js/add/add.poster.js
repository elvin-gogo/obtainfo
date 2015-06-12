/*
 * 图片处理类
 * 
 * 1. 手动添加图片，从URL或者从本地图片
 * 2. 初始化的时候添加图片
 */

var validate_url = function( value ) {
	// contributed by Scott Gonzalez: http://projects.scottsplayground.com/iri/
	return /^(https?|s?ftp):\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?)(:\d*)?)(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i.test( value );
};

function Poster() {
	var self = this,
		storage = Array(),
		post_url = '/admin/process_image/?split=True',
		pre_dit = Handlebars.compile($("#display_image").html());
	
	this.render = function () {
		
		$('#render_image_show').html( pre_dit({items:storage}) );
		
		$("input[type='checkbox'][name='DS']").on('change', function (e) {
			var $target = $(e.target),
				selnum = $("input[type='checkbox'][name='DS']:checked").length,
				index = _.find(storage, function(s){return $target.attr('data') == s.index});
			
			if ($target.is(':checked')) { // unchecked, un support this
				if ( selnum > 1) {
					$("input[type='checkbox'][name='DS']:checked").each(function(){
						var j = $(this),
							img = _.find(storage, function(s){return j.attr('data') == s.index});
						if (img != index) {
							img['DS'] = 'None';
							j.prop("checked",false);
						}
					})
				}
				
				index['DS'] = $target.attr('name');
			}else{
				$target.prop("checked",true);
			}
			
			return false;
		});
		
		$("input[type='checkbox'][name='DH']").on('change', function (e) {
			var $target = $(e.target),
				selnum = $("input[type='checkbox'][name='DH']:checked").length,
				index = _.find(storage, function(s){return $target.attr('data') == s.index});
			
			if ($target.is(':checked')) { // unchecked, un support this
				if ( selnum > 1) {
					$("input[type='checkbox'][name='DH']:checked").each(function(){
						var j = $(this),
							img = _.find(storage, function(s){return j.attr('data') == s.index});
						if (img != index) {
							img['DH'] = 'None';
							j.prop("checked",false);
						}
					})
					
				}
				
				index['DH'] = $target.attr('name');
			}else{
				$target.prop("checked",true);
			}
			
			return false;
		});
	};
	
	function update(images) {
		_.each(storage, function(s){s['DH']=''; s['DS']='';});
		_.each(images, function(img){img['index']=_.uniqueId();});
		storage = storage.concat(images);
		
		self.render();
	}
	
	this.add = update;
	this.adds = update;
	
	this.reset = function(){
		storage = Array();
	};
	
	this.get = function(){
		/* use defualt image, set flag to server */
		if ( $('input[name="poster-checkbox"]').bootstrapSwitch('state') ){
			
			image = 'default';
			
		}else{
			big = _.find(storage, function(s){return s['DH'] === 'DH'});
			small = _.find(storage, function(s){return s['DS'] === 'DS'});
			
			if (big && small) {
				image = { DS:{url:small.url, name:small.name}, DH:{ url:big.url, name:big.name} };	
			}else{
				console.log('movie image not set');
				image = "";
			}
		}
		
		return image;
	};
	
	this.initialize = function(){
		$("#add_img_url").click(function(e){
			e.preventDefault();
			
			var img = $("#image_url").val();
			if (validate_url(img)) {
				$.getJSON(post_url,
					{img:img},
					function(data){
						update(data['data']);
						$("#image_url").val("");
					}
				);
			}
			
			return false;
		});
		
		$('#fileupload').fileupload({
			url: post_url,
			dataType: 'json',
			done: function (e, data){ update(data['result']['data']); }
		});
		
		$("[name='poster-checkbox']").bootstrapSwitch();
	};
}

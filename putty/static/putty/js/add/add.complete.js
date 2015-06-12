/*
 * 完整剧集资源处理类
 * 
 */

function Complete() {
	var self = this,
		storage = Array(),
		pre_drt = Handlebars.compile($("#display_resource").html());
	
	this.render = function() {
		var result = String();
		
		for (var i=0; i<storage.length; i++) {
			var data = storage[i];
			data['index'] = i;
			result += pre_drt(data);
		}
		
		$('#render_resource_show').html(result);
		
		/* edit or del */
		$('#render_resource_show').unbind("click").click(function (e) {
			e.preventDefault();
			var $target = $(e.target),
				index = parseInt($target.attr("data"));
			
			if ($target.text() == "Del") {
				storage.splice(index, 1);
				self.render();
			}else{ // Edit
				var data = storage[index];
				
				$("#resource_new").val(index);
				$("#resource_quality").val(data['quality']);
				$("#resource_size").val(data['size']);
				$("#resource_name").val(data['name']);
				$("#resource_link").val(data['link']);		
			}
			
			return false;
		});
	};
	
	function update(complete) {
		storage = storage.concat(complete);
		self.render();
	}
	
	this.add = update;
	this.adds = update;
	
	this.get = function(){
		var ret = $.extend(true, [], storage);
		_.each(ret, function(r){delete r.index;});
		return ret;
	};
	
	this.reset = function(){
		storage = Array();
	};
	
	this.initialize = function(){
		$("#resource_add_reset").click(function(e){
			e.preventDefault();
			
			$("#resource_new").val("true");
			$("#resource_quality").val("");
			$("#resource_size").val("");
			$("#resource_name").val("");
			$("#resource_link").val("");
			
			return false;
		});
		
		$("#resource_add").click(function(e){
			e.preventDefault();
			
			var isnew = $("#resource_new").val(),
				quality = $("#resource_quality").val(),
				size = $("#resource_size").val(),
				name = $("#resource_name").val(),
				link = $("#resource_link").val();
				
			if (link == '') {
				return false;
			}
			
			if (quality == '') {
				quality = 'DVD';
			}
			
			if (isnew == 'true') {
				storage.push({quality:quality, size:size, name:name, link:link});
			}else{
				var index = parseInt(isnew);
				storage[index]['quality'] = quality;
				storage[index]['size'] = size;
				storage[index]['name'] = name;
				storage[index]['link'] = link;
			}
			
			$("#resource_new").val("true");
			$("#resource_quality").val("");
			$("#resource_size").val("");
			$("#resource_name").val("");
			$("#resource_link").val("");
			
			self.render();
			
			return false;
		});
	
		$("#resource_add_ed2k").click(function(e){
			e.preventDefault();
			
			var link = $("#resource_link").val();
				
			if (link != '') {
				$.post("/admin/process_ed2k/", {ed2k:link}, function(e){
					if (e.status == 'success') {
						storage.push({quality:e.quality, size:e.size, name:e.name, link:e.link});
						
						$("#resource_new").val("true");
						$("#resource_quality").val("");
						$("#resource_size").val("");
						$("#resource_name").val("");
						$("#resource_link").val("");
						
						self.render();		
					}	
				});
			}
			
			return false;
		});
		
		$('#btupload').fileupload({
			url: '/admin/process_bt/',
			dataType: 'json',
			done: function (e, data) {
				var r = data['result'];
				storage.push({quality:r['quality'], size:r['size'], name:r['name'], link:r['link']});
				self.render();
			}
		});
	};
}

/**
 * netdisk process class
 * 
 */
/* URL 校验函数 */
var validate_url = function( value ) {
	// contributed by Scott Gonzalez: http://projects.scottsplayground.com/iri/
	return /^(https?|s?ftp):\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?)(:\d*)?)(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i.test( value );
};

function Netdisk() {
	var pre_dnrt = Handlebars.compile($("#display-netdisk-resource").html()),
		storage = Array();
	
	var self = this;
	
	this.render = function(){
		var result = String();
		for (var i=0; i<storage.length; i++) {
			var data = storage[i];
			data['index'] = i;
			result += pre_dnrt(data);
		}
		
		$('#render-netdisk-show').html(result);
		
		/* del button */
		$('#render-netdisk-show').unbind("click").click(function (e) {
			e.preventDefault();
			var $target = $(e.target),
				index = parseInt($target.attr("data"));
			
			if ($target.text() == "Del") {
				storage.splice(index, 1);
				self.render();
			}
			
			return false;
		});
	}
	
	this.add = function(site){
		storage.push(site);
		self.render();
	};
	
	this.adds = function(sites){
		_.each(sites, this.add);
	};
	
	this.get = function(){
		return storage;
	};
	
	this.reset = function(){
		storage = Array();
	};
	
	this.initialize = function(){
		
		$("#netdisk-add-reset").click(function(e){
			e.preventDefault();
			
			$("#netdisk-link").val("");
			$("#netdisk-code").val("");
			
			return false;
		});
		
		$("#netdisk-add").click(function(e){
			e.preventDefault();
			var link = $("#netdisk-link").val(), code = $("#netdisk-code").val();
				
			if (validate_url(link)) {
				storage.push({'link':link, 'code':code});
				$("#netdisk-link").val('');
				$("#netdisk-code").val('');
				
				self.render();
			}
			
			return false;
		});
	};
}

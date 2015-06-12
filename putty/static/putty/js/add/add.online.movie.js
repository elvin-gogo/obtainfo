/**
 * Online process class
 */

/* URL 校验函数 */
var validate_url = function( value ) {
	// contributed by Scott Gonzalez: http://projects.scottsplayground.com/iri/
	return /^(https?|s?ftp):\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?)(:\d*)?)(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i.test( value );
};

function OnlineMovie() {
	var storage = Array(),
		self = this,
		pre_block = Handlebars.compile($("#movie-online-template").html()); /* 资源显示模板 */
	
	this.render = function() {
		var result = String();
		
		for (var i=0; i<storage.length; i++) {
			var data = storage[i];
			data['index'] = i;
			result += pre_block(data);
		}
		
		$('#render_movie_online_show').html(result);
		
		/* del button */
		$('#render_movie_online_show').unbind("click").click(function (e) {
			e.preventDefault();
			var $target = $(e.target),
				index = parseInt($target.attr("data"));
			
			if ($target.text() == "Del") {
				storage.splice(index, 1);
				self.render()
			}
			
			return false;
		});
	}

	this.add = function(target){
		storage.push(target);
		self.render();
	};
	
	this.adds = function(groups){
		_.each(groups, function(g){self.add(g);});
	};
	
	this.get = function(){
		return storage;
	};
	
	this.reset = function(){
		storage = Array();
	};
	
	/* register global button event */
	this.initialize = function(){
		$("#movie_online_add_reset").click(function(e){
			e.preventDefault();
			$("#movie_online_link").val("");
			return false;
		});
		
		$("#movie_online_add").click(function(e){
			e.preventDefault();
			var link = $("#movie_online_link").val();
			
			if (validate_url(link)) {
				storage.push({'link':link});
				$("#movie_online_link").val("");
				
				self.render();
			}
			
			return false;
		});
	};
}

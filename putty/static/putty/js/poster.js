var Poster = function(Jquery) {
	// build template
	var nav_render_template    = Handlebars.compile( $("#display_nav_item").html() ),
	 	detail_render_template = Handlebars.compile( $("#display_detail_item").html() ),
	 	search_render_template = Handlebars.compile( $("#inside_show").html() ),
	 	match_render_template  = Handlebars.compile( $("#inside_second_show").html() ),
	 	image_render_template  = Handlebars.compile( $("#display_input_img").html() ),
	 	check_render_template  = Handlebars.compile( $("#check_show").html() );

	var posters = Array(), checks = Array(), process = Array();

	/**
	 * 图片显示
	 */
	var render_image = function( dat ) {
		if (dat.status == 'success') {
			$('#render_image_show').html(image_render_template(dat.data[0]));
			
			// finish manual add image
			$("#manual_finish").click(function(e){
				e.preventDefault();
				// commit to server, save
				var info = $("#render_match_show .result_items"),
					title=info.attr("title"), 
					oid=info.attr("oid"),
					url = $("#render_image_show .caption img").attr("src");
				
				var post = { method:'save', data:[{ title:title, oid:oid, pic:url, remote:false}] };
				// render new list
				$.post("/admin/poster/", JSON.stringify(post), function(e){
					if (e.status == 'success'){
						window.location.href = "/admin/poster/";
					}
				});
				
				return false;
			});
		}
	};

	var render_detail_detail = function(content){
		$('#detail').empty().html( detail_render_template(content) );
		
		$("#detail-action").on('click', function(e){
			e.preventDefault();
				
			var el = $(e.target), 
				method = el.attr('method'), 
				bid = el.attr('bid');
				
			$.post("/admin/poster/", 
				JSON.stringify({method:method, data:bid}), 
				function(data){
					if (data.status == 'success') {
						window.location.href = "/admin/poster/";
					}
			});
			
			return false;
		});
	},
	render_check_detail = function(e){
		$('#check').empty().html(check_render_template(e));
		
		$("#check_save").unbind('click').click(function(e){
			e.preventDefault();
			var mid=$("select[name=MID]").val(), 
				img = $("select[name=IMG]").val(),
				el = $(e.target), 
				opts = checks, 
				id = el.attr('data');
			
			for (var i in opts){
				if (opts[i]['id'] == id) {
					var checked = checks.splice(i, 1)[0];

					process.push({oid:mid, pic:img, title:checked.title, remote:true, action:'use', id:checked.id});
					
					if (checks.length) {
						update_nav_list(checks);
					}else{
						// all checked
						$("#check_commit").trigger("click");
					}
					break;
				}
			}

			return false;
		});

		$("#check_commit").on('click', function(e){
			e.preventDefault();

			if (process.length) {				
				$.post( "/admin/poster/", 
					JSON.stringify( {method:'save', data:process} ), 
					function(data){
						if (data.status == 'success') {
							window.location.href = "/admin/poster/";
						}
				});
			}

			return false;
		});
		
		// this picture unused, in other word pass this image
		$("#check_pass").unbind('click').click(function(e){
			e.preventDefault();
			var el = $(e.target),
				opts = checks,
				id = el.attr('data');
			
			for (var i in opts){
				if (opts[i]['id'] == id) {
					var checked = checks.splice(i, 1)[0];
					process.push({remote:true, action:'delete', id:checked.id});

					if (checks.length) {
						update_nav_list(checks);
					}else{
						// all checked
						$("#check_commit").trigger("click");
					}
					break;
				}
			}
			return false;
		});
	},
	update_nav_list = function(e){
		var el = $('#nav_content');
		var active = $("#poster_main .active :first-child").attr("href");
		
		el.html(nav_render_template({e:e}));
		
		el.on("click", function(e) {
            e.preventDefault();
            var el = $(e.target), ct = $(this), ol = ct.children(".active"), id = el.attr('data');
			var active = $("#poster_main .active :first-child").attr("href");
			
            if (ol.attr("data") != el.attr("data")){ /* repeat click, ingore */
                if (ol) {
                    ol.removeClass('active'); // remove active class	
                }
                
                el.parent().addClass('active'); // set new active class
                
                if ( active == '#report'){
	                for (var i in posters){
	                    if (posters[i]['id'] == id) {
	                    	render_detail_detail(posters[i]);
	                        break;
	                    }
	                }
                }else if(active == '#check'){
					for (var i in checks){
						if (checks[i]['id'] == id) {
							render_check_detail(checks[i]);
							break;
						}
					}
                }
            }
            
            return false;
        });
		
		// show first
		$("#nav_content li:first a").trigger("click");
	};

	/*
	* bootstrap tab as flat page,  register flat page all event as first stage event
	*/
	this.initialize = function(){
		$.post("/admin/poster/", JSON.stringify({method:'fill'}), function(e){
			posters = e;
			
			$('#pagination').twbsPagination({
				totalPages: parseInt((posters.length + 18 - 1) / 18),
				visiblePages: 6,
				onPageClick: function (event, page) {
					var start = (page - 1) * 18;
					update_nav_list(posters.slice(start, start + 18));
				}
			});
			
			var oid = $("#fill_oid").attr("data");
			if (oid != '') {
				$('#poster_main > .active').next('li').find('a').trigger('click');
				$('#oid').val(oid);
				$('#auto_trigger_search').trigger('click');
			}
		});

		$('a[data-toggle="tab"]').on('show', function (e) {
			var et = $(e.target);
			if (et.attr("href") == "#check") {
				if (checks.length) {
					update_nav_list(checks);
				}else{
					$('#check').spin({top:"30%", left:'60%'});
					$.post("/admin/poster/", JSON.stringify({method:'check'}), function(e){
						checks = e.data;
						$('#check').spin(false);
						update_nav_list(e.data);
					});	
				}
			}else{
				$('#check').spin(false);
				var page = parseInt( $("#pagination .active").find('a').text() );
				var start = (page - 1) * 18;
				update_nav_list(posters.slice(start, start+18));
			}
		});

		$('#auto_trigger_search').click(function(e){
			e.preventDefault();
			var qs = $("input[name=oid]").val();
			
			if (qs){
				var qs = { method:'query', data:qs };
				$.post('/admin/poster/', JSON.stringify(qs), function(data){
					
					var fill_content = function(content){
						$('#render_match_show').html(match_render_template(content));
						$("#first_step").css('display','none');
						$("#second_step").css('display','block');
					};
						
					if (data.status == 'success') {
						if (data.type == 'result' && data.count > 0) { //get an effective query
							
							$('#render_search_show').html(search_render_template(data));
							
							$('ul#inside_result_show li').click( function(e){
								e.preventDefault();
								var el = $(e.target);
								
								while( el.is('li') == false ){
									el = el.parent();
								}
								
								var bid = el.attr('id');
								
								for (var i in data.inside) {
									if (data.inside[i]['id'] == bid) {
										fill_content(data.inside[i]);
										break;
									}
								}
								
								return false;
							});
							
						}else if (data.type == 'oid') { // jump to second step
							fill_content(data.data);
						}
					}
				});
			}

			return false;
		});

		$("#add_img_url").click(function(e){
			e.preventDefault();
			
			var img = $("#image_url").val();
			
			if (img == '') {
				return false;
			}
			
			$.getJSON( "/admin/process_image/", { img:img }, render_image);
			
			return false;
		});
		
		$('#fileupload').fileupload({
			url: '/admin/process_image/',
			dataType: 'json',
			done: function (e, d) {
				render_image(d['result']);
			}
		}).prop('disabled', !$.support.fileInput)
			.parent().addClass($.support.fileInput ? undefined : 'disabled');

	}; 

};

$(document).ready(function() {
	var poster = new Poster();
	poster.initialize();
});

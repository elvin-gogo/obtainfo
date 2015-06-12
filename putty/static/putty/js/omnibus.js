/**
 * global data : window.data, window.group
 */
var render_check_detail = function(e){
	var check_render_template  = Handlebars.compile( $("#check_show").html() );
	$('#render_check_show_content').empty().html(check_render_template(e));
	
	$(".choosen").click(function(e){
		e.preventDefault();
		
		var index = parseInt($("#nav_search").find('.active').attr('data'));
		var selected = $(this).attr('id');
		var opts = window.data.data.list;
		
		for (var i in opts){
			if (opts[i]['id'] == index) {
				var item = window.data.data.list.splice(i, 1)[0];
				window.list.push(selected);
				
				if (opts.length) {
					update_nav_list(window.data);
				}else{
					// all checked
					window.data.data.list = window.list;
					$.post( "/admin/selection/commit/", 
						JSON.stringify( window.data.data ), 
						function(data){
							if (data.status == 'success') {
								window.location.href = "/admin/selection/";
							}
					});
				}
				break;
			}
		}
		
		return false;
	});
};

var update_nav_list = function(e){
	var data = e.data, count = e.count, total = e.total;
	
	if (count) {
		var nav_render_template = Handlebars.compile( $("#display_nav_item").html() );
		var el = $('#nav_content');
		el.html(nav_render_template({e:data, total:total, count:count}));
		
		$("#nav_search").on("click", function(e) {
			e.preventDefault();
			var el = $(e.target), ct = $(this), ol = ct.children(".active"), id = el.attr('data');
			
			if (ol.attr("data") != el.attr("data")){ /* repeat click, ingore */
				if (ol) {
					ol.removeClass('active'); // remove active class	
				}
				
				el.parent().addClass('active'); // set new active class
				
				var checks = window.data.data.list;
				for (var i in checks){
					if (checks[i]['id'] == id) {
						render_check_detail(checks[i]);
						break;
					}
				}
			}
			
			return false;
		});
		
		// show first
		$("#nav_content li:first a").trigger("click");
	}
};

$(document).ready(function() { 
	
	$(".detail-edit").click(function(e){
		var $this = $(e.target), data = $this.attr("data");
		var post = {method:'pre_edit', data:data};
		if ( data == '') {
			return false;
		}
		
		$.post( '/admin/selection/', post, function(data){
			if (data.status == 'success') {
				// window.location.href = '/admin/omnibus/';
				$("#detail").empty().multiselect2side({
						commit_url : "/admin/selection/commit/",
						after_url : "/admin/selection/append/",
						redirect_url:"/admin/selection/"
					}, data.data
				);
			}
		}, 'json');
		
		return false;
	});
	
	$(".detail-del").click(function(e){
		var $this = $(e.target), data = $this.attr("data");
		var post = {method:'del', data:data};
		if ( data == '') {
			return false;
		}
		
		$.post( '/admin/selection/', post, function(data){
			if (data.status == 'success') {
				window.location.href = '/admin/selection/';
			}
		}, 'json');
		
		return false;
	});
	
	$("#rollback").click(function(e){
		$("#first_step").css('display','block');
		$("#second_step").css('display','none');
	});
	
	$('#formtolist_btn').click(function(e){
		e.preventDefault();
		var title = $("input[name='title']").val(),
			content = $("textarea[name='content']").val(),
			desc = $("#selection-desc").val();
			
		var bigpic = '';
		var stdpic = '';
		
		if (window.showlist[0].DH == 'DH') {
			var bigpic = window.showlist[0]['url'];
			var stdpic = window.showlist[1]['url'];
		}else{
			var bigpic = window.showlist[1]['url'];
			var stdpic = window.showlist[0]['url'];
		}
		
		
		if (title == '' || content == '' || stdpic == '' || desc == ''){
			return false;
		}
		
		$.post('/admin/selection/list/', 
			{title:title, content:content, stdpic:stdpic, bigpic:bigpic, desc:desc},
			function(e){
				if (e.count) {
					window.data = e;
					window.list = Array();
					
					$("#first_step").css('display','none');
					$("#second_step").css('display','block');
					update_nav_list(e);
				}
			}
		);
		
		return false;
	});

	$('#douban_btn').click(function(e){
		e.preventDefault();
		var title = $("input[name='title']").val(),
			content = $("textarea[name='content']").val(),
			desc = $("#selection-desc").val();
			
		if (window.showlist[0].DH == 'DH') {
			var bigpic = window.showlist[0]['url'];
			var stdpic = window.showlist[1]['url'];
		}else{
			var bigpic = window.showlist[1]['url'];
			var stdpic = window.showlist[0]['url'];
		}
		
		if (title == '' || content == '' || bigpic == '' || desc == ''){
			return false;
		}
		
		$.post('/admin/selection/douban/',
			JSON.stringify( {title:title, content:content, bigpic:bigpic, stdpic:stdpic, desc:desc} ), 
			function(e){
				if (e.status == 'success') {
					window.location.href = '/admin/selection/';
				}
			}
		);
		
		return false;
	});
	
	/**
	 * 图片显示
	 */
	var render_image = function( dat ) {
		var image_render_template  = Handlebars.compile( $("#display_input_img").html() );
		if (dat.status == 'success') {
			$("#image_url").val('');
			window.showlist = dat.data;
			$('#render_image_show').html(image_render_template({imgs : dat.data}));
		}
	};

	$("#add_img_url").click(function(e){
		e.preventDefault();
		
		var img = $("#image_url").val();
		
		if (img == '') {
			return false;
		}
		
		$.getJSON( "/admin/process_image/?selection=True", { img:img }, render_image);
		
		return false;
	});
	
	$('#fileupload').fileupload({
		url: '/admin/process_image/?selection=True',
		dataType: 'json',
		done: function (e, d) {
			render_image(d['result']);
		}
	}).prop('disabled', !$.support.fileInput).parent().addClass($.support.fileInput ? undefined : 'disabled');
});

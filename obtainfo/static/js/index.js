$(document).ready(function(){
	$('.carousel').carousel({interval:false});
	
	$('#bg-carousel').on('slid', function() {
		$(window).trigger('scroll');
	});

	$('a[data-toggle="tab"]').on('shown', function () {
		$(window).trigger('scroll');
	});
	
	$("img.lazy").lazyload({ effect : "fadeIn" });
	
	$('.video').mouseover(function () {
		$(this).find('.play_icon_shadow').show();
		$(this).find('.play_icon').show();
	}).mouseout(function () {
		$(this).find('.play_icon_shadow').hide();
		$(this).find('.play_icon').hide();
	});
	
	$('.vb-item').mouseover(function () {
		$(this).find('.vbip-icon-shadow').show();
		$(this).find('.vbip-icon').show();
	}).mouseout(function () {
		$(this).find('.vbip-icon-shadow').hide();
		$(this).find('.vbip-icon').hide();
	});
	
	$.getJSON('/lazy/', {s:'recommend', n:30}, function(e){
		if (e.status == 'success') {
			var template = Handlebars.compile($("#sidebar-template").html());
			$("#sidebar").html(template(e.ranking));
		}else{
			$("#sidebar").empty();
		}
	});
});

var opts = {
	lines: 13, // The number of lines to draw
	length: 20, // The length of each line
	width: 10, // The line thickness
	radius: 30, // The radius of the inner circle
	corners: 1, // Corner roundness (0..1)
	rotate: 0, // The rotation offset
	direction: 1, // 1: clockwise, -1: counterclockwise
	color: '#0088cc', // #rgb or #rrggbb or array of colors
	speed: 1, // Rounds per second
	trail: 60, // Afterglow percentage
	shadow: false, // Whether to render a shadow
	hwaccel: false, // Whether to use hardware acceleration
	className: 'spinner', // The CSS class to assign to the spinner
	zIndex: 2e9, // The z-index (defaults to 2000000000)
	top: '100px', // Top position relative to parent
	left: '50%' // Left position relative to parent
};
	
function fetch(argument, spin, page) {
	
	$('#short-content').empty().spin(spin);
	
	global.page = page;
	
	$.post(location.pathname, JSON.stringify(global),
		function(e){
			$('#short-content').spin(false);
			
			var n = 5, per_page = 20;
			var lists = _.groupBy(e.results, function(element, index){
				return Math.floor(index/n);
			});
			lists = _.toArray(lists); //Added this to convert the returned object to an array.
			
			var pre_board = Handlebars.compile($("#viedo-board-template").html());
			var page = e.page, ab = Array();
			page.board = lists;
			for (var i in page.range) {
				ab.push({a:page.range[i], b:page.current})
			}
			page.range = ab;
			
			$('#short-content').html(pre_board(page));
			
			$("#pagination").click(function(e){
				e.preventDefault();
				
				jQuery('html,body').scrollTop(0);
				fetch(global, opts, parseInt($(e.target).attr('page')));
				
				return false;
			});
	});	
}

$(document).ready(function(){
	Handlebars.registerHelper('if_eq', function(a, b, opts) {
		if(a == b)
			return opts.fn(this);
		else
			return opts.inverse(this);
	});
	
	$("img.lazy").lazyload({ effect : "fadeIn" });
		
	$(".condition ul").each(function(){
		var $this = $(this);
		global[$this.attr('data-name')] = parseInt($this.find('.active a').attr('data-val'));
	});
	
	fetch(global, opts, 1);
	
	$(".condition a[data-toggle='pill']").on('shown', function(e){
		var el = $(e.target);
		global[el.parent().parent().attr('data-name')] = parseInt(el.attr('data-val'));
		
		fetch(global, opts, 1);
	});
	
});
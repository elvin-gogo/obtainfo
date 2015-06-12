
var series_template = function() {  
    /*
	<div class="ranking" style="margin-bottom: 14px;">
		<h4>影视系列</h4>
		<ol class="ranklist" style="margin-top: 20px;">
			{{#each series}}
			<li class="list">
				{{#if same}}
				<span class="no no2">{{no}}</span>
				{{else}}
				<span class="no no4">{{no}}</span>
				{{/if}}
				<a href="/detail/{{id}}/" target="_blank" title="{{title}}">{{title}}</a>
			</li>
			{{/each}}
		</ol>
	</div>
    */
};

var ranking_template = function() {  
/*
<div class="ranking">
	<h4>{{title}}</h4>
	<ol class="ranklist">
		<li class="poster">
			<dl>
				<dt>
				<a href="/detail/{{first.id}}/" target="_blank" static="no=1">
					<img src="{{first.image}}" alt="{{first.title}}" width=200 height=92>
					<span class="no no1">1</span>
					<span class="s-title">{{first.title}}</span>
					<span class="v-all-bg">&nbsp;</span>
				</a>
				</dt>
			</dl>
		</li><!--poster-->
        {{#each second}}
		<li class="list">
			<span class="no no{{no}}">{{no}}</span>
			<a href="/detail/{{id}}/" target="_blank" title="{{title}}">{{title}}</a>
		</li>
		{{/each}}
	</ol>
</div>
*/
};

var ranking_template = function() {  
/*
<div class="ranking">
	<h4>{{title}}</h4>
	<ol class="ranklist">
		<li class="poster">
			<dl>
				<dt>
				<a href="/detail/{{first.id}}/" target="_blank" static="no=1">
					<img src="{{first.image}}" alt="{{first.title}}" width=200 height=92>
					<span class="no no1">1</span>
					<span class="s-title">{{first.title}}</span>
					<span class="v-all-bg">&nbsp;</span>
				</a>
				</dt>
			</dl>
		</li><!--poster-->
        {{#each second}}
		<li class="list">
			<span class="no no{{no}}">{{no}}</span>
			<a href="/detail/{{id}}/" target="_blank" title="{{title}}">{{title}}</a>
		</li>
		{{/each}}
	</ol>
</div>
*/
};

Function.prototype.getMultiLine = function() {  
    var lines = new String(this);  
    lines = lines.substring(lines.indexOf("/*") + 3, lines.lastIndexOf("*/"));  
    return lines;  
};

lazyload = function(oid){
	$.getJSON('/lazy/', {s:'hot', n:30, o:oid}, function(e){
		if (e.status == 'success') {
			var template = Handlebars.compile(ranking_template.getMultiLine());
			$("#sidebar").html(template(e.ranking));
			
			if (e.series.length) {
				_.each(e.series, function(s){
					if (s.id == oid) {
						s.same = true;
					}else{
						s.same = false;
					}
				});
				
				var template = Handlebars.compile(series_template.getMultiLine());
				$("#sidebar").prepend(template(e));
			}
		}else{
			$("#sidebar").empty();
		}
	});
}

$(document).ready(function(){
	$("img.lazy").lazyload({ effect : "fadeIn" });
		
	if (window.ismobile == false && i_flash == true)
	{
		$("#copy").zclip({
			path:'http://cdn.staticfile.org/zclip/1.1.2/ZeroClipboard.swf',
			copy:function(){
				return $('.link').attr('href');
			},
			afterCopy:function(){
				$(".link").css({'color':'#51a351'});
				$("#alert-download").css('display','block'); 
			}
		});
	}else{
		$("#copy").css('display','none'); 
	}
	
	$("#torrent-download").click(function(e){
		e.preventDefault();
		var el = $(this);
		jQuery("#add-product-form").submit();
		return false;
	});
	
	if ($("#online-menu").length) {
		$($("#online-menu li a")[0]).trigger('click');	
	}else{
		$($("#resource-tab li a")[0]).trigger('click');	
	}
	
	try {
		lazyload(Global.oid);/* 最新情况，所有条件都满足 */
	} catch(e) {
		var render = $("#sidebar"), Global = {oid : location.pathname.split('/')[2]};
		if (render.length) {/* 只是没有Global这个结构 */
			lazyload(Global.oid);
		}else{ /* 最原始情况  */
			/* 1. 修正HTML结构*/
			$(".span3").html("<div class='sidebar' id='sidebar'></div>");
			/* 2. 修正CSS */
			$(".sidebar").css({
				"margin-top":"20px",
				"border-left":"1px solid #ddd",
				"min-height": "875px"}
			);
			$(".ranking").css({
				"margin-top":'',
				'border-left':'',
				"padding-left":"15px",
				"width":"200px"
			});
			/* 正常情况 */
			lazyload(Global.oid);
		}
	}
});
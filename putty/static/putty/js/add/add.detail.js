function Detail() {
	this.show = function(info, oid){
		/* 首先使用数据库中的信息进行加载，然后用豆瓣的信息进行更新，不要清除数据库中的OID标识 */
		if (oid) {
			$("#oid").val(oid);
			if (info.type == 'movie') {
				$('#samesite').val(info.samesite);
			}
		}
		
		/* 强制更新电影的所有信息 */		
		for(var k in info){
			if (k != 'samesite') {
				$('#' + k).val(info[k]);
			}
		}
		
		/* 更新bootstrap switch */
		if (info.finish) {
			$("[name='finish-checkbox']").bootstrapSwitch('destroy');
			$("[name='finish-checkbox']").attr('checked', true);
			$("[name='finish-checkbox']").bootstrapSwitch();
		}else{
			$("[name='finish-checkbox']").bootstrapSwitch('destroy');
			$("[name='finish-checkbox']").attr('checked', false);
			$("[name='finish-checkbox']").bootstrapSwitch();
		}
	};
	
	this.get = function(){
		
		var detail = {
				/* 数据库ID, 数据类型 */
				_id:$("#oid").val(), type:$("#type").val(),
				
				/* 电影标题，别名 */
				title:$("#title").val(), aka:$("#aka").val(),
				
				/* IMDB编号，豆瓣ID，豆瓣评分 */
				imdb:$("#imdb").val(), douban:$("#douban").val(), ranking:$("#ranking").val(),
				
				/* 导演、编剧、演员名字 */
				director:$("#director").val(), writer:$("#writer").val(), actor:$("#actor").val(),
				
				/* 类型、语言、地区 */
				genre:$("#genre").val(), language:$("#language").val(), area:$("#area").val(),
				
				/* 上映时间、年份 */
				showtime:$("#showtime").val(), year:$("#year").val(),
				
				/* 季、集数、单集片长 */
				season:$("#season").val(), episode:$("#episode").val(), runtime:$("#runtime").val(),
				
				/* 电影简介 */
				plot:$("#plot").val(),
				
				/* 来源 */
				samesite:$("#samesite").val(),
		};
		
		/* 数据库附加信息，用于标识是否显示到首页 */
		if ( $('input[name="ontop-checkbox"]').bootstrapSwitch('state') ){
			detail.ontop = true;
		}else{
			detail.ontop = false;
		}
		
		/* 数据库附加信息，电视剧集数是否完结 */
		if ( $('input[name="finish-checkbox"]').bootstrapSwitch('state') ){
			detail.finish = true;
		}else{
			detail.finish = false;
		}
		
		return detail;
	};
	
	this.reset = function(){
	};
	
	this.initialize = function(){
		$("[name='ontop-checkbox']").bootstrapSwitch();
		$("[name='finish-checkbox']").bootstrapSwitch();
	};
}

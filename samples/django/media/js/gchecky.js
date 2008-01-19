var Site = {
    start: function() {
        if ($('sidemenu')) {
            Site.parseSidemenu();
        }
    },

    parseSidemenu: function() {
		var items = $$('#sidemenu a');
		var fx = new Fx.Elements(items, {wait: false, duration: 200, transition: Fx.Transitions.quadOut});
		items.each(function(item, i){
			item.addEvent('mouseenter', function(e){
				var obj = {};
				obj[i] = {
					'padding-left': [item.getStyle('padding-left').toInt(), item.getStyle('padding-right').toInt()*7]
				};
				items.each(function(other, j){
					if (other != item){
						var pl = other.getStyle('padding-left').toInt();
						var pr = other.getStyle('padding-right').toInt();
						if (pl != pr * 5) obj[j] = {'padding-left': [pl, pr * 5]};
					}
				});
				fx.start(obj);
			});
		});
		
		$('sidemenu').addEvent('mouseleave', function(e){
			var obj = {};
			items.each(function(other, j){
				obj[j] = {'padding-left': [other.getStyle('padding-left').toInt(), other.getStyle('padding-right').toInt()*5]};
			});
			fx.start(obj);
		});
    }
};

window.addEvent('load', Site.start);

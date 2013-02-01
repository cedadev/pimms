/**
 * jQuery.fixer - Scrolling Table With Fixed Rows And Columns
 * 
 * Copyright (c) 2011, Anand Inumpudi Licensed under the MIT license
 * http://creativecommons.org/licenses/MIT/ Version: 1.41 Date: 2011/01/30
 */
(function($) {
	//
	// plugin definition
	//
	$.fn.fixer = function(options) {
		var opts = $.extend({}, $.fn.fixer.defaults, options);
		return $(this)
				.each(
						function() {
							// only process tables
							if ($(this).get(0).tagName != "TABLE")
								return;
							// load options
							var fixedrows = Math.round(opts.fixedrows);
							var fixedcols = Math.round(opts.fixedcols);
							var height = Math.round(opts.height);
							var width = Math.round(opts.width);
							//get scroll bar width
							var sbwidth = $.getScrollbarWidth();								
							// get the table into a local variable
							var fixertable = $(this);
							// remove table padding and margin
							fixertable.removeClass('clearfix');
							fixertable.css('margin', '0').css('padding', '0');
							// create a shell to use for the subtables
							fixershell = $(this.cloneNode(false));
							// get height and width of table and width of parent
							var tableheight = fixertable.outerHeight();
							var tablewidth = fixertable.outerWidth();
							var parentwidth = fixertable.parent().width();
							//use evenIfHidden if the table is hidden
							if (fixertable.is(":hidden")) {
								fixertable
										.evenIfHidden(function(element) {
											tableheight = element.outerHeight();
											tablewidth = element.outerWidth();
										});
								fixertable.parent().evenIfHidden(
										function(element) {
											parentwidth = element.width();
										});
							}
							// see if the user wants to deliberately set width
							var setwidth = false;
							if (width > 0)
								setwidth = true;
							else {
								// otherwise, in IE, use the parent's explicit
								// width later
								width = parentwidth;
								if ($.browser.msie)
									setwidth = true;
							}
							// get the row and column count
							var rows = $('tr', fixertable);
							var cols = $('th,td', rows[0]);
							var rowcount = rows.length;
							var colcount = cols.length;
							// if table has no content, nothing to do
							if (rowcount == 0 || colcount == 0)
								return;
							// flags to indicate if rows are to be fixed,
							// columns are to be fixed, or both
							var fixrows = false;
							var fixcols = false;
							if (fixedrows > 0 && fixedrows < rowcount)
								fixrows = true;
							else
								fixedrows = 0;
							if (fixedcols > 0 && fixedcols < colcount)
								fixcols = true;
							else
								fixedcols = 0;
							// get the heights of rows and widths of columns
							var heights = new Array();
							var outerheights = new Array();
							var widths = new Array();
							rows.each(function() {
										if ($(this).is(":hidden"))
											$(this).evenIfHidden(
															function(element) {
																heights.push(element.height());
																outerheights.push(element.outerHeight());
															});
										else {
											outerheights.push($(this).outerHeight());
											heights.push($(this).height());
										}
									});
							cols.each(function() {
										if ($(this).is(":hidden"))
											$(this).evenIfHidden(
															function(element) {
																widths.push(element.outerWidth());
															});
										else
											widths.push($(this).outerWidth());
									});
							// calculate the height of the fixed rows and width
							// of the fixed columns
							var fixedheight = 0;
							var fixedwidth = 0;
							for ( var i = 0; i < fixedrows; i++)
								fixedheight = fixedheight + outerheights[i];
							for ( var i = 0; i < fixedcols; i++)
								fixedwidth = fixedwidth + widths[i];
							// don't fix rows/cols if the fixed table
							// doesn't have
							// enough viewing area or has too much area
							if (fixedheight > height || tableheight <= height) {
								fixrows = false;
								fixedrows = 0;
								fixedheight = 0;
							}
							if (fixedwidth > width || tablewidth <= width) {
								fixcols = false;
								fixedcols = 0;
								fixedwidth = 0;
							}
							//return without doing anything if the entire table fits within the area
							if (tableheight < height && tablewidth < width)
								return;
							// remove table from DOM to speed up operations
							var placeholder = $('<table></table>');
							fixertable.replaceWith(placeholder);
							// if cols will be fixed set explicit heights
							if (fixcols)
								rows.each(function(i, e) {
									$(this).height(heights[i]);
								});
							// create the four tables
							var toplefttable;
							var toprighttable;
							var bottomlefttable;
							var bottomrighttable = fixertable;
							if (fixrows) {
								toprighttable = fixershell.clone();
								toprighttable.append(rows.slice(0, fixedrows));
							}
							if (fixcols) {
								if (fixrows) {
									toplefttable = fixershell.clone();
									for (i = 0; i < fixedrows; i++) {
										row = $(rows[i].cloneNode(false));
										row.append($('td,th', rows[i]).slice(0,
												fixedcols));
										toplefttable.append(row);
									}
								}
								bottomlefttable = fixershell.clone();
								for (i = fixedrows; i < rowcount; i++) {
									row = $(rows[i].cloneNode(false));
									row.append($('td,th', rows[i]).slice(0,
											fixedcols));
									bottomlefttable.append(row);
								}
							}
							//set column widths in fixed layout if rows are being fixed
							if (fixrows) {
									toprighttable.css('box-sizing','border-box').css("table-layout","fixed");
									bottomrighttable.css('box-sizing','border-box').css("table-layout","fixed");
									var colgroup = $("<colgroup></colgroup>");
									for (i=fixedcols;i<colcount;i++)
										colgroup.append($("<col></col>").css("width",widths[i]));
									toprighttable.prepend(colgroup);
									bottomrighttable.prepend(colgroup.clone());
									if (fixcols) {
										var colgroup = $("<colgroup></colgroup>");
										toplefttable.css('box-sizing','border-box').css("table-layout","fixed");
										bottomlefttable.css('box-sizing','border-box').css("table-layout","fixed");
										for (i=0;i<fixedcols;i++)
											colgroup.append($("<col></col>").css("width",widths[i]));
										toplefttable.prepend(colgroup);
										bottomlefttable.prepend(colgroup.clone());
										toplefttable.css("width",fixedwidth+1);
										bottomlefttable.css("width",fixedwidth+1);
										toprighttable.css("width",tablewidth-fixedwidth+1);
										bottomrighttable.css("width",tablewidth-fixedwidth+1);
										}
									else {
										toprighttable.css("width",tablewidth);
										bottomrighttable.css("width",tablewidth);
									}
							}
							// individually wrap the tables and then put them in
							// a parent wrapper div. Add a 1px spacer in the beginning to fix an IE7 standards  mode issue
							var wrapper = $("<div></div>");
							// wrap the top left table if it exists
							if (fixrows && fixcols) {
								var topleft = $("<div></div>");
								topleft.css("float", "left").css("overflow",
										"hidden").css('margin', '0').css('padding', '0');
								topleft.append(toplefttable);
								wrapper.append(topleft);
							}
							// wrap the top right table if it exists
							if (fixrows) {
								var topright = $("<div></div>");
								topright.css("overflow", "hidden").css('margin', '0').css('padding', '0');
								if ($.browser.msie)
									topright.css("float", "left");
								topright.append(toprighttable);
								wrapper.append(topright);
								wrapper.append($("<div></div>").css("clear","both").css('margin', '0').css('padding', '0'));
							}
							// wrap the bottom left table if it exists
							if (fixcols) {
								var bottomleft = $("<div></div>");
								bottomleft.css("float", "left").css("overflow","hidden").css('margin', '0').css(
										'padding', '0');
								bottomleft.append(bottomlefttable);
								wrapper.append(bottomleft);
							}
							// wrap the bottom right table; always exists
							var bottomright = $("<div></div>");
							bottomright.css("overflow", "hidden").css('margin', '0').css('padding', '0');
							if (!setwidth || tablewidth>width)
								bottomright.css("overflow-x", "scroll");
							if (tableheight>height) {
								bottomright.css("overflow-y", "scroll");
								if (!setwidth && fixrows) {
									topright.css("overflow-y", "scroll");
									if (fixedheight< (2*sbwidth)) {
										topright.prepend($("<div></div>").css("height",2*sbwidth-fixedheight));
										if (fixcols)
											topleft.prepend($("<div></div>").css("height",2*sbwidth-fixedheight));
									}
								}
							}
							if ($.browser.msie)
								bottomright.css("float", "left");
							bottomright.append(bottomrighttable);
							wrapper.append(bottomright);
							wrapper.append($("<div></div>").css("clear","both"));
							// constrain the heights of bottom tables based on
							// options
							bottomright.css("height", height - fixedheight);
							if (fixcols)
								bottomleft.css("height", height
										- fixedheight-sbwidth);
							if (setwidth) {
								// if a width is known,
								// be explicit with the widths on right wrapper divs
								// TODO: use actual table border thickness instad of +1
								bottomright.css("width", width - fixedwidth);
								if (fixrows)
										topright.css("width", width	- fixedwidth - sbwidth);
							}
							// synchronize scrolling
							if (fixrows && fixcols)
								bottomright.scroll(function() {
									topright.scrollLeft(bottomright
											.scrollLeft());
									bottomleft.scrollTop(bottomright
											.scrollTop());
								});
							else if (fixcols)
								bottomright.scroll(function() {
									bottomleft.scrollTop(bottomright
											.scrollTop());
								});
							else if (fixrows)
								bottomright.scroll(function() {
									topright.scrollLeft(bottomright
											.scrollLeft());
								});
							// finally, add the fixed tables back to the DOM
							placeholder.replaceWith(wrapper);
							// and adjust width of top level wrapper so that there is enough space
							// for left and right divs to be inline
							if (fixcols && setwidth)
								if (wrapper.is(":hidden")) {
									var bottomleftouterwidth;
									var bottomrightouterwidth;
									bottomlefttable.evenIfHidden(function(element){bottomleftouterwidth=bottomleft.outerWidth();});
									bottomrighttable.evenIfHidden(function(element){bottomrightouterwidth=bottomright.outerWidth();});
									wrapper.css('width',bottomleftouterwidth+bottomrightouterwidth);
								}
							else
								wrapper.css('width',bottomleft.outerWidth()+bottomright.outerWidth());
						});
	};

	$.fn.fixer.defaults = {
		width : 0,
		height : 500,
		fixedrows : 1,
		fixedcols : 1
	};
})(jQuery);

/**
 * jQuery.evenIfHidden - get layout information of hidden DOM elements
 * http://petr.illodavi.de/jquery-evenifhidden
 *
 * Copyright (c) 2010, Davide Petrillo
 * Licensed under the MIT license http://creativecommons.org/licenses/MIT/
 *
 * Version: 1.0
 * Date:    2010/04/22
 *
 **/ 

jQuery.fn.evenIfHidden = function( callback ) {

  return this.each( function() {
    var self = $(this);
    var styleBackups = [];
    
    var hiddenElements = self.parents().andSelf().filter(':hidden');
    
    if ( ! hiddenElements.length ) {
      callback( self );
      return true; //continue the loop
    }

    hiddenElements.each( function() {
      var style = $(this).attr('style');
      style = typeof style == 'undefined'? '': style;
      styleBackups.push( style );
	  //start of modified code
	  var display = 'block';
	  var tag = $(this)[0].tagName;
	  if (tag=='TABLE' || tag=='TBODY')
		  display = 'table';
	  else if (tag=='TR')
		  display = 'table-row';
	  else if (tag=='TH' || tag=='TD')
		  display = 'table-cell';
      $(this).attr( 'style', style + ' display: '+display+' !important;' );
	  //end of modified code
    });
    
    hiddenElements.eq(0).css( 'left', -10000 );

    callback(self);

    hiddenElements.each( function() {
      $(this).attr( 'style', styleBackups.shift() );
    });

  });
};

/*! Copyright (c) 2008 Brandon Aaron (brandon.aaron@gmail.com || http://brandonaaron.net)
 * Dual licensed under the MIT (http://www.opensource.org/licenses/mit-license.php) 
 * and GPL (http://www.opensource.org/licenses/gpl-license.php) licenses.
 */

/**
 * Gets the width of the OS scrollbar
 */
(function($) {
	var scrollbarWidth = 0;
	$.getScrollbarWidth = function() {
		if ( !scrollbarWidth ) {
			if ( $.browser.msie ) {
				var $textarea1 = $('<textarea cols="10" rows="2"></textarea>')
						.css({ position: 'absolute', top: -1000, left: -1000 }).appendTo('body'),
					$textarea2 = $('<textarea cols="10" rows="2" style="overflow: hidden;"></textarea>')
						.css({ position: 'absolute', top: -1000, left: -1000 }).appendTo('body');
				scrollbarWidth = $textarea1.width() - $textarea2.width();
				$textarea1.add($textarea2).remove();
			} else {
				var $div = $('<div />')
					.css({ width: 100, height: 100, overflow: 'auto', position: 'absolute', top: -1000, left: -1000 })
					.prependTo('body').append('<div />').find('div')
						.css({ width: '100%', height: 200 });
				scrollbarWidth = 100 - $div.width();
				$div.parent().remove();
			}
		}
		return scrollbarWidth;
	};
})(jQuery);
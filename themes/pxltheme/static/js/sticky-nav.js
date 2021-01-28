// Sticky-sidebar
// Not only does this move when the 
$(function(){

    var above = '#sticky-top';
    var sticky = '#sticky-sidebar';
    var footer = '#footer';
    var vertOffset = 120;
    var footerPadding = 00;
    
    if (!!$(sticky).offset()) { // ensure sticky element exists

	var stickyTopInit = $(above).offset().top;
	
	$(window).scroll(function(){ // scroll event

	    var windowTop = $(window).scrollTop() + vertOffset;
	    var footerTop = $(footer).offset().top-footerPadding;
	    var stickyTop = $(above).offset().top + $(above).height();

	   if (stickyTop+$(sticky).height() > footerTop - vertOffset) {
	       // Rare case when sidebar is supporting footer
	       return
	    }
	    
	    if (windowTop+$(sticky).height() >= footerTop) {
		// If the sidebar is below the footer, raise it up
		$(sticky).css({position:'relative',
			       top: footerTop-stickyTop-$(sticky).height(),
			       width: ''});
	    } else {
		if ( stickyTop < windowTop ) {
		    // If the top of the window is below the sidebar, lower it
		    // This will also return the sidebar to its position
		    $(sticky).css({ position: 'fixed', top: vertOffset, width: $(above).width() });
		} else {
		    // Return the sidebar to its correct place
		    $(sticky).css({ position: 'static', width: '' });
		}

	    }
	});
    }
});


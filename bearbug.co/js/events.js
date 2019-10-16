$(document).ready(function() {

	// On page load, grab the url and the user's
	// scroll location on the page.
	var path = window.location.pathname;
	var scrolled = $(window).scrollTop();

	// If the user is scrolled past 50px on page
	// load, instantly set the header and the
	// message to their completed positions to
	// stop elements moving unpredictably up the
	// page when you're scrolled further down and
	// you can't even see why.
	if (scrolled > 50) {
		morph.quickHideMessage();
		morph.quickBecomeHeader();

	// If the path's length isn't 1 (/), we aren't
	// on the homepage, and so we should quickly
	// set the header and message into their final
	// positions, because the fancy animation will
	// get old really quick if you're flying through
	// pages.
	} else if (path.length !== 1) {
		morph.quickHideMessage();
		morph.quickBecomeHeader();
		morph.underlineTitle();
		morph.fadeBackground();
	
	// Top of the homepage? Fancy time!
	} else {
		morph.slowBecomeHeader();
	  morph.underlineTitle();
	  morph.fadeBackground();
	}
});

// On scroll, check location and if you're
// 50px from the top, do a fancy animation
// to minimise the message panel.
$(window).scroll(function() {
	var scrolled = $(window).scrollTop();
	if (scrolled > 50) {
		morph.slowHideMessage();
	}
});
// Jack's very own animations library, sort of.
// Uses very crude JQuery based DOM modifications
// to achieve basic animations in speeds that vary
// between perceptible and imperceptible.

morph = {
	underlineTitle: function()  {
		$(".title-area__underline").width("115px");
	},

	fadeBackground: function() {
		$(".site-header").css("background", "#F9CC7B");
	},

	slowBecomeHeader: function() {
		$(".site-header").css("transition", "background 1s ease-in-out, height 1s ease-in-out 1s");
		$(".site-header").height("150px");
	},

	quickBecomeHeader: function() {
		$(".site-header").css("transition", "none");
		$(".site-header").height("150px");
	},

	slowHideMessage: function() {
		$(".message").css("transition", "opacity 1s ease-in-out, height 1s ease-in-out")
		$(".message").css("height", "200px");
	},

	quickHideMessage: function() {
		$(".message").css("transition", "none");
		$(".message").css("height", "200px");
	}
}
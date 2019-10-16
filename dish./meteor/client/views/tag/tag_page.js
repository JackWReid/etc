/* =============== *\
*      HELPER      *
\* =============== */

Template.tagPage.helpers({
	/* Really simple posts data context helper
	*  that grabs all posts that have the current
	*  tag from the route in their tagged array. */
	postsByTag: function () {
		var query = String(this);
		return Posts.find({tags: query}, {sort: {createdAt: -1}});
	}
});
Template.discoverPlain.helpers({
	/* To populate the plain discover tab with
	*  posts. Currently just returns all posts
	*  by all users but should actually tailor
	*  to the current user's preferences and
	*  location. */
	discoverPosts: function () {
		return Posts.find({}, {sort: {createdAt: -1}});
	}
});

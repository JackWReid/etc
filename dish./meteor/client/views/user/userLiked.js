Template.userLiked.helpers({
	/* Returns a list of posts that the user
	*  likes to be used with #each as a data
	*  context. */
	postsUserLikes: function() {
		var user = this.username;
		return Posts.find({likedBy: user}, {sort: {createdAt: -1}});
	},

	/* Checks if the the current broswing user
	*  already follows whatever profile is
	*  loaded up. */
	userFollowed: function() {
		var targetUser = this.username;
		var user = Meteor.user();

			for (var i in user.profile.following) {
				if (user.profile.following[i] == targetUser) {
					return true;
				}
			}
			return false;
	},

});

Template.userLiked.events({
	/* Event handler for the user follow button
	*  that calls the user follow method on the
	*  server. */
	"click .user-follow": function () {
		event.preventDefault();

		var post = {
			username: this.username
		}

		Meteor.call('userFollow', post, function(error,id) {
			if (error) {
				return console.error(error.reason);
			}
		});
	}
});
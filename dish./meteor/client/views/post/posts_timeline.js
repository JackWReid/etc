/* =============== *\
*      HELPER      *
\* =============== */


Template.postsTimeline.helpers({
	/* Returns a list of posts that where the user
	*  who posted the dishh is in the logged user's
	*  following list. This way, the logged users
	*  only sees posts by people they follow. */
	postsTimeline: function() {
		var loggedUser = Meteor.user();

		if (!loggedUser.profile.following){
			throw new Meteor.Error(401, "The logged in user doesn't follow anyone, not even themselves?!.");
			return undefined;

		} else {
			return Posts.find(
				{username: { $in: loggedUser.profile.following } },
				{sort: {createdAt: -1} }
			);
		}
	}
});

Template.postsTimelineCard.helpers({
	/* Checks if the logged in user has liked the
	*  post already */
	postLiked: function() {
		var currentUser = Meteor.user();
		var postLikes = this.likedBy;
		return postLikes.indexOf(currentUser.username) > -1;
	},

	/* Helper to count the amount of likes the post
	*  has. */
	postLikesCount: function() {
		var postLikes = this.likedBy;
		if (!postLikes){
			return 0;
		} else {
			return postLikes.length;
		}
	},

	// Returns the number of comments on the post
	postCommentsCount: function() {
		var postComments = this.comments;
		if (!postComments){
			return " " + 0;
		} else {
			return " " + postComments.length;
		}
	},

	// Returns the image of the user who posted the post
	userImage: function() {
		var user = this.username;
		var userObject = Meteor.users.findOne({username: user});
		return userObject.profile.image;
	},

	// What does this do?
	restaurantID: function () {
		var restaurantName = this.restaurant;
		var restaurantObject = Restaurants.findOne({ name: restaurantName });
		return restaurantObject._id.valueOf();
	},

	// Data of users who've liked the post
	usersLikedPost: function() {
		return Meteor.users.find({ username: { $in: this.likedBy } });
	},

});



/* =============== *\
*       EVENT      *
\* =============== */


Template.postsTimelineCard.events({
	/* Deletes this post by calling a postDelete
	*  method on the server side (which checks
	*  that the current user owns the post). */
	"click .post-delete": function () {
		event.preventDefault();

		var post = {
			_id: this._id,
			username: this.username
		}

    Meteor.call('postDelete', post, function(error, id) {
			if (error) {
				return console.error(error.reason);
			}
    });
	},
	
	/* Likes the post by adding the current user's
	*  username to the post's likedBy array */
	"click .post-like": function () {
		event.preventDefault();

		var post = {
			_id: this._id,
			username: this.username
		}

		var postLikes = this.likedBy;
		var currentUser = Meteor.user();
		var postLiked = postLikes.indexOf(currentUser.username) > -1;

		Meteor.call('postLike', post, function(error, id) {
			if (error) {
				return console.error(error.reason);
			}
		});
	},

		"dblclick .timeline-card__image": function (event) {
			event.preventDefault();

			var post = {
				_id: this._id,
				username: this.username
			}

			Meteor.call('postLike', post, function(error, id) {
				if (error) {
					return console.error(error.reason);
				}
			});

		},

});
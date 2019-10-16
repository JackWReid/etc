/* =============== *\
*      HELPER      *
\* =============== */

Template.userProfile.helpers({

	/* Returns a data context with all the user data
	*  for users who this user follows. Checks if the
	*  client has access to the user's profile first
	*  for some unknown reason. */
	userFollowing: function() {
		var loggedUser = Meteor.user();
		if (this.profile) {
			var profileUser = this.profile.following;
			var userFollowingObject = Meteor.users.find({ username: { $in: profileUser } });
			return userFollowingObject;
		} else {
			return [];
		}
	},

	/* Returns a data context with all the user data
	*  for users who follow this user. */
	userFollowedBy: function() {
		var loggedUser = Meteor.user();
		var profileUser = this.username;
		var usersFollowingProfile = Meteor.users.find({ 'profile.following': profileUser });
		return usersFollowingProfile;
	},

	/* Returns the number of posts the user has ever
	*  submitted. */
	numberOfPosts: function() {
		var user = this.username;
		var posts = Posts.find({username: user}).count();

		if (posts) {
			return posts;
		} else {
			return "0";
		}
	},

	/* Returns the number of posts the user likes, the
	*  count of posts with the user's username in the
	*  likedBy array. */
	numberOfLikedPosts: function() {
		var user = this.username;
		var posts = Posts.find({likedBy: user}).count();

		if (posts) {
			return posts;
		} else {
			return "0";
		}
	},

	/* Checks if the current user follows the profile
	*  user already to show the right follow/unfollow
	*  button (filtered through a template helper that
	*  is declared globally in main). */
	userFollowed: function() {
		var targetUser = this.username;
		var user = Meteor.user();

		if (user.profile) {
			for (var i in user.profile.following) {
				if (user.profile.following[i] == targetUser) {
					return true;
				}
			}
			return false;
		} else {
			return false;
		}
	},

	/* Makes the user following modals session variable
	*  available as a template helper. */
	modalUserFollows: function() {
		return Session.get("modalUserFollows");
	},

	/* Returns the number of users that the profile user
	*  follows as a template helper. */
	followingCount: function() {
		var followList = this.profile.following;
		return followList.length;
	},

	/* Returns the number of users that follow the profile
	*  user as a template helper. */
	followerCount: function() {
		var targetUser = this.username;
		var followers = Meteor.users.find({'profile.following': targetUser});
		return followers.count();
	},

	/* Posts data for posts that the profile user has
	*  posted themselves to be used with #each in a
	*  post grid. */
	postsByUser: function() {
		var user = this.username;
		return Posts.find({username: user}, {sort: {createdAt: -1}});
	},

	/* Posts data for posts that the profile user has
	*  liked, to be used with #each in a post grid. */
	postsUserLikes: function() {
		var user = this.username;
		return Posts.find({likedBy: user}, {sort: {createdAt: -1}});
	},

	/* Helper to feed the follower/ing panel state
	*  through to the template. */
	followersPanel: function() {
		return Session.get("profileFollowersPanel");
	},

	followingPanel: function() {
		return Session.get("profileFollowingPanel");
	}

});


/* =============== *\
*       EVENT      *
\* =============== */

Template.userProfile.events({
	/* Calls the user follow method on the server
	*  when the user follow button is clicked on
	*  the client. */
	"click .user-profile-follow": function () {

		var post = { username: this.username }

		Meteor.call('userFollow', post, function(error,id) {
			if (error) {
				return console.error(error.reason);
			}
		});
	},

	/* Sets the session variable to activate extra
	*  panels showing lists of users following the
	*  profile user and of users the profile user
	*  follows. */
	"click .user-profile-stats__followers": function () {
		var currentState = Session.get("profileFollowersPanel");
		if (currentState) {
			Session.set("profileFollowersPanel", false);
		} else {
			Session.set("profileFollowersPanel", true);
			Session.set("profileFollowingPanel", false);
		}
	},

	"click .user-profile-stats__following": function () {
		var currentState = Session.get("profileFollowingPanel");
		if (currentState) {
			Session.set("profileFollowingPanel", false);
		} else {
			Session.set("profileFollowingPanel", true);
			Session.set("profileFollowersPanel", false);
		}
	},

	/* Sets and unsets the session variable that
	*  controls the visibility of the modal. */
	"click .user-profile-follows": function () {
		Session.set("modalUserFollows", true);
	},

		"click .modal-user-follows": function () {
			Session.set("modalUserFollows", false);
		},

	/* Force the user's score to update via the
	*  method on the server. */
	"click .user-profile-info__score": function() {
		var user = this.username;

		Meteor.call('updateScore', user, function(error,id) {
			if (error) {
				return console.error(error.reason);
			}
		})
	},

});
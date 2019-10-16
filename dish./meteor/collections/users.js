/* No collection invocation because Meteor
*  Accounts sets that up automatically. */

/* As yet un-used search index initialisation
*  for the users collection, for the not yet
*  implimented user search section on discover */
/*
Meteor.users.initEasySearch(['username', 'profile.name'], {
	'limit': 40,
	'use': 'mongo-db'
});
*/

Meteor.methods({

	/* Method to add the target user to the array
	*  of followed users of the current user as
	*  passed by the client. Checks that the client
	*  is logged in, and not trying to alter their
	*  own follow state (if users don't follow
	*  themslves, they don't see their own posts).
	*  If that all passes, the method checks if
	*  the user already follows the target. If so,
	*  they unfollow, they don't, they follow.
	*  If the method results in a follow action, a
	*  notification is dispatched. */
	userFollow: function(postAttributes) {
		var user = Meteor.user();
		var targetUser = postAttributes.username;

		if (!user) {
			throw new Meteor.Error(401, "You need to login to follow.");
		}
		if (user.username == targetUser) {
			throw new Meteor.Error(401, "You can can't follow yourself.");
		}

		/* Internal function that interates through the
		*  current user's following array and checks if
		*  the target user is in there. If they do, we're
		*  looking at an 'unfollow' situation, if not, it's
		*  a follow. */
		function userFollowed(targetUser, user) {
			for (var i in user.profile.following) {
				if (user.profile.following[i] == targetUser) {
					return true;
				}
			}
			return false;
		}

		if (userFollowed(targetUser, user) == true ) {
			Meteor.users.update(
				{ _id: user._id },
				{ $pull: { 'profile.following': targetUser } },
				{ multi: true }
			);
			console.info(user.username + " unfollowed " + targetUser);

		} else if (userFollowed(targetUser, user) == false ) {
			Meteor.users.update(
				{ _id: user._id },
				{ $addToSet: { 'profile.following': targetUser } }
			);

			var notification = {
				target: targetUser,
				type: 'newFollower',
				user: user.username,
				url: String("/user/" + user.username)
			}

			Meteor.call('sendNotification', notification, function(error,id){
				if (error) {
					return console.error(error.reason);
				}
			});
			
		} else {
			throw new Meteor.Error(401, "The userFollowed check failed.");
		}

	},

	/* A method for modular notification dispatch
	*  notifications to the user. Takes an object
	*  from whatever called the method and attaches
	*  an object to the target user. Doesn't attach
	*  a notification object if the notification is
	*  coming from the same user as target. */
	sendNotification: function(notificationData) {
		var target = notificationData.target;

		var notification = {
			createdAt: new Date(),
			type: notificationData.type,
			user: notificationData.user,
			post: notificationData.post,
			url: notificationData.url,
			unread: true
		}

		if (notificationData.target !== notificationData.user) {
			Meteor.users.update(
				{ username: target },
				{ $push: { 'profile.notifications': notification } }
			);
		}

	},

	/* Marks all of the user's notifications as
	*  read by iterating through the obejct array
	*  and setting the field 'unread' to false. */
	readAllNotifications: function(notificationData) {
		var user = Meteor.user();
		if (user) {
			Meteor.users.update(
				{ username: user.username },
				{ $set: { "notifications.$.unread": false } }
			);
		}
	},

	/* Empties the notifications array on the user
	*  document, deletes altogether a user's
	*  notifications. */
	clearAllNotifications: function(notificationData) {
		var user = Meteor.user();
		if (user) {
			Meteor.users.update(
				{ username: user.username },
				{ $unset: { 'profile.notifications': "" } }
			);
		} else {
			throw new Meteor.Error(401, "You have to be logged in to clear notifications");
		}
	},

	/* Take the relavent variables and calculate the
	*  dish. score for the user in the function
	*  argument. The formula for the score is the square
	*  root of the total number of likes on all of the
	*  user's posts plus the square root of the number
	*  of followers the user has, plus the cube root
	*  of the number of users the user follows. */
	updateScore: function(user) {
		var updateUser = Meteor.users.findOne({ username: user });
		var userPosts = Posts.find({ username: user });

		/*
		var userLikesCount = 0;
		for (var i = 0; i < userPosts.length; i++){
			var userLikesCount = userLikesCount + this.likedBy.length;
		}
		*/

		var userFollowers = Meteor.users.find({'profile.following': updateUser}).count();
		var userFollowing = updateUser.profile.following.length;

		/* Lacking the user likes count, see above. */
		var userScore = Math.round( Math.pow(userFollowers, 1/2) + Math.pow(userFollowing, 1/3) );

		Meteor.users.update(
			{ username: user },
			{ $set: {
				'profile.score': userScore
			} },
			{ upsert: true }
		);
	},

	/* Updates the user's settings based on the
	*  passed settings object. Checks the presence
	*  of each field and then updates that on the
	*  object. */
	settingsUpdate: function(settings) {
		var user = Meteor.user();

		if (!user) {
			throw new Meteor.Error(401, "You need to login to follow.");
		}

		if (settings.image) {
			var image = settings.image;
		} else {
			var image = user.profile.image;
		}

		if (settings.name) {
			var name = settings.name;
		} else {
			var name = user.profile.name;
		}

		if (settings.email) {
			var email = settings.email;
		} else {
			var email = user.profile.email;
		}

		if (settings.bio) {
			var bio = settings.bio;
		} else {
			var bio = user.profile.bio;
		}

		Meteor.users.update(
			{ username: user.username },
			{ $set: {
				'profile.image': image,
				'profile.name': name,
				'profile.email': email,
				'profile.bio': bio,
			} },
			{ upsert: true }
		);
	},

	/* Run some checks and then delete the
	*  account associated with the passed
	*  user id. */
	deleteAccount: function(user) {
		if (!user) {
			throw new Meteor.Error(401, "You need to log in to delete an account.");
		} else {
			Meteor.users.remove({_id: user});
		}
	}

});
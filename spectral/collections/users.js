Meteor.methods({

	/* Checks the Twitter services information
	*  and populates the user's profile with
	*  the appropriate fields. */
	updateProfile: function(){
		var user = Meteor.user();
		var userData = user.services;

		if (!user) {
			return false;
		}

		Meteor.users.update(
			{ _id: user._id },
			{ $set: {
				'profile.image': userData.twitter.profile_image_url,
				'profile.username': userData.twitter.screenName,
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
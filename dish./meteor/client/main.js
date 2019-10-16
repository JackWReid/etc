/* =============== *\
*   CONFIGURATION   *
\* =============== */

/* For now, dish. app crudely subscribes to
*  all relevant publications on every page
*  load. This could be altered to improve
*  page performance and security. */
Meteor.subscribe('posts');
Meteor.subscribe('usersInfo');
Meteor.subscribe('restaurantsInfo');
Meteor.subscribe('uploadsInfo');

/* Congfigures the Accounts package to ask
*  for an email address on a new user sign
*  up event. */
Accounts.ui.config({
	passwordSignupFields: 'USERNAME_AND_OPTIONAL_EMAIL'
});

/* =============== *\
*      HELPERS      *
\* =============== */

/* Star Converter: Takes a rating string
*  and turns it into a string of unicode
*  stars. */
Template.registerHelper('ratingStars', function(rating) {
	if (rating === 1){
		return "<span class='on'>\u2605</span>\u2605\u2605\u2605\u2605";
	} else if (rating === 2){
		return "<span class='on'>\u2605\u2605</span>\u2605\u2605\u2605";
	} else if (rating === 3){
		return "<span class='on'>\u2605\u2605\u2605</span>\u2605\u2605";
	} else if (rating === 4){
		return "<span class='on'>\u2605\u2605\u2605\u2605</span>\u2605";
	} else if (rating === 5){
		return "<span class='on'>\u2605\u2605\u2605\u2605\u2605</span>";
	} else {
		return "<span class='on'>\u2605</span>\u2605\u2605\u2605\u2605";
	}
});

/* Heart Converter: Takes a boolean value
*  and turns it into a filled heart or an
*  empty heart. */
Template.registerHelper('likeHeart', function(value) {
	if (value == true){
		return "<i class='fa fa-heart on'></i>";
	} else if (value == false){
		return "<i class='fa fa-heart off'></i>";
	} else {
		return "<i class='fa fa-heart off'></i>";
	}
});

	/* Texty Heart Converter: Takes a boolean
	*  and turns it into a filled heart or an
	*  empty heart with like or unliked. */
	Template.registerHelper('likeHeartText', function(value) {
		if (value == true){
			return "<i class='fa fa-heart'></i> Unlike";
		} else if (value == false){
			return "<i class='fa fa-heart-o'></i> Like";
		} else {
			return "<i class='fa fa-heart'></i>";
		}
	});

/* Follow Converter: Takes a boolean value
*  and turns it into a plus user or cross
*  user. */
Template.registerHelper('followBuddy', function(value) {
	if (value == true){
		return "<i class='fa fa-user-times'></i>";
	} else {
		return "<i class='fa fa-user-plus'></i>";
	}
});

	/* Follow Converter: Takes a boolean value
	*  and turns it into a plus user or cross
	*  user. */
	Template.registerHelper('followBuddyText', function(value) {
		if (value == true){
			return "<i class='fa fa-user-times'></i> Unfollow";
		} else {
			return "<i class='fa fa-user-plus'></i> Follow";
		}
	});

/* Checks with data context to see if the
*  user is looking at their own post,
*  profile, comment etc */
Template.registerHelper('userOwns', function() {
	var user = Meteor.user();
	if (this.username || this.postedBy) {
		if (this.username == user.username || this.postedBy == user.username) {
			return true;
		} else {
			return false;
		}
	} else {
		return false;
	}
});

/* Returns the user in question's image */
Template.registerHelper('userImage', function() {
	var user = this.username;
	var userObject = Meteor.users.findOne({username: user});
	return userObject.profile.image;
});

		/* To clear out the uploaded image session
		*  variable. */
		Template.registerHelper('clearImage', function () {
			Session.set("newPostImage", false);
		});

/* Returns the number of notifications globally */
Template.registerHelper('unreadNotificationCount', function() {
	var user = Meteor.user();

	if (user){
		var unreadNotifications = user.profile.notifications;
		if (unreadNotifications) {
			return unreadNotifications.length;
		} else {
			return false;
		}
	} else {
		return false;
	}
		return false;
});

/* =============== *\
*    DATE CONVERT   *
\* =============== */

/*  14th February 2015. */
Template.registerHelper('longDate', function(date) {
	return moment(date).format('Do MMMM YYYY');
});

/*  14th February. */
Template.registerHelper('shortDate', function(date) {
	return moment(date).format('Do MMMM');
});

/*  5 mins ago. */
Template.registerHelper('timeAgo', function(date) {
	return moment(date).fromNow();
});
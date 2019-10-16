/* =============== *\
*   CONFIGURATION   *
\* =============== */

/* For now, huemanism app crudely subscribes to
*  all relevant publications on every page
*  load. This could be altered to improve
*  page performance and security. */
Meteor.subscribe('posts');
Meteor.subscribe('usersInfo');

/* Congfigures the Accounts package to ask
*  for an email address on a new user sign
*  up event. */
Accounts.ui.config({
	passwordSignupFields: 'USERNAME_AND_OPTIONAL_EMAIL'
});

/* =============== *\
*      HELPERS      *
\* =============== */

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

Template.registerHelper('testHelpers', function(message) {
	console.log(message);
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

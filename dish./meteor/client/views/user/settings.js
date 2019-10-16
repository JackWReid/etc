Template.settings.helpers({
	/* Used with a with tag to draw in the data
	*  context of the current user where it isn't
	*  pulled in via the route. */
	userData: function () {
		return Meteor.users.findOne({username: Meteor.user().username});
	},

	/* Returns the URL of the user's profile
	*  image after it's been uploaded, and
	*  makes it available as a template helper. */
	imageUrl: function () {
		return Session.get("uploadFile");
	},

	/* Returns a string for the delete button
	*  based on the confirmation state of the
	*  delete account flow. */
	accountDeleteMessage: function() {
		var confirmValue = Session.get("deleteAccountConfirm");
		if (confirmValue === undefined) {
			Session.set("deleteAccountConfirm", false);
			return "Delete Account";
		} else if (confirmValue === false) {
			return "Delete Account";
		} else if (confirmValue === true) {
			return "You sure?";
		} else {
			return "Error";
		}
	},

	/* Returns a boolean based on the state of
	*  confirmation for the delete account flow. */
	accountDeleteConfirmed: function() {
		return Session.get("deleteAccountConfirm");
	}
});

Template.settings.events({
	/* Puts together a user settings object when
	*  you submit the user settings form, and
	*  passes it to the settings method in the user
	*  collection. */
	"submit .user-settings-form": function (event) {
		event.preventDefault();
		var user = Meteor.user();
		var currentUser = Meteor.users.findOne({username: user.username});
		var currentSettings = currentUser.profile;

		var settings = {
			image: Session.get("uploadFile"),
			name: $(event.target).find('[name=settings-name]').val(),
			email: $(event.target).find('[name=settings-email]').val(),
			bio: $(event.target).find('[name=settings-bio]').val()
		}

		Meteor.call('settingsUpdate', settings, function(error,id) {
			if (error) {
				return console.error(error.reason);
			}
		});

		Router.go("homePage");
	},

	/* Image upload event handler that uses Slingshot
	*  to send the image to S3 and saves a URL in the
	*  uploadFile session variable. */
	"change #file-upload-button": function (event, template){
		event.preventDefault();

		var file = $("#file-upload-button").get(0).files[0];

		var uploader = new Slingshot.Upload("dishUpload");
		uploader.send(file, function (error, downloadUrl) {
			Session.set("uploadFile", downloadUrl);
		});
	},

	/* Handles events for delete account button. First
	*  click sets the confirm session value to true, then
	*  second click calls the delete method. */
	"click .button-delete-account": function () {
		var confirmValue = Session.get("deleteAccountConfirm");

		if (confirmValue === false) {
			Session.set("deleteAccountConfirm", true);
		}

		else if (confirmValue === true) {
			var user = Meteor.user()._id;
			Meteor.call('deleteAccount', user, function(error,id) {
				if (error) {
					return console.error(error.reason);
				}
			});
		}

		else { console.error("Unexpected session value."); }
	},

	/* Handler to step down account deletion confirmation
	*  by clicking on button. */
	"click .button-nevermind-account": function () {
		Session.set("deleteAccountConfirm", false);
	}

});
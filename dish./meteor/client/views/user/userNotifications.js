Template.userNotifications.helpers({

	/* Used with #each to return the user's notification
	*  object array from the document. */
	notifications: function () {
		user = Meteor.user();
		return user.profile.notifications;
	},
	
	/* Takes the objects from the notifications array
	*  and presents them in the template with specific
	*  icon and relavent information. */
	renderNotification: function() {
		if (this.type == "newFollower"){
			return "<i class='fa fa-user'></i><span> <span class='user'>" + this.user + "</span> followed you.</span>";
		} else if (this.type == "newLike"){
			return "<i class='fa fa-heart'></i><span> <span class='user'>" + this.user + "</span> liked your dish.</span>";
		} else if (this.type == "newComment"){
			return "<i class='fa fa-comment'></i><span> <span class='user'>" + this.user + "</span> commented on your dish.</span>";
		} else {
			return "";
		}
	},

	/* To be placed within a notification iteration to
	*  produce a read or unread class to style
	*  notifications. */
	notificationStatus: function () {
		if (this.unread == true){
			return "notification-unread";
		} else {
			return "notification-read"
		}
	}

});

Template.userNotifications.events({
	/* Marks all the notifications in the user's set
	*  as read, stopping them from showing up as
	*  badges. */
	"click .read-notifications": function() {
		var user = this;
		Meteor.call('readAllNotifications', user, function(error,id) {
			if (error) {
				return console.error(error.reason);
			}
		});
	},

	/* Clears the users notifications when the handler
	*  is called by clicking the clear notifications
	*  button. Uses clearAllNotifications method. */
	"click .clear-notifications": function () {
		var user = this;
		Meteor.call('clearAllNotifications', user, function(error,id) {
			if (error) {
				return console.error(error.reason);
			}
		});
	}
});
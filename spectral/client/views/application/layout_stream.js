Template.stream.helpers({
	/* Supplies posts collection to the client
	*  view. */
	postsStream: function(){
		var loggedUser = Meteor.user();
		return Posts.find({
			userID: loggedUser && loggedUser._id
		}, {
			sort: { posted: -1 } 
		});
	}

});
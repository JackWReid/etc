Template.postStreamCard.helpers({
	/* Grabs the user's profile colour from
	*  the record corrensponding to the user
	*  who made the current post. */
	userColour: function() {
		postUser = Meteor.users.find(
		{username: this.username});

		if (!postUser.colour){
			return "#498C34";
		} else {
			return postUser.colour;
		}

		console.log("huh");
		return "huh";
		
	},

	/* Handles the state of the user having
	*  clicked on the post message, thus
	*  starting the delete post flow. */
	deleteActivated: function() {
		deleteStatus = Session.get("postDeleteStatus");
		if (deleteStatus === false){
			return false;
		} else if (deleteStatus === true){
			return true;
		} else {
			return false;
		}
	},

});


Template.postStreamCard.events({
	/* Handle the event of clicking on the
	*  text in each post. */
	"click .post-stream__card__colour-block__inner": function(event){
		event.stopPropagation();
		deleteStatus = Session.get("postDeleteStatus");
		
		/* Run a pulse focus animation on the
		*  inner block to smooth DOM node
		*  swap out. */
		$(".post-stream__card__colour-block__inner").removeClass("animated pulse");
		$(".post-stream__card__colour-block__inner").addClass("animated pulse");

		if (deleteStatus === undefined){
			Session.set("postDeleteStatus", true);
		} else if (deleteStatus === false){
			Session.set("postDeleteStatus", true);

		/* What happens if the user clicks on
		*  the text if it's already in delete
		*  mode. */
		} else if (deleteStatus === true){
			postID = this._id;

			/* Clear the delete mode. */
			Session.set("postDeleteStatus", false);

			/* Push the method call. */
			Meteor.call("postDelete", postID, function(error, id) {
				if (error) { return console.error(error.reason); }});

		} else{
			Session.set("postDeleteStatus", false);
		}
	},

	/* Clearing out of delete mode by clicking
	*  on the rest of the colour box. */
	"click .post-stream__card__colour-block": function(event){
		deleteStatus = Session.get("postDeleteStatus");

		/* Run a pulse focus animation on the
		*  inner block to smooth DOM node
		*  swap out. */
		$(".post-stream__card__colour-block__inner").removeClass("animated pulse");
		$(".post-stream__card__colour-block__inner").addClass("animated pulse");

		if (deleteStatus === undefined){
			Session.set("postDeleteStatus", false);
		} else if (deleteStatus === false){
			// Do nothing.
		} else if (deleteStatus === true){
			Session.set("postDeleteStatus", false);
		} else {
			Session.set("postDeleteStatus", false);
		}
	},

});
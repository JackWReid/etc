Template.add.helpers({
	/* Feeds the live colour update session
	*  variable into a template helper to
	*  change the colour of the box as the
	*  colour input is changed. */
	"liveColourBox": function() {
		return Session.get("liveColourBox");
	}
});

/* Sets the session value for the colour
*  input box to brand shade by default. */
Session.setDefault("liveColourBox", "#CC6449");

Template.add.events({
	/* Updates the session variable every time a
	*  new input goes into the colour selection
	*  box. */
	"input .add-post__form__colour__box": function(event) {
		Session.set("liveColourBox", event.target.value);
	},

	/* Wrap up all the form's fields into an object
	*  and call the post add method on the collection
	*  with the data an argument. */
	"submit .add-post__form": function(event){
		event.preventDefault();

		var data = {
			colour: $(event.target).find('[name=colour]').val(),
			text: $(event.target).find('[name=text]').val()
		}

		if (!data.colour || !data.text){
			/* Add an error bar for the user's sake. */
			return console.error("One of the fields was not filled in.");
		}

		else {
			/* Clear the form fields upon method call. */
			$(event.target).find('[name=colour]').val("");
			$(event.target).find('[name=text]').val("");

			/* Set the delete value back to false. */
			Session.set("postDeleteStatus", false);

			/* Do the actual add call. */
			Meteor.call('addEntry', data, function(error, id) {
				if (error) {
					return console.error(error.reason);
				}
			});
		}

	},
});
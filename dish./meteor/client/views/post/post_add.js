/* =============== *\
*       EVENT      *
\* =============== */

Template.postAdd.helpers({
	/* Returns the URL of the image from the
	*  image upload session variable. */
	imageUrl: function () {
		if (this.uploader.progress() && this.uploader.progress() < 0.9){
			return "http://i.imgur.com/v9iKxEL.gif";
		} else {
			return Session.get("uploadFile");
		}
	},

	/* Returns the session-stored rating value
	*  that powers the button clicking rating
	*  feature. */
	ratingIndicator: function() {
		var rating = Session.get("temporaryRating");
		if (!rating){
			return 0;
		} else {
			return rating;
		}
	}
});

Template.postAdd.events({
	/* Uses Slingshot to upload the image selected,
	*  then saves the URL of the image once uploaded
	*  to the session variable uploadFile, to be
	*  displayed in preview and submitted. */
	"change #file-upload-button": function (event, template){
		event.preventDefault();

		var file = $("#file-upload-button").get(0).files[0];

		var uploader = new Slingshot.Upload("dishUpload");
		uploader.send(file, function (error, downloadUrl) {
			Session.set("uploadFile", downloadUrl);
		});
	},

	/* Controls for the rating stars, modulating the
	*  session variable up and down. */
	"click .rating-add-box__control__minus": function() {
		event.preventDefault();
		var currentRating = Session.get("temporaryRating");
		if (!currentRating) {
			Session.set("temporaryRating", 1);
		} else if (currentRating === 1) {
			Session.set("temporaryRating", 1);
		} else {
			Session.set("temporaryRating", currentRating - 1);
		}
	},
	"click .rating-add-box__control__plus": function() {
		event.preventDefault();
		var currentRating = Session.get("temporaryRating");
		if (!currentRating) {
			Session.set("temporaryRating", 5);
		} else if (currentRating === 5) {
			Session.set("temporaryRating", 5);
		} else {
			Session.set("temporaryRating", currentRating + 1);
		}
	},

	/* Constructs a post object from the contents
	*  of the form being submitted in the event.
	*  Then passes the object to the new post
	*  method. First though, uses string methods
	*  and regexing to format the strings that go
	*  into the tag array of the post object. Also,
	*  router redirects home after method call. */
	"submit .post-add-form": function (event) {
		event.preventDefault();

		var raw_title = $(event.target).find('[name=title]').val();
		var final_title = s(raw_title).humanize().titleize().value();

		/* If the tag field was filled in, split
		*  the string and format the tags, commit
		*  them to the database. If not, take the
		*  supplied title and split it word-by-word
		*  into tags. */
		var raw_tags = $(event.target).find('[name=tags]').val();
		if (!raw_tags){
			var lower_tags = final_title.toLowerCase;
			var char_tags = lower_tags.replace(/[\.-\/#!'$%\^&\*;:{}=\-_`~()\s+]/g,'');
			var split_tags = char_tags.split(' ');
			var nulled_tags = $.grep(split_tags, function(n){ return(n) });
		} else {
			var lower_tags = raw_tags.toLowerCase();
			var char_tags = lower_tags.replace(/[\.-\/#!'$%\^&\*;:{}=\-_`~()\s+]/g,'');
			var split_tags = char_tags.split(',');
			var nulled_tags = $.grep(split_tags, function(n){ return(n) });
		}

		var rating = Session.get("temporaryRating");

		var post = {
			image: Session.get("uploadFile"),
			title: final_title,
			restaurant: $(event.target).find('[name=restaurant]').val(),
			location: $(event.target).find('[name=location]').val(),
			rating: rating,
			tags: nulled_tags,
		}

		Meteor.call('postAdd', post, function(error, id) {
			if (error) {
				return console.error(error.reason);
			}
		});

		Router.go('homePage');
	},

});

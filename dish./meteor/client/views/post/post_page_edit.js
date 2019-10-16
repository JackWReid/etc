Template.postPageEdit.helpers({
	/* Returns the URL of the image from the
	*  image upload session variable. */
	imageUrl: function () {
		return Session.get("uploadFile");
	},
});

Template.postPageEdit.events({
	"submit .post-page-edit-form": function(event){
		event.preventDefault();

		var raw_tags = $(event.target).find('[name=tags]').val();
		var lower_tags = raw_tags.toLowerCase();
		var char_tags = lower_tags.replace(/[\.-\/#!'$%\^&\*;:{}=\-_`~()\s+]/g,'');
		var split_tags = char_tags.split(',');
		var nulled_tags = $.grep(split_tags, function(n){ return(n) });

		var post = {
			_id: this._id,
			username: this.username,
			image: Session.get("uploadFile"),
			title: $(event.target).find('[name=title]').val(),
			restaurant: $(event.target).find('[name=restaurant]').val(),
			location: $(event.target).find('[name=location]').val(),
			rating: parseInt($(event.target).find('[name=rating]').val()),
			tags: nulled_tags,
		}

		Meteor.call('postEdit', post, function(error, id) {
			if (error) {
				return console.error(error.reason);
			}
		});

		Router.go('homePage');
	},

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
	}
});
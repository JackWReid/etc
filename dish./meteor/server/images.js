Slingshot.createDirective("dishUpload", Slingshot.S3Storage, {

	/* Configures the Slingshot plugin to upload
	*  images to the correct S3 bucket. */
	bucket: "dish-app-images",
	region: "eu-west-1",
	acl: "public-read",

	authorize: function() {
		if (!this.userId) {
			var message = "Please login before posting files";
			throw new Meteor.Error("Login Required", message);
		}
		return true;
	},

	/* Defines the path to which images are saved
	*  on the S3 bucket. In a folder by the user's
	*  name, then the file is called by the UTC
	*  date, underscore, the name of the file as
	*  passed by the user's upload. The UTC is
	*  there to stop file overwrites, with a sure
	*  unique filename every time. */
	key: function(file) {
		var user = Meteor.users.findOne(this.userId);
		var date = new Date().getTime();
		return user.username + "/" + date + "_" + file.name.replace(/\s+/g, '');
	},

	allowedFileTypes: ["image/png", "image/jpeg", "image/gif"],
	maxSize: 10 * 1024 * 1024,

});
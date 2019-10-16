/* =============== *\
*      HELPER      *
\* =============== */

Template.postPage.helpers({

	// Returns how many likes post has
	postLikesCount: function() {
		var postLikes = this.likedBy;
		if (!postLikes){
			return 0;
		} else {
			return postLikes.length;
		}
	},

	// Returns how many comments post has
	postCommentsCount: function () {
		var postComments = this.comments;
		if (!postComments){
			return 0;
		} else {
			return postComments.length;
		}
	},

	// Sees if the current user likes the powt
	postLiked: function() {
		var postLikes = this.likedBy;
		var currentUser = Meteor.user();
		return postLikes.indexOf(currentUser.username) > -1;
	},

	// Switch for the posts liked by modal
	modalPostLikes: function() {
		var modalStatus = Session.get("modalPostLikes");
		return modalStatus;
	},

	// Data of users who've liked the post
	usersLikedPost: function() {
		return Meteor.users.find({ username: { $in: this.likedBy } });
	},

	// Returns pretty version of post category
	postCategory: function() {
		return this.category.charAt(0).toUpperCase() + this.category.substring(1);
	}

});


Template.comments.helpers({
	comments: function() {
		return this.comments;
	},

	commentsImage: function() {
		var user = this.postedBy;
		var userObject = Meteor.users.findOne({username: user});
		return userObject.profile.image;
	}
});

/* =============== *\
*       EVENT      *
\* =============== */

Template.postPage.events({
	/* Likes the post by adding the current user's
	*  username to the post's likedBy array */
	"click .post-like": function (event) {
		event.preventDefault();

		var post = {
			_id: this._id,
			username: this.username
		}

		Meteor.call('postLike', post, function(error, id) {
			if (error) {
				return console.error(error.reason);
			}
		});
	},

	"dblclick .post-item-image": function (event) {
		event.preventDefault();

		var post = {
			_id: this._id,
			username: this.username
		}

		Meteor.call('postLike', post, function(error, id) {
			if (error) {
				return console.error(error.reason);
			}
		});
	},

	"click .post-delete": function (event) {
		event.preventDefault();

		var post = {
			_id: this._id,
			username: this.username,
		}

		Meteor.call('postDelete', post, function(error, id) {
			if (error) {
				return console.error(error.reason);
			}
		});

		$('.post-item').addClass('animated bounceOut');
		$('.post-item').one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', Router.go('homePage'));

	},

	/* Shows and hides the modal showing post's
	*  likers. */
	"click .post-likes-count": function (event) {
		event.preventDefault();
		Session.set("modalPostLikes", true);
	},

		"click .modal-post-likes": function (event) {
			Session.set("modalPostLikes", false);
		},

});


Template.comments.events({

	"submit .comments-add": function (event) {
		event.preventDefault();
		var user = Meteor.user();
		var comment = {
			postId: this._id,
			postUser: this.username,
			content: $(event.target).find('[name=content]').val()
		}

		Meteor.call('postComment', comment, function(error, id) {
			if (error) {
				return console.error(error.reason);
			}
		});

		$(event.target).find('[name=content]').val("");
	},

	"click .delete-comment": function (event) {
		event.preventDefault();

		var comment = {
			postId: Template.parentData(1)._id,
			createdAt: this.createdAt,
			postedBy: this.postedBy
		}

		Meteor.call('postDeleteComment', comment, function(error, id) {
			if (error) {
				return console.error(error.reason);
			}
		})
	},
});
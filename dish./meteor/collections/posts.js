/* Initialises the posts collection in Meteor
*  so that it can be referenced as 'Posts' */
Posts = new Meteor.Collection('posts');

/* Initialises the easy search meteor plugin
*  to index this collection, making it open
*  to searching. The 'limit' param controls
*  how many results are show whenever this
*  index is searched. The fields 'tags' and
*  'title' are searchable. */
Posts.initEasySearch(['title', 'tags', 'createdAt'], {
	'limit': 40,
	'use': 'mongo-db',
	'sort': { 'createdAt': -1 }
});

/* Allows the client to insert documents
*  into this collection, should be reviewed
*  seeing as this should all be handled by
*  server methods now. */
Posts.allow({
	insert: function(userId, doc) {
    return !! userId;
	},
});

Meteor.methods({

	/* Method to add a new post to the posts
	*  collection. First checks that the client
	*  is a logged in user, then grabs the fields
	*  passed by the client calling the method.
	*  The server then appends fields including
	*  the username of the client (who is posting
	*  the post), the time that the post was
	*  created, and who likes the post to begin
	*  with (the person who posted it). */
	postAdd: function(postAttributes) {
		var user = Meteor.user();

		if (!user) {
		  throw new Meteor.Error(401, "You need to login to post new dishhes.");
		}

		var post = _.extend(_.pick(
			postAttributes,
			'image',
			'title',
			'restaurant',
			'location',
			'rating',
			'description',
			'tags',
			'comments'
			), 

			{
			username: user.username,
			createdAt: new Date(),
			likedBy: [user.username]
			}

		);

		var postId = Posts.insert(post);

		return postId;
  },

  /* Method to update the post's information
  *  if the client user is the one who created
  *  the post. */
  postEdit: function(postAttributes) {
  	var user = Meteor.user();
  	var postId = postAttributes._id;
  	var postUser = postAttributes.username;

  	if (!user) {
  		throw new Meteor.Error(401, "You need to login to edit dishes.");
  	}

  	if (user.username !== postUser) {
  		throw new Meteor.Error(401, "You can only edit your own posts.");
  	}

  	if (postAttributes.title) {
  		Posts.update(
  			{ _id: postAttributes._id },
  			{ $set: { title: postAttributes.title } }
  		);
  	}

  	if (postAttributes.image) {
  		Posts.update(
	  		{ _id: postAttributes._id },
	  		{ $set: { image: postAttributes.image } }
  		);
  	}

  	if (postAttributes.restaurant) {
  		Posts.update(
  			{ _id: postAttributes._id },
  			{ $set: { restaurant: postAttributes.restaurant } }
  		);
  	}

  	if (postAttributes.location) {
  		Posts.update(
  			{ _id: postAttributes._id },
  			{ $set: { location: postAttributes.location } }
  		);
  	}

  	if (postAttributes.rating) {
  		Posts.update(
  			{ _id: postAttributes._id },
  			{ $set: { rating: postAttributes.rating } }
  		);
  	}

  	if (postAttributes.tags) {
  		Posts.update(
  			{ _id: postAttributes._id },
  			{ $set: { tags: postAttributes.tags } }
  		);
  	}

  },

  /* Method to delete the post if the client
  *  user is the one who created the post.
  *  Checks the client is logged in and that
  *  the post ID passed is their own. Then
  *  it dumps their post from the collection.
  *  Note that the client-side event call
  *  should immediately route the client away
  *  from the post page, otherwise they'll
  *  see a blank and broken page because
  *  they've deleted the data the template
  *  draws from. */
  postDelete: function(postAttributes) {
  	var user = Meteor.user();
  	var postId = postAttributes._id;
  	var postUser = postAttributes.username;

		if (!user) {
		  throw new Meteor.Error(401, "You need to login to delete dishes.");
		}

		if (user.username !== postUser) {
			throw new Meteor.Error(401, "You can only delete your own posts.");
		}

		Posts.remove({_id: postId});

  },

  /* Method to like a post, or unlike it if
  *  it's already been liked before. In the
  *  case that you're liking another user's
  *  post, method constructs a notification
  *  object and dispatches it to the
  *  notification method. */
  postLike: function(postAttributes) {
  	var user = Meteor.user();
  	var postId = postAttributes._id;
  	var postUser = postAttributes.username;
  	var prePost = Posts.findOne({_id: postAttributes._id});

  	if (!user) {
  		throw new Meteor.Error(401, "You need to login to like dishhes.");
  	}

		/* Function takes the post and the user, runs
		*  through the post's likedBy array and sees
		*  if the user in question is in there. If
		*  they are, postPreLiked, if not, false. */
		function postPreLiked(post, user) {
			for (var i in post.likedBy) {
				if (post.likedBy[i] == user.username) {
					return true;
				}
			}
			return false;
		}

		/* Unlikes post if liked already and not own post */
		if (postPreLiked(prePost, user) == true && postUser !== user.username ) {
			Posts.update(
				{ _id: postId },
				{ $pull: { likedBy: user.username } },
				{ multi: true }
			);

		/* Does nothing because you can't unlike your own post */
		} else if (postPreLiked(prePost, user) == true && postUser == user.username) {
			return false;

		/* Likes post if you don't already like it */
		} else if (postPreLiked(prePost, user) == false) {
			Posts.update(
				{ _id: postId },
				{ $addToSet: { likedBy: user.username } },
				{ upsert: true }
			);

			/* Construct a notification object for the
			*  notification dispatcher */
			var notification = {
				target: postUser,
				type: 'newLike',
				user: user.username,
				post: postId,
				url: String("/post/" + postId)
			}

			Meteor.call('sendNotification', notification, function(error,id){
				if (error) {
					return console.error(error.reason);
				}
			});

		} else {
			throw new Meteor.Error(401, "The postPreLiked check failed.");
		}
  	
  },

  /* Method to post a comment by the user passed
  *  by the client to the post passed by the
  *  client. Throws errors if the client isn't
  *  logged in or if the comment content field
  *  passed by the client is empty. If all that
  *  works out okay, appends to the comment object
  *  to the post's comment array. Then it
  *  constructs a notification object and passes
  *  it to the notification dispatcher. */
  postComment: function(commentAttributes) {
  	var user = Meteor.user();
  	var username = user.username;
 		var postId = commentAttributes.postId;
 		var postUser = commentAttributes.postUser;
 		var content = commentAttributes.content;

		if (!user) {
		  throw new Meteor.Error(401, "You need to login to comment.");
		}

		if (!content) {
			throw new Meteor.Error(401, "You can't comment nothing.");
		}

		Posts.update(
			{ _id: postId },
			{ $push: {
				comments: {
					postedBy: user.username,
					content: content,
					createdAt: new Date()
				}
			}}
		);

		var notification = {
			target: postUser,
			type: 'newComment',
			user: user.username,
			post: postId,
			url: String("/post/" + postId)
		}

		Meteor.call('sendNotification', notification, function(error,id){
			if (error) {
				return console.error(error.reason);
			}
		});

  },

  /* Method to delete a user's own comment.
  *  Throws errors if the client isn't logged
  *  or if they're trying to delete somebody
  *  else's comment. If that all passes, method
  *  pulls the comment object from the array on
  *  the post. */
  postDeleteComment: function(commentAttributes) {
  	var user = Meteor.user();
  	var comment = commentAttributes;

  	if (!user) {
  		throw new Meteor.Error(401, "You need to be logged in to delete comments.");
  	}

  	if (comment.postedBy !== user.username) {
  		throw new Meteor.Error(401, "You can only delete your own comments.");
  	}

 		Posts.update(
			{ _id: comment.postId },
			{ $pull: {
				comments: {
					createdAt: comment.createdAt
				}
			}}
		);

  }

});

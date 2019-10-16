/* Initialises the posts collection in Meteor
*  so that it can be referenced as 'Posts' */
Posts = new Meteor.Collection('posts');

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
	addEntry: function(submission) {
		var user = Meteor.user();

		var post = _.extend(_.pick(
			submission,
      'text',
      'colour'
			), 

			{
  			userID: user._id,
  			createdAt: new Date(),
			}
		);

    if (!user) {
      throw new Meteor.Error(401, "You need to be logged in to post.");
    } else {
      Posts.insert({
        userID: user._id,
        posted: new Date(),
        colour: post.colour,
        text: post.text
      });
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
  postDelete: function(postID) {
  	var user = Meteor.user();

		if (!user) {
		  throw new Meteor.Error(401, "You need to login to delete posts.");
		}

		Posts.remove({_id: postID});

  },

});

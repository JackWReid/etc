Meteor.publish('posts', function() {
	return Posts.find();
});

/* Selectively publishes the fields from the user
*  object for privacy's sake. */
Meteor.publish("usersInfo", function () {
  return Meteor.users.find(
    {},
    {
      fields: {
        _id: 1,
        username: 1,
        colour: 1,
        services: 1,
        bio: 1,
        following: 1,
        createdAt: 1,
    }
  });
});
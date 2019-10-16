Meteor.publish('posts', function() {
	return Posts.find();
});

Meteor.publish("restaurantsInfo", function () {
  return Restaurants.find();
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
        profile: 1,
        bio: 1,
        following: 1,
        createdAt: 1,
        score: 1
    }
  });
});

/* Hooks into the Accounts user creation process
*  to ensure that every new user has the basics
*  filled in on their account. */
Accounts.onCreateUser( function(options, user) {

  console.log("New user: " + options.username);

  var profileAppend = {
    name: options.username,
    image: "/defaultuser.png",
    following: ["jackwreid", options.username],
    bio: "A new dish user",
    categories: [],
    score: 1
  };

  if (!options.profile) {
    user.profile = profileAppend;
  }
  return user;

});
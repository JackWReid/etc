/* Initialises the restuarants collection in
*  Meteor so that it can be referenced as
*  'Restaurants' */
Restaurants = new Meteor.Collection('restaurants');

/* Initialises the collection search index
*  for the disover section of the site. The
*  fields 'name', 'category', and 'bio', are
*  searchable. Results limited to 40. */
Restaurants.initEasySearch(['name', 'category', 'bio'], {
	'limit': 40,
	'use': 'mongo-db'
});
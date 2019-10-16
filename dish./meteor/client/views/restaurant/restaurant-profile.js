Template.restaurantProfile.helpers({
	/* #each style data context for posts that
	*  have this restaurant as their restaurant
	*  field. Could be tricky for things that
	*  don't fully match the text. */
	postsAtRestaurant: function () {
		var thisRestaurant = this.name;
		return Posts.find({restaurant: thisRestaurant}, {sort: {createdAt: -1}});
	},

	/* Checks whether the restaurant booking
	*  modal has been activated or not, to be
	*  used as a template helper switch. */
	modalRestaurantBook: function () {
		if (Session.get("modalRestaurantBook")) {
			return true;
		} else { return false; }
	}
});


Template.restaurantProfile.events({
	/* Event handlers to set the restaurant
	*  booking modal session variable on and
	*  off. */
	"click .restaurant-book": function () {
		if (Session.get("modalRestaurantBook")) {
			Session.set("modalRestaurantBook", false);
		} else {
			Session.set("modalRestaurantBook", true);
		}
	},

	"click .modal-restaurant-book": function () {
		Session.set("modalRestaurantBook", false);
	},
});
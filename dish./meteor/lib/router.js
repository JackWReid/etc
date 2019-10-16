/* Iron:Router configuration.
*  
*  layoutTemplate:   Goes in between the body
*                    tags and the route template.
*
*  loadingTemplate:  Shown while whatever is in
*                    waitOn is loaded to local.
*
*  notFoundTemplate: Shown if the address don't
*                    correspond to route.
*
 */
Router.configure({
	layoutTemplate: 'layout',
	loadingTemplate: 'loading',
	notFoundTemplate: 'notFound',
	/* All routes wait on the subscriptions to posts
	*  info and users info before they load the
	*  template. This should mean that all info is in
	*  place by the time the page loads */
	waitOn: function() { 
	  return [ Meteor.subscribe('posts'), Meteor.subscribe('usersInfo') ];
  }
});

Router.map( function () {

	this.route('homePage', {
		path: '/'
	});

	this.route('postAdd', {
		path: '/add'
	});

	this.route('postPage', {
		path: '/post/:_id',
		data: function() {
			return Posts.findOne(this.params._id);
		}
	});

		this.route('postPageEdit', {
			path: '/post/:_id/edit',
			data: function() {
				return Posts.findOne(this.params._id);
			},
			after: function() {
				Session.set("uploadFile", false);
			}
		});

	this.route('discover', {
		path: '/discover'
	});

		this.route('discoverPosts', {
			path: '/discover/posts'
		});

		this.route('discoverUsers', {
			path: '/discover/users'
		});

		this.route('discoverRestaurants', {
			path: '/discover/restaurants'
		});

	this.route('tagPage', {
		path: '/tag/:tag',
		data: function() {
			return this.params.tag;
		}
	});

	/* Each of the user routes includes a data context
	*  of the Mongo document containing the info of
	*  whatever user is in the URL string dynamic
	*  section. */
	this.route('userProfile', {
		path: '/user/:username',
		layoutTemplate: 'layout_profile',
		data: function () {
			return Meteor.users.findOne({username: this.params.username});
		}
	});

		this.route('userLiked', {
			path: '/user/:username/liked',
			data: function () {
				return Meteor.users.findOne({username: this.params.username});
			}
		});

		this.route('userNotifications', {
			path: '/notifications',
			data: function () {
				return Meteor.users.findOne({username: this.params.username});
			}
		});

		this.route('userFollows', {
			path: '/user/:username/follows',
			data: function () {
				return Meteor.users.findOne({username: this.params.username});
			}
		});

	this.route('restaurantProfile', {
		path: '/restaurant/:name',
		data: function() {
			return Restaurants.findOne({name: this.params.name});
		}
	});

	this.route('settings', {
		path: '/settings',
	});

	this.route('about', {
		path: '/about',
	});

	this.route('admin', {
		path: '/admin',
	});

});

/* Each time a new route and therefore template
*  loads up, scroll to the top of the screen. */
Router._filters = {
  resetScroll: function () {
    var scrollTo = window.currentScroll || 0;
    $('body').scrollTop(scrollTo);
    $('body').css("min-height", 0);
  }
};

if(Meteor.isClient) {
  Router.onAfterAction(Router._filters.resetScroll);
}
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
	//layoutTemplate: '',
	/* All routes wait on the subscriptions to posts
	*  info and users info before they load the
	*  template. This should mean that all info is in
	*  place by the time the page loads */
	/*waitOn: function() { 
	  return [ Meteor.subscribe('posts'), Meteor.subscribe('usersInfo') ];
  }*/
});

Router.map( function () {

	this.route('stream', {
		path: '/'
	});

});
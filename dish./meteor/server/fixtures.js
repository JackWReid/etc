/* =============== *\
*     ACCOUNTS      *
\* ===============

if ( Meteor.users.find().count() === 0 ) {

	Accounts.createUser({
		username: "jackwreid",
		email: "emailjackreid@gmail.com",
		password: "dilapidated",
		profile: {
			name: "Jack Reid",
			image: "http://i.imgur.com/dC6GscY.jpg",
			bio: "Baby daddy of dish., lovingly hammering it into something viable.",
			following: ["jackwreid", "lizziebump"],
			categories: []
		}
	});

	Accounts.createUser({
		username: "lizziebump",
		email: "lizziehatfield4@hotmail.co.uk",
		password: "Burger101",
		profile: {
			name: "Lizzie Hatfield",
			image: "http://i.imgur.com/zoHUZeR.png",
			bio: "Design brains behind more projects than you'll ever know.",
			following: ["lizziebump", "jackwreid", "matthacke", "lauraclarke"],
			categories: []
		}
	});

	Accounts.createUser({
		username: "matthacke",
		email: "matt.hacke@btinternet.com",
		password: "evertondouche",
		profile: {
			name: "Matt Hacke",
			image: "http://i.imgur.com/72pOAcv.jpg",
			bio: "Poor unsuspecting fool.",
			following: ["matthacke", "jackwreid", "lizziebump"],
			categories: []
		}
	});

	Accounts.createUser({
		username: "lauraclarke",
		email: "lc416@exeter.ac.uk",
		password: "billericay",
		profile: {
			name: "Laura Clarke",
			image: "http://i.imgur.com/4jQpJoh.jpg?1",
			bio: "Law-ra. Law-ra. Law-ra.",
			following: ["jackwreid", "lizziebump", "beccashepard"],
			categories: []
		}
	});

	Accounts.createUser({
		username: "beccashepard",
		email: "r.shepard@live.co.uk",
		password: "coventgarden",
		profile: {
			name: "Becca Sherpard",
			image: "http://i.imgur.com/lXE3PKi.jpg",
			bio: "Female detective at work.",
			following: ["lauraclarke", "jackwreid", "lizziebump"],
			categories: []
		}
	});

}

/* =============== *\
*   SAMPLE POSTS    *
\* ===============

if (Posts.find().count() === 0) {

	Posts.insert({
		title: "Steak Frites",
		restaurant: "Café Rouge",
		location: "Epsom",
		rating: 3,
		tags: ["beef", "steak", "fries", "grill", "grease"],
		category: "pub",
		image: "http://i.imgur.com/ZqQDZ7T.jpg",
		username: "lizziebump",
		createdAt: new Date(),
		likedBy: ["jackwreid", "matthacke"],
		comments: []
	});

	Posts.insert({
		title: "American Hot",
		restaurant: "Pizza Express",
		location: "Exeter",
		rating: 2,
		tags: ["pizza", "baked", "pepperoni", "hot", "peppers"],
		category: "italian",
		image: "http://i.imgur.com/iV38e50.jpg",
		username: "jackwreid",
		createdAt: new Date(),
		likedBy: ["lizziebump"],
		comments: []
	});

	Posts.insert({
		title: "B-Rex Burger",
		restaurant: "Byron",
		location: "Exeter",
		rating: 4,
		tags: ["burger", "diner", "mayo", "beef", "cheese", "grease", "bacon", "bbq", "onion"],
		category: "burger",
		image: "http://i.imgur.com/bI1IqXB.jpg",
		username: "jackwreid",
		createdAt: new Date(),
		likedBy: ["matthacke", "lizziebump"],
		comments: []
	});

	Posts.insert({
		title: "Chicken Fajita Salad",
		restaurant: "Las Iguanas",
		location: "Exeter",
		rating: 2,
		tags: ["salsa", "chicken", "fajita", "salas"],
		category: "health",
		image: "http://i.imgur.com/4RbrVUk.jpg",
		username: "lauraclarke",
		createdAt: new Date(),
		likedBy: ["beccashepard", "lizziebump"],
		comments: []
	});

	Posts.insert({
		title: "Side of Chips",
		restaurant: "Jamie's Italian",
		location: "Exeter",
		rating: 1,
		tags: ["fries", "chips", "side", "wedges", "salty"],
		category: "italian",
		image: "http://i.imgur.com/NmF7pvh.jpg",
		username: "beccashepard",
		createdAt: new Date(),
		likedBy: ["lauraclarke", "lizziebump"],
		comments: []
	});

	Posts.insert({
		title: "The Ronaldo",
		restaurant: "Byron",
		location: "Strand",
		rating: 3,
		tags: ["burger", "diner", "beef", "cheese", "grease", "onion", "pickles"],
		category: "burger",
		image: "http://i.imgur.com/NeTLb3j.jpg",
		username: "beccashepard",
		createdAt: new Date(),
		likedBy: ["matthacke", "lizziebump", "lauraclarke"],
		comments: []
	});

	Posts.insert({
		title: "Tomato Bruschetta",
		restaurant: "Jamie's Italian",
		location: "Exeter",
		rating: 5,
		tags: ["bruschetta", "tomato", "salad", "mayo"],
		category: "italian",
		image: "http://i.imgur.com/lrSgTjX.jpg?1",
		username: "matthacke",
		createdAt: new Date(),
		likedBy: ["lizziebump"],
		comments: []
	});

}

/* =============== *\
*    RESTAURANTS    *
\* ===============

if (!Restaurants.find({name: "Las Iguanas"})){
	Restaurants.insert({
		name: "Las Iguanas",
		category: "Bar",
		image: "http://i.imgur.com/x39rIhy.png",
		book: {
			web: "http://www.iguanas.co.uk/locations/exeter",
			phone: "01392 210753",
		},
		bio: "Flame-grilled Latin American dishes and shared plates served in a contemporary chain dining room."
	});
}

if (!Restaurants.find({name: "Jamie's Italian"})){
	Restaurants.insert({
		name: "Jamie's Italian",
		category: "Italian",
		image: "http://i.imgur.com/fRHzJII.png",
		book: {
			web: "http://www.jamieoliver.com/italian/restaurants/exeter",
			phone: "01392 348448"
		},		
		bio: "Jamie's Italian features fantastic, rustic dishes, using recipes that Jamie Oliver loves!"
	});
}

if (!Restaurants.find({name: "Pizza Express"})){
	Restaurants.insert({
		name: "Pizza Express",
		category: "Pizzeria",
		image: "http://i.imgur.com/JOgKUxf.png",
		book: {
			web: "http://www.pizzaexpress.com/visit-a-restaurant/restaurant/exeter",
			phone: "01392 495788",
		},		
		bio: "Chain pizzeria where chefs in striped t-shirts toss handmade pizzas."
	});
}

if (!Restaurants.find({name: "Café Rouge"})){
	Restaurants.insert({
		name: "Café Rouge",
		category: "French Bistro",
		image: "http://i.imgur.com/y6zvG2C.jpg",
		book: {
			web: "http://www.caferouge.co.uk/",
			phone: "01392 251042",
		},
		bio: "Chain bistro for French classics from croque-monsieurs to mussels in a retro Parisian setting."
	});
}

if (!Restaurants.find({name: "Byron"})){
	Restaurants.insert({
		name: "Byron",
		category: "Burger Joint",
		image: "http://i.imgur.com/emULCI5.jpg",
		book: {
			web: "https://www.byronhamburgers.com/",
			phone: "01392 433340",
		},
		bio: "American-inspired chain diner serving posh hamburgers with a choice of toppings, sides and salads."
	});
}

Restaurants.insert({
	name: "Bill's",
	category: "Café",
	image: "http://i.imgur.com/OHVFyxU.jpg",
	book: {
		web: "http://bills-website.co.uk/restaurants/exeter/",
		phone: "01392 259227",
	},
	bio: "Take a seat and relax over breakfast, lunch or dinner. Book your table online and enjoy Bill's warm and welcoming local atmosphere."
});

Restaurants.insert({
	name: "Samuel Jones",
	category: "Grill",
	image: "http://i.imgur.com/IfotQit.gif",
	book: {
		web: "http://www.samueljonesexeter.co.uk/",
		phone: "01392 345345",
	},
	bio: "Welcome to Samuel Jones, a classic ale & smoke house built in the old bonded warehouse on the river Exe in Exeter."
});

if (!Restaurants.find({name: "Prezzo"})){
	Restaurants.insert({
		name: "Prezzo",
		category: "Italian",
		image: "http://i.imgur.com/IWWHl2L.jpg",
		book: {
			web: "http://www.prezzorestaurants.co.uk/find-and-book/",
			phone: "01392 477739",
		},
		bio: "Casual Italian chain restaurant for stone-baked pizzas and classic pastas, plus separate kids' menu."
	});
}

*/

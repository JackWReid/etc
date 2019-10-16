/* =============== *\
*   SAMPLE POSTS    *
\* ===============

if (Posts.find().count() === 0) {
	Posts.insert({
		username: "jackwreid",
		createdAt: new Date(),
		entries: [
			{
				entryTime: new Date(),
				text: "Lorem ipsum dolor sit.",
				colour: "#AAAAAF"
			},
			{
				entryTime: new Date(),
				text: "Lorem oopsum dolor sit.",
				colour: "#AAADDD"
			}
		]
	});
}

*/
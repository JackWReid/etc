function getCurrentlyReading(callback) {
  fetch('https://buukks.firebaseio.com/users/WdJCTIIi66Mqn0N8tG7aSAfVVlx2/currentlyReading.json')
  .then(function(response) {
    return response.json();
  })
  .then(function(json) {
    callback(json);
  })
  .catch(function(error) {
    console.error(error);
  });
}

var goodreadsParagraph = document.getElementById('goodreadsParagraph');
var currentlyReadingTitle = document.getElementById('currentlyReadingTitle');
var currentlyReadingLink = document.getElementById('currentlyReadingLink');
var currentlyReadingAuthor = document.getElementById('currentlyReadingAuthor');
var currentlyReadingComments = document.getElementById('currentlyReadingComments');

getCurrentlyReading(function(response) {
  currentlyReadingTitle.innerHTML = response.title;
  currentlyReadingLink.href = response.link;
  currentlyReadingAuthor.innerHTML = response.author;
  currentlyReadingComments.innerHTML = response.comments;
});

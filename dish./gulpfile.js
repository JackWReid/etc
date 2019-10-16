var gulp = require('gulp'),
    path = require('path'),

    // DEPLOY
    sftp = require("gulp-sftp"),

    // Import files
    pkg = require('./package.json')

;

// Deploy task
gulp.task('deploy', function(){
  gulp.src(['index.html'])
    .pipe(sftp({
      host: "159.203.76.23",
      user: "root",
      remotePath: "/var/www/usedish.com/public_html/",
      key: {location: "~/.ssh/id_rsa", passphrase: "Joe09051989"}
    }));
});

// Default task
gulp.task('default', ['deploy'], function (event) {
    gulp.watch("index.html", ['deploy']);
});

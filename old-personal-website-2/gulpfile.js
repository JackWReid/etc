var gulp = require('gulp'),
    path = require('path'),
    shell = require('gulp-shell'),

    sass = require('gulp-sass'),
    autoprefixer = require('gulp-autoprefixer'),
    minify = require('gulp-minify-css'),
    concat = require('gulp-concat'),
    babel = require('gulp-babel'),
    uglify = require('gulp-uglify'),
    imagemin = require('gulp-imagemin'),
    sftp = require("gulp-sftp")
;


// SASS
gulp.task('sass', function() {
    gulp.src('_sass/style.scss')
        .pipe(sass({style: 'compressed'}))
        .pipe(autoprefixer())
        .pipe(minify())
        .pipe(gulp.dest('css/'))
});

// JS
gulp.task('js', function () {
    gulp.src(['_js/**.js'])
        .pipe(concat('build.js'))
        .pipe(babel())
        .pipe(uglify())
        .pipe(gulp.dest('js/'))
});

// Images
gulp.task('images', function () {
    gulp.src('_images/**')
        .pipe(imagemin())
        .pipe(gulp.dest('images'))
});

// Jekyll build runners
gulp.task('jekyll', shell.task ([
  "jekyll build"
]));

// Deploy only previews task
gulp.task('previews', function(){
  gulp.src(['previews/**', 'previews/**/**', 'previews/**/**/**'])
    .pipe(sftp({
      host: "159.203.76.23",
      user: "root",
      remotePath: "/var/www/jackwreid.uk/public_html/",
      key: {location: "~/.ssh/id_rsa", passphrase: "Joe09051989"}
    }));
});

// Default task
gulp.task('default', ['sass', 'js', 'images', 'jekyll'], function(cb){
  gulp.watch(['_sass/*.scss', '_sass/*/*.scss'] , ['sass', 'jekyll']);
  gulp.watch(['*.html', 'work/*.html', '_includes/*.html', '_layouts/*.html', '_posts/*'], ['jekyll']);
});

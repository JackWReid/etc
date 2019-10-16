var gulp = require("gulp");
var fs = require("fs");
var sass = require("gulp-sass");
var autoprefixer = require("gulp-autoprefixer");
var uglify = require("gulp-uglify");
var plumber = require("gulp-plumber");
var concat = require("gulp-concat");
var inject = require("gulp-inject-string");

var onError = function (err) {
  console.error(err);
};

gulp.task("styles", function() {
  return gulp.src("styles/style.scss")
  	.pipe(plumber({errorHandler: onError}))
    .pipe(sass({outputStyle: 'compressed'}))
    .pipe(autoprefixer())
    .pipe(gulp.dest("."))
});

gulp.task("scripts", function() {
	return gulp.src("js/*.js")
		.pipe(concat("app.js"))
    .pipe(uglify())
		.pipe(gulp.dest("."));
});

gulp.task("injection", function () {
  var styles = fs.readFileSync("style.css", "utf8");
  var scripts = fs.readFileSync("app.js", "utf8");

  return gulp.src("theme.html")
    .pipe(inject.after('<style data-inject="styles">', styles))
    .pipe(inject.after('<script data-inject="scripts">', scripts))
    .pipe(gulp.dest("."));
});

gulp.task("watch", function () {
  gulp.watch(["styles/*", "js/*"], ["styles", "scripts", "injection"]);
});

gulp.task("default", ["styles", "scripts", "injection"]);
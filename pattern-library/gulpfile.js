var gulp = require('gulp'),
    path = require('path'),

    // CSS
    sass = require('gulp-sass'),
    autoprefixer = require('gulp-autoprefixer'),

    // JS BUILD
    concat = require('gulp-concat'),
    babel = require('gulp-babel'),
    rename = require('gulp-rename'),
    uglify = require('gulp-uglify'),

    // DEPLOY
    sftp = require("gulp-sftp"),

    // Import files
    pkg = require('./package.json')
;


// SASS
gulp.task('sass', function() {
  gulp.src('_sass/style.scss')
    .pipe(sass({style: 'compressed'}))
    .pipe(autoprefixer())
    .pipe(gulp.dest('css/'))
});

// JS
gulp.task('js', function () {
  gulp.src(['_js/data/*',
            '_js/components/*',
            '_js/main.js'])
    .pipe(concat('app.js'))
    .pipe(babel({
        presets: ['es2015', 'react']
    }))
    //.pipe(uglify())
    .pipe(gulp.dest('js/'))
});

// Jekyll Task
gulp.task('jekyll', function (gulpCallBack){
  var spawn = require('child_process').spawn;
  var jekyll = spawn('jekyll', ['build'], {stdio: 'inherit'});

  jekyll.on('exit', function(code) {
    gulpCallBack(code === 0 ? null : 'ERROR: Jekyll process exited with code: '+code);
  });
});

// Jekyll Serve Task
gulp.task('serve', function (gulpCallBack){
  var spawn = require('child_process').spawn;
  var jekyll = spawn('jekyll', ['serve'], {stdio: 'inherit'});

  jekyll.on('exit', function(code) {
    gulpCallBack(code === 0 ? null : 'ERROR: Jekyll process exited with code: '+code);
  });
});

// Default task
gulp.task('default', ['sass', 'js', 'jekyll'], function (event) {
  gulp.watch("_sass/**", ['sass', 'jekyll']);
  gulp.watch(['*.html', '*/*.html', '*/*.md'], ['jekyll']);
  gulp.watch("js/*.js", ['js', 'jekyll']);
});

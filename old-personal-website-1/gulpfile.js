var gulp = require('gulp'),
    postcss = require('gulp-postcss'),
    gutil = require('gulp-util'),

    autoprefixer = require('autoprefixer'),
    precss = require('precss'),

    browserSync = require("browser-sync").create();

gulp.task('browser-sync', function() {
  browserSync.init({
    server: { baseDir: "./" }
  });
});

gulp.task('css', function () {
  return gulp.src('./styles/style.css')
    .pipe(postcss([autoprefixer, precss]))
    .pipe(gulp.dest('./'))
    .pipe(browserSync.stream());
});

gulp.task('serve', ['css'], function() {
  browserSync.init({
    server: "./"
  });

  gulp.watch("./styles/**/**", ['css']);
  gulp.watch("./*.html").on('change', browserSync.reload);
});

gulp.task('default', ['css', 'browser-sync'], function() {
  gulp.watch('./styles/*.css', ['css']);
});

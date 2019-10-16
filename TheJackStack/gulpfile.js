var gulp = require("gulp"),
    sass = require("gulp-sass"),
    autoprefixer = require("gulp-autoprefixer"),
    concat = require("gulp-concat"),
    babel = require("gulp-babel"),
    uglify = require("gulp-uglify"),
    imagemin = require("gulp-imagemin"),
    sftp = require("gulp-sftp"),
    pkg = require("./package.json")
;

gulp.task("styles", function() {
  gulp.src("_styles/style.scss")
    .pipe(sass({style: "compressed"}))
    .pipe(autoprefixer())
    .pipe(gulp.dest("css/"))
});

gulp.task("scripts", function () {
  gulp.src(["_scripts/**.js"])
    .pipe(concat("build.js"))
    .pipe(babel())
    .pipe(uglify())
    .pipe(gulp.dest("js/"))
});

gulp.task("images", function () {
  gulp.src("_images/**/*.{png,svg,jpg,gif}")
    .pipe(imagemin())
    .pipe(gulp.dest("images"))
});

gulp.task("jekyll", function (gulpCallBack){
  var spawn = require("child_process").spawn;
  var jekyll = spawn("jekyll", ["build"], {stdio: "inherit"});
  jekyll.on("exit", function(code) {
    gulpCallBack(code === 0 ? null : "ERROR: Jekyll process exited with code: " + code);
  });
});

gulp.task("deploy", function(){
  gulp.src(["_site/**/**",
            "!_site/node_modules/**",
            "!_site/jekyll/**",
            "!_site/gulpfile.js"])
    .pipe(sftp({
      host: "159.203.76.23",
      user: "root",
      remotePath: "/var/www/jackwreid.uk/public_html/",
      key: {location: "~/.ssh/id_rsa", passphrase: "Joe09051989"}
    }));
});

gulp.task("build", ["styles", "scripts", "images", "jekyll"]);

gulp.task("watch", ["styles", "scripts", "images", "jekyll"], function(){
  gulp.watch("_styles/**", ["styles", "jekyll"]);
  gulp.watch(["*.html", "**/*.html", "*.md", "**/*.md"], "jekyll");
  gulp.watch("_scripts/**/*.{js,jsx}", ["scripts", "jekyll"]);
  gulp.watch("_images/**.{png,svg,jpg,gif}", ["images", "jekyll"]);

});

gulp.task("default", ["build"]);

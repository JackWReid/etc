#The Jack Stack

A boilerplate project to get you going. Build websites more simply with modern web technologies ([Jekyll](http://jekyllrb.com), [Gulp](http://gulpjs.com), [React](https://facebook.github.io/react), [Sass](http://sass-lang.com)), but without faffing around with server-side building.
To get started just clone the repo:
`git clone http://github.com/jackwreid/TheJackStack`

Getting Started
Once you've cloned the repo, you'll want to `cd` into it. Next open up `package.json` and you should see this:

###Node Packages
```javascript
{
  "name": "TheJackStack",
  "description": "Build websites more simply with modern web technologies.",
  "version": "1.0.0",
  "author": "Your Name",
  "repository": "https://github.com/YourGitHub/YourRepo.git",
  "homepage": "http://yourweb.page",
  "dependencies": {
    "gulp": "^3.9.0",
    "gulp-autoprefixer": "^3.0.1",
    "gulp-babel": "^5.2.1",
    "gulp-concat": "^2.6.0",
    "gulp-imagemin": "^2.3.0",
    "gulp-sass": "^2.0.4",
    "gulp-sftp": "^0.1.5",
    "gulp-uglify": "^1.4.0",
    "gulp-watch": "^4.3.5"
  },
  "scripts": {
    "build": "gulp build",
    "deploy": "gulp deploy"
  },
  "license": "MIT"
}
```

You'll want to go through the name, description, author, and repository fields here and change them so that they're relevant to your project. Also take note of the dependencies field, look how little you need to run the whole environment and deployment!

###Jekyll Settings
```yaml
# Site settings
title: The Jack Stack
description: > # Build websites more simply with modern web technologies.
baseurl: ""
url: ""

# Build settings
markdown: kramdown
permalink: none
exclude: [node_modules]
```

In the `_config.yml` file, you'll also need to switch out the title, description, and URL fields to suit your own purposes. Whilst you're developing locally, leave the URL fields empty. When you deploy, be sure to swap them out for the URL of your deployment server. Another handy trick here is the `exclude: [node_modules]` line. I was wondering why my Jekyll build was taking forever. It turns out that Jekyll was pouring through all the `node_module` directories completely uneccesarily. I don't know why that's a default behaviour but there you go, from about 10s per build, to 1s per build.

###The Gulpfile</h3>
Next take a look at the `gulpfile.js`, where the magic really happens. The Gulp dependencies are laid out at the top, and then underneath are the tasks, each separated by a line. You probably know what a Gulpfile looks like. Anyway, we'll go task by task.

```javascript
gulp.task("styles", function() {
  gulp.src("_styles/style.scss")
    .pipe(sass({style: "compressed"}))
    .pipe(autoprefixer())
    .pipe(gulp.dest("css/"))
});
```

We assume that your stylesheets work as follows: a master stylesheet, written in Sass, imports the rest of your stylesheets. In the boilerplate repository, the imported styles are all prefixed with an underscore, but they aren't sorted into subdirectories. In the case of most websites with any size, you'll probably want to organise your Sass files into folders in some scheme. This setup totally facilitates that; just make sure that the `gulp.src` points to your master stylesheet. This task pipes those styles through a [Sass module](https://www.npmjs.com/package/gulp-sass), which also minifies your styles nicely, and then [an autoprefixer](https://www.npmjs.com/package/gulp-autoprefixer) left on the default settings, which I usually find sufficient for my purposes.

```javascript
gulp.task("scripts", function () {
  gulp.src(["_scripts/**.js"])
    .pipe(concat("build.js"))
    .pipe(babel())
    .pipe(uglify())
    .pipe(gulp.dest("js/"))
});
```

With scripts, we take each individual file in the top layer of the`_scripts` directory into what they, in the Node world, call the glob. Each file is concatenated into a single file called `build.js`. Then that file is run through [Babel](https://babeljs.io), which will allow you to write JSX in your JS, or use any ES6 features you feel like using. Then, the file is minified by an [Uglify module](https://www.npmjs.com/package/gulp-uglify), and finally spit out as `_site/js/build.js`.


```javascript
gulp.task("images", function () {
  gulp.src("_images/**/*.{png,svg,jpg,gif}")
    .pipe(imagemin())
    .pipe(gulp.dest("images"))
});
```

This task will take all images (as distinguished by the file extensions in the glob selector) from all subdirectories of the images folder and run them through [Imagemin](https://www.npmjs.com/package/gulp-imagemin), which is a great omnibus image compressor that will pretty much compress any image format you throw at it.

```javascript
gulp.task("jekyll", function (gulpCallBack){
  var spawn = require("child_process").spawn;
  var jekyll = spawn("jekyll", ["build"], {stdio: "inherit"});
  jekyll.on("exit", function(code) {
    gulpCallBack(code === 0 ? null : "ERROR: Jekyll process exited with code: " + code);
  });
});
```

This task is where the good stuff starts, in my opinion. This task will run the Jekyll build process as a part of the Gulp task. Jekyll, if you don't already know, is the build tool that generates a full static website using configuration files, markdown and markup files, and by filling in those liquid tags with content. Usually you would have to run the task separately to any Gulp process as Jekyll is built on top of Ruby and Gulp on top of node, but by spawning a child process, that is avoided, and you can do the Jekyll part of the build alongside your scripts, styles, and images. It's pretty great.

```javascript
gulp.task("deploy", function(){
  gulp.src(["_site/**/**",
            "!_site/node_modules/**",
            "!_site/jekyll/**",
            "!_site/gulpfile.js"])
    .pipe(sftp({
      host: "159.203.76.23",
      user: "root",
      remotePath: "/var/www/jackwreid.uk/public_html/",
      key: {location: "~/.ssh/id_rsa", passphrase: "*********"}
    }));
});
```

Here is where the site is automatically deployed after it's been built. The following assumptions are made about your server setup in this scenario (though note they are easily made to fit any server that allows [SFTP upload](https://www.npmjs.com/package/gulp-sftp)): you're using an Apache server that has your SSH credentials, and you're using virtualhosts for multiple domains on the same server.

```javascript
gulp.task("build", ["styles", "scripts", "images", "jekyll"]);

gulp.task("watch", ["styles", "scripts", "images", "jekyll"], function(){
  gulp.watch("_styles/**", ["styles", "jekyll"]);
  gulp.watch(["*.html", "**/*.html", "*.md", "**/*.md"], "jekyll");
  gulp.watch("_scripts/**/*.{js,jsx}", ["scripts", "jekyll"]);
  gulp.watch("_images/**.{png,svg,jpg,gif}", ["images", "jekyll"]);
});

gulp.task("default", ["build"]);
```

Here's where it's all tied together. If you just run `gulp`, then the site will build with styles, scripts, images, and finally Jekyll running. Once it's built, you might want to check it's all looking like you hoped it would by opening _site/index.html or whichever page you're checking out, in Chrome. Once you're happy, and you've made sure that all your server settings are right, `gulp deploy`.

var gulp = require('gulp');
var babel = require("gulp-babel");
var requirejsOptimize = require('gulp-requirejs-optimize');

gulp.task('default', ['scripts'], function() {
});

gulp.task('jsx', function () {
	return gulp.src('src/webinterface/app/**/*.jsx')
		.pipe(babel({
			presets: ['es2015', 'stage-0', 'react']
		}))
		.pipe(gulp.dest('src/webinterface/build'));
});

gulp.task('js', function () {
	return gulp.src('src/webinterface/app/**/*.js')
		.pipe(gulp.dest('src/webinterface/build'));
});

gulp.task('scripts', ['jsx', 'js'], function () {
	return gulp.src('src/webinterface/build/webinterface/welcome.js')
		.pipe(requirejsOptimize({
			//optimize: 'none',
			paths: {
				'react': 'empty:',
				'react-mdl': 'empty:',
				'react-router': 'empty:'
			},
			baseUrl: 'src/webinterface/build',
			name: 'webinterface/welcome'
		}))
		.pipe(gulp.dest('src/webinterface/htdocs'));
});

gulp.task('watch', ['default'], function() {
	gulp.watch('src/webinterface/app/**/*.jsx', ['default']);
});

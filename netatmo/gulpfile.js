var gulp = require('gulp');
var babel = require("gulp-babel");
var requirejsOptimize = require('gulp-requirejs-optimize');

gulp.task('default', ['scripts'], function() {
});

gulp.task("babel", function () {
	return gulp.src(['src/netatmo/app/**/*.jsx', 'src/netatmo/app/**/*.js'])
		.pipe(babel({
			presets: ['es2015', 'stage-0', 'react']
		}))
		.pipe(gulp.dest('src/netatmo/build'));
});

gulp.task('scripts', ['babel'], function () {
	return gulp.src('src/netatmo/build/netatmo/netatmo.js')
		.pipe(requirejsOptimize({
			paths: {
				'react': 'empty:',
				'react-mdl': 'empty:',
				'react-redux': 'empty:',
				'dialog-polyfill': 'empty:',
				'telldus': 'empty:',
				'websocket': 'empty:',
			},
			baseUrl: 'src/netatmo/build',
			name: 'netatmo/netatmo'
		}))
		.pipe(gulp.dest('src/netatmo/htdocs'));
});

gulp.task('watch', ['default'], function() {
	gulp.watch(['src/netatmo/app/**/*.jsx', 'src/netatmo/app/**/*.js'], ['default']);
});

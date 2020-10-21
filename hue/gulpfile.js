var gulp = require('gulp');
var babel = require("gulp-babel");
var requirejsOptimize = require('gulp-requirejs-optimize');

gulp.task("babel", function () {
	return gulp.src(['src/hue/app/**/*.jsx', 'src/hue/app/**/*.js'])
		.pipe(babel({
			presets: ['es2015', 'stage-0', 'react']
		}))
		.pipe(gulp.dest('src/hue/build'));
});

gulp.task('scripts', gulp.series('babel', function () {
	return gulp.src('src/hue/build/hue/hue.js')
		.pipe(requirejsOptimize({
			paths: {
				'react': 'empty:',
				'react-mdl': 'empty:',
				'react-redux': 'empty:',
				'dialog-polyfill': 'empty:',
				'telldus': 'empty:',
				'websocket': 'empty:',
			},
			baseUrl: 'src/hue/build',
			name: 'hue/hue'
		}))
		.pipe(gulp.dest('src/hue/htdocs'));
}));

gulp.task('default', gulp.series('scripts', function (done) {
	done();
}));

gulp.task('watch', gulp.series('default', function () {
	gulp.watch(['src/hue/app/**/*.jsx', 'src/hue/app/**/*.js'], ['default']);
}));

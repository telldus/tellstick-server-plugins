define(
	['react', 'react-mdl', 'react-router'],
	function(React, ReactMDL, ReactRouter) {
		class WelcomeApp extends React.Component {
			render() {
				return (
					<div>
						<h1>hello world!</h1>
						<p>
							This is a small example showing how a webpage can be integrated into the local interface
						</p>
					</div>
				);
			}
		};

		return WelcomeApp;
	});

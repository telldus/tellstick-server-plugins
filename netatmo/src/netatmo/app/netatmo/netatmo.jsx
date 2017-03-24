define(
	['react', 'react-mdl'],
function(React, ReactMDL) {
	class NetatmoConfiguration extends React.Component {
		constructor(props) {
			super(props);
			this.state = {activated: props.activated}
		}
		activate() {
			fetch('/netatmo/activate',{credentials: 'include'})
			.then(response => response.json())
			.then(json => window.location.href = json.url)
		}
		logout() {
			fetch('/netatmo/logout',{credentials: 'include'})
			.then(response => response.json())
			.then(json => {
				if (json.success == true) {
					this.setState({activated: false})
				}
			})
		}
		render() {
			return (
				<div>
					{!this.state.activated && <ReactMDL.Button onClick={() => this.activate()}>Activate</ReactMDL.Button>}
					{this.state.activated && <ReactMDL.Button onClick={() => this.logout()}>Log out</ReactMDL.Button>}
				</div>
			)
		}
	};
	return NetatmoConfiguration;
});

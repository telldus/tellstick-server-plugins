define(
	['react', 'react-mdl', 'websocket'],
function(React, ReactMDL, WebSocket) {
	class HueConfiguration extends React.Component {
		constructor(props) {
			super(props);
			this.state = {'state': -1}
			this.websocket = new WebSocket();
		}
		componentDidMount() {
			this.websocket.onMessage('hue', 'status', (module, action, data) => this.setState({'state': data.state}));
			// Always update the state on mounting
			fetch('/hue/state',{credentials: 'include'})
				.then(response => response.json())
				.then(json => this.setState({'state': json.state}))
		}
		componentWillUnmount() {
			// Unsubscribe messages
			this.websocket.onMessage('hue', 'status', null);
		}
		reset() {
			fetch('/hue/reset',{credentials: 'include'})
		}
		render() {
			return (
				<div>
					{(this.state.state == 0 || this.state.state == -1) && <div>
						<p>Searching for bridges, please wait...</p>
						<ReactMDL.Spinner />
					</div>}
					{this.state.state == 1 && <div>
						<img src="/hue/img/smartbridge.jpg" />
					</div>}
					{this.state.state == 2 && <div>
						<p>Connected to Philips Hue!</p>
						<p><ReactMDL.Button onClick={() => this.reset()}>Reset connection to Philips HUE</ReactMDL.Button></p>
					</div>}
				</div>
			)
		}
	};
	return HueConfiguration;
});

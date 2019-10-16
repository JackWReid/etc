var ButtonArea = React.createClass ({
  getInitialState: function(){
  	return { count: 1 };
  },

  countUp: function() {
  	console.log("Button clicked.");
  	var current = this.state.count;
  	this.setState({ count: current + 1 });
  },

  render: function() {
    return (
    	<div className="button-area">
    	<ReactButton countUpdate={ this.countUp } />
    	<span className="button-area__counter">{ this.state.count }</span>
    </div>
    );
  }
});

var ReactButton = React.createClass ({
	render: function() {
		return(
		<button onClick={ this.props.countUpdate } className="button-area__button">
			Click Me
		</button>
		);
	}
});

var mountNode = document.getElementById("reactArea");
React.render(<ButtonArea />, mountNode);

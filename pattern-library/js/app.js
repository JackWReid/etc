"use strict";

var data = new Object();

data.message = "Hello World!";

var HelloMessage = React.createClass({
  displayName: "HelloMessage",

  render: function render() {
    return React.createElement(
      "h1",
      null,
      this.props.message
    );
  }
});

ReactDOM.render(React.createElement(HelloMessage, { message: data.message }), document.getElementById('helloMessage'));
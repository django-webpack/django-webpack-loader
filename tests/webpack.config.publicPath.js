var config = require("./webpack.config.simple.js");

config.output.publicPath = "http://custom-static-host.com/"

module.exports = config;

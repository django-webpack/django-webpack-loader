var config = require("./webpack.config.simple.js");

config.plugins[1].options.publicPath = "http://custom-static-host.com/";

module.exports = config;

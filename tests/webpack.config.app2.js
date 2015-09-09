var config = require("./webpack.config.simple.js");
var BundleTracker = require('webpack-bundle-tracker');
var ExtractTextPlugin = require("extract-text-webpack-plugin");

config.entry = {
  app2: './assets/js/index'
};

config.plugins = [
    new ExtractTextPlugin("styles-app2.css"),
    new BundleTracker({filename: './webpack-stats-app2.json'})
];

module.exports = config;

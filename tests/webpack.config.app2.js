var config = require("./webpack.config.simple.js");
var BundleTracker = require('webpack-bundle-tracker');
var MiniCssPlugin = require("mini-css-extract-plugin");

config.entry = {
  app2: './assets/js/index'
};

config.plugins = [
    new MiniCssPlugin(),
    new BundleTracker({filename: './webpack-stats-app2.json'})
];

module.exports = config;

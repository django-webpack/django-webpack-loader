var config = require("./webpack.config.simple.js");
var BundleTracker = require('webpack4-bundle-tracker');
var MiniCssPlugin = require("mini-css-extract-plugin");

config.entry = {
  app2: './assets/js/index'
};

config.plugins = [
  new MiniCssPlugin(),
  new BundleTracker({
    filename: "./webpack-stats-app2.json",
    publicPath: "/static/bundles/",
  }),
];

module.exports = config;

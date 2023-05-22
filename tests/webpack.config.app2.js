var config = require("./webpack.config.simple.js");
var BundleTracker = require('webpack-bundle-tracker');
var MiniCssExtractPlugin = require('mini-css-extract-plugin');

config.entry = {
  app2: './assets/js/index'
};

config.plugins = [
  new MiniCssExtractPlugin(),
  new BundleTracker({path: __dirname, filename: 'webpack-stats-app2.json'})
];

module.exports = config;

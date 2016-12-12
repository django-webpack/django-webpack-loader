var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');
var ExtractTextPlugin = require("extract-text-webpack-plugin");


module.exports = {
  context: __dirname,
  entry: {
      exported_assets: './assets/exported_assets.js'
    },
  output: {
      path: path.resolve('./assets/bundles/'),
      filename: "[name].js"
  },

  plugins: [
    new ExtractTextPlugin("styles.css"),
    new BundleTracker({filename: "webpack-stats.json", assetsIdentifier: "exported_assets"}),
  ],

  module: {
    loaders: [
      // we pass the output from babel loader to react-hot loader
      { test: /\.jsx?$/, exclude: /node_modules/, loaders: ['babel'], },
      { test: /\.css$/, loader: ExtractTextPlugin.extract("style-loader", "css-loader") },
      { test: /\.png$/, loader: "file-loader" }
    ],
  }
}

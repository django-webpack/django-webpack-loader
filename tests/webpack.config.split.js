var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');
var SplitByPathPlugin = require('webpack-split-by-path');
var ExtractTextPlugin = require("extract-text-webpack-plugin");


module.exports = {
  context: __dirname,
  entry: './assets/js/index',
  output: {
      path: path.resolve('./assets/bundles/'),
      filename: "[name].js",
      chunkFilename: "[name].js"
  },

  plugins: [
    new ExtractTextPlugin("styles.css"),
    new BundleTracker({filename: './webpack-stats.json'}),
    new SplitByPathPlugin([
      {
        name: 'vendor',
        path: path.join(__dirname, '/node_modules/')
      }
    ])
  ],

  module: {
    loaders: [
      // we pass the output from babel loader to react-hot loader
      { test: /\.jsx?$/, exclude: /node_modules/, loaders: ['babel'], },
      { test: /\.css$/, loader: ExtractTextPlugin.extract("style-loader", "css-loader") }
    ],
  },

  resolve: {
    modulesDirectories: ['node_modules', 'bower_components'],
    extensions: ['', '.js', '.jsx']
  },
}

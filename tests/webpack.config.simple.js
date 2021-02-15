var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack4-bundle-tracker');
var MiniCssPlugin = require("mini-css-extract-plugin");

module.exports = {
  mode: 'production',
  context: __dirname,
  entry: './assets/js/index',
  output: {
    path: path.resolve('./assets/bundles/'),
    filename: "[name].js"
  },

  plugins: [
    new MiniCssPlugin({filename: '[name].css', chunkFilename: '[id].css'}),
    new BundleTracker({
      filename: "./webpack-stats.json",
      publicPath: "/static/bundles/",
    }),
  ],

  module: {
    rules: [
      // we pass the output from babel loader to react-hot loader
      {test: /\.jsx?$/, exclude: /node_modules/, use: ['babel-loader'],},
      {test: /\.css$/, use: [MiniCssPlugin.loader, "css-loader"]},
      {test: /\.png$/, type: 'asset/resource', use: 'file-loader?name=assets/[name].[ext]'},
    ],
  },

  resolve: {
    extensions: ['.css', '.js', '.jsx']
  },
}

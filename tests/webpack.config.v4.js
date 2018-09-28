var path = require("path");
var BundleTracker = require('webpack-bundle-tracker');
var MiniCssPlugin = require("mini-css-extract-plugin");


module.exports = {
  context: __dirname,
  mode: 'production',
  entry: './assets/js/index',
  output: {
      path: path.resolve('./assets/bundles/'),
      filename: "[name].js",
      chunkFilename: "[name].js"
  },

  optimization: {
    splitChunks: {
      chunks: 'all'
    }
  },

  plugins: [
    new MiniCssPlugin({filename: '[name]-[chunkhash].css',     chunkFilename: '[id]-[chunkhash].css' }),
    new BundleTracker({filename: './webpack-stats.json'}),
  ],

  module: {
    rules: [
      // we pass the output from babel loader to react-hot loader
      { test: /\.jsx?$/, exclude: /node_modules/, use: [ 'babel-loader'], },
      { test: /\.css$/, use: [MiniCssPlugin.loader, "css-loader"] }
    ],
  },

  resolve: {

    extensions: ['.css', '.js', '.jsx']
  },
}

var path = require("path");
var BundleTracker = require('webpack-bundle-tracker');


module.exports = {
  context: __dirname,
  entry: {
    'main': './assets/js/index',
    'other': './assets/js/other',
  },
  output: {
    path: path.resolve('./assets/bundles/'),
    filename: "[name]-[hash].js",
    chunkFilename: "[name]-[hash].js"
  },

  plugins: [
    new BundleTracker({filename: './webpack-stats.json'}),
  ],

  module: {
    rules: [
      // we pass the output from babel loader to react-hot loader
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        loaders: ['babel-loader'],
      },
    ],
  },

  resolve: {
    modules: ['node_modules', 'bower_components'],
    extensions: ['.js', '.jsx']
  },
}

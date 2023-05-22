var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');
var MiniCssExtractPlugin = require('mini-css-extract-plugin');


module.exports = {
  context: __dirname,
  entry: './assets/js/index',
  output: {
      path: path.resolve('./assets/django_webpack_loader_bundles/'),
      filename: "[name].js",
      chunkFilename: "[name].js"
  },

  plugins: [
    new MiniCssExtractPlugin(),
    new BundleTracker({path: __dirname, filename: 'webpack-stats.json'}),
  ],

  module: {
    rules: [
      // we pass the output from babel loader to react-hot loader
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-react']
          }
        }
      },
      { test: /\.css$/, use: [MiniCssExtractPlugin.loader, 'css-loader'] }
    ],
  },

  resolve: {
    modules: ['node_modules'],
    extensions: ['.js', '.jsx']
  },

  optimization: {
    splitChunks: {
      cacheGroups: {
        commons: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
          enforce: true
        }
      }
    }
  }
}

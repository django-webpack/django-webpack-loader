const path = require("path");
const BundleTracker = require('webpack-bundle-tracker');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
  context: __dirname,
  entry: './assets/js/index',
  output: {
    path: path.resolve(__dirname, 'assets/bundles/'),
    publicPath: 'http://localhost:3000/dist/',
    filename: "[name]-[contenthash].js",
    chunkFilename: "[name]-[contenthash].js"
  },

  plugins: [
    new BundleTracker({ path: __dirname, filename: 'webpack-stats.json' }),
    new MiniCssExtractPlugin({
      filename: '[name]-[contenthash].css',
      chunkFilename: '[name]-[contenthash].css',
    }),
  ],

  module: {
    rules: [
      // we pass the output from babel loader to react-hot loader
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
        },
      },
      {
        test: /\.css$/,
        use: [MiniCssExtractPlugin.loader, 'css-loader'],
      }
    ],
  },

  resolve: {
    extensions: ['.js', '.jsx'],
  },
};
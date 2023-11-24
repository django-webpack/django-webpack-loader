var path = require("path");
var BundleTracker = require('webpack-bundle-tracker');
var MiniCssExtractPlugin = require('mini-css-extract-plugin');

// https://github.com/cockpit-project/starter-kit/commit/3220617fec508aabbbc226a87a165c21fb72e913
// webpack 4 requires monkey-patch in node v18
const crypto = require("crypto");
const crypto_orig_createHash = crypto.createHash;
crypto.createHash = algorithm => crypto_orig_createHash(algorithm == "md4" ? "sha256" : algorithm);

module.exports = {
  mode: "production",
  context: __dirname,
  entry: './assets/js/index',
  output: {
      path: path.resolve('./assets/django_webpack_loader_bundles/'),
      filename: "[name].js"
  },

  plugins: [
    new MiniCssExtractPlugin(),
    new BundleTracker({path: __dirname, filename: 'webpack-stats.json', integrity: true}),
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
      { test: /\.css$/, use: [MiniCssExtractPlugin.loader, 'css-loader'], }
    ],
  },

  resolve: {
    modules: ['node_modules'],
    extensions: ['.js', '.jsx']
  },
}

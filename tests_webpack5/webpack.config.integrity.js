var path = require("path");
var BundleTracker = require('webpack-bundle-tracker');

module.exports = {
  entry: {
    resources: './assets/js/resources'
  },

  output: {
    assetModuleFilename: 'assets/[name]-[contenthash][ext]',
    path: path.resolve('./assets/django_webpack_loader_bundles/'),
    publicPath: 'http://custom-static-host.com/',
  },

  module: {
    rules: [{ test: /\.txt$/, type: 'asset/resource' }]
  },

  plugins: [
    new BundleTracker({path: __dirname, integrity: true})
  ],

  resolve: {
    extensions: ['.js', '.jsx']
  },
}


var config = require('./webpack.config.publicPath.js');
var BundleTracker = require('webpack-bundle-tracker');
var ExtractTextPlugin = require('extract-text-webpack-plugin');

config.output.filename = 'name.js?[hash]';
config.output.plugins = [
    new ExtractTextPlugin('styles.css?123'),
    new BundleTracker({filename: './webpack-stats.json'})
];

module.exports = config;

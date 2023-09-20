const webpack = require('webpack');
const { merge } = require('webpack-merge');
const WebpackDevServer = require('webpack-dev-server');
const config = require('./webpack.config.js');

const devServerOptions = {
  devMiddleware: {
    publicPath: config.output.publicPath,
  },
  host: 'localhost',
  port: 3000,
  hot: true,
  historyApiFallback: true,
  headers: { 'Access-Control-Allow-Origin': '*' },
};

const mergedConfig = merge(config, {
  mode: 'development',
  devtool: 'eval-source-map', // Optional: Choose an appropriate devtool for your needs
});

const compiler = webpack(mergedConfig);
const server = new WebpackDevServer(devServerOptions, compiler);

server.start();
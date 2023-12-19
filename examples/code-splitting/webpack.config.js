var path = require("path");
var BundleTracker = require("webpack-bundle-tracker");

module.exports = {
  context: __dirname,
  entry: {
    main: "./assets/js/index",
    other: "./assets/js/other",
  },
  output: {
    path: path.resolve(__dirname, "assets/webpack_bundles/"),
    publicPath: "auto",
    filename: "[name]-[contenthash].js",
  },

  plugins: [
    new BundleTracker({ path: __dirname, filename: "webpack-stats.json" }),
  ],

  module: {
    rules: [
      // we pass the output from babel loader to react-hot loader
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
        },
      },
    ],
  },

  resolve: {
    extensions: [".js", ".jsx"],
  },
};

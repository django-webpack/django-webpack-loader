## Split By Path Webpack Plugin

This plugin will split a Webpack entry bundle into any number of arbitrarily defined smaller bundles.

Based on [Split by Name Webpack Plugin](https://github.com/soundcloud/split-by-name-webpack-plugin).

**Unlike original component, it uses absolute path to identify bundle.**

### Why?

- Browsers will open [between 6 and 10][browserscope] parallel connections to a single host. By splitting up one large
file (your main bundle) into a number of smaller ones, you can leverage these connections to download the files
[faster][stevesouders].
- It's likely that you will have some third party scripts which you change infrequently. By putting these into their own
bundle, then if they haven't changed between builds, your users may still be able to use the cached version from before.

### How?

Configuration of the plugin is simple. You instantiate the plugin with an array of objects, each containing the keys `name` and `path`. Any modules which are in your entry chunk which match the bucket's path (first matching bucket is used), are then moved to a new chunk with the given name.

`path` should be an absolute path string value. It can be also an array of such values.

Creating a 'catch-all' bucket is not necessary: anything which doesn't match one of the defined buckets will be left in
the original chunk.

### Example

```js
var SplitByPathPlugin = require('webpack-split-by-path');
module.exports = {
  entry: {
    app: 'app.js'
  },
  output: {
    path: __dirname + '/public',
    filename: "[name]-[chunkhash].js",
    chunkFilename: "[name]-[chunkhash].js"
  },
  plugins: [
    new SplitByPathPlugin([
      {
        name: 'vendor',
        path: path.join(__dirname, 'node_modules/')
      }
    ])
  ]
};
```

So every module that is being requested from `node_modules` will be placed in `public/vendor.js` and everything else will be placed in `public/app.js`.

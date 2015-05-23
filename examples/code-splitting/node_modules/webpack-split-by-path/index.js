// Based on Split by Name Webpack Plugin – https://github.com/soundcloud/split-by-name-webpack-plugin

function SplitByPathPlugin (buckets) {
  this.buckets = buckets.slice(0).map(function (bucket) {
    if (!Array.isArray(bucket.path)) {
      bucket.path = [ bucket.path ];
    }

    bucket.path = bucket.path.map(function (path) {
      return new RegExp('^' + path);
    });

    return bucket;
  });
}

SplitByPathPlugin.prototype.apply = function(compiler) {
  var buckets = this.buckets;

  function findMatchingBucket(chunk) {
    var match = null;

    buckets.some(function (bucket) {
      return bucket.path.some(function (path) {
        if (path.test(chunk.userRequest)) {
          match = bucket;
          return true;
        }
      });
    });

    return match;
  }

  compiler.plugin('compilation', function (compilation) {
    var extraChunks = {};

    // Find the chunk which was already created by this bucket.
    // This is also the grossest function name I've written today.
    function bucketToChunk(bucket) {
      return extraChunks[bucket.name];
    }

    compilation.plugin('optimize-chunks', function (chunks) {
      var addChunk = this.addChunk.bind(this);
      chunks
        // only parse the entry chunk
        .filter(function (chunk) {
          return chunk.entry;
        })
        .forEach(function (chunk) {
          chunk.modules.slice().forEach(function (mod) {
            var bucket = findMatchingBucket(mod),
                newChunk;
            if (!bucket) {
              // it stays in the original bucket
              return;
            }
            if (!(newChunk = bucketToChunk(bucket))) {
              newChunk = extraChunks[bucket.name] = addChunk(bucket.name);
            }
            // add the module to the new chunk
            newChunk.addModule(mod);
            mod.addChunk(newChunk);
            // remove it from the existing chunk
            mod.removeChunk(chunk);
          });

          buckets
            .map(bucketToChunk)
            .filter(Boolean)
            .concat(chunk)
            .forEach(function (bucket, index, allChunks) { // allChunks = [bucket0, bucket1, .. bucketN, orig]
              if (index) { // not the first one, they get the first chunk as a parent
                bucket.parents = [allChunks[0]];
              } else { // the first chunk, it gets the others as 'sub' chunks
                bucket.chunks = allChunks.slice(1);
              }

              bucket.initial = bucket.entry = !index;
            });
        });
    });
  });
};

module.exports = SplitByPathPlugin;

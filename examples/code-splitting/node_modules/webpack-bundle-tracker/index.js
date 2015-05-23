var path = require('path');
var fs = require('fs');
var stripAnsi = require('strip-ansi');

var assets = {};
var DEFAULT_OUTPUT_FILENAME = 'webpack-stats.json';


function Plugin(options) {
  this.options = options || {};
}

Plugin.prototype.apply = function(compiler) {
    var self = this;

    compiler.plugin('compilation', function(compilation, callback) {
      compilation.plugin('failed-module', function(fail){
        var output = {
          status: 'error',
          error: fail.error.name
        };
        if (fail.error.module !== undefined) {
          output.file = fail.error.module.userRequest;
        }
        if (fail.error.error !== undefined) {
          output.message = stripAnsi(fail.error.error.codeFrame);
        }
        self.writeOutput(compiler, output);
      });
    });

    compiler.plugin('compile', function(compiler, callback) {
      self.writeOutput(compiler, {status: 'compiling'});
    });

    compiler.plugin('done', function(stats){
      if (stats.compilation.errors.length > 0) {
        var error = stats.compilation.errors[0];
        self.writeOutput(compiler, {
          status: 'error',
          error: error['name'],
          message: error['message']
        });
        return;
      }

      var chunks = {};
      stats.compilation.chunks.map(function(chunk){
        var files = chunk.files.map(function(file){
          var F = {name: file};
          if (compiler.options.output.publicPath) {
            F.publicPath= compiler.options.output.publicPath + file;
          }
          if (compiler.options.output.path) {
            F.path = path.join(compiler.options.output.path, file);
          }
          return F;
        });
        chunks[chunk.name] = files;
      });
      self.writeOutput(compiler, {status: 'done', chunks: chunks});


    });
};


Plugin.prototype.writeOutput = function(compiler, contents) {
  var outputDir = this.options.path || '.';
  var outputFilename = path.join(outputDir, this.options.filename || DEFAULT_OUTPUT_FILENAME);
  fs.writeFileSync(outputFilename, JSON.stringify(contents));
};

module.exports = Plugin;

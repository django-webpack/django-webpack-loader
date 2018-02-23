# django-webpack-loader changelog

For more general information, view the [readme](README.md).

Releases are added to the
[github release page](https://github.com/ezhome/django-webpack-loader/releases).

## [0.6.0] -- 2018-02-22

- Added support for 'Access-Control-Allow-Origin' header
- Read stats file with unicode support
- Cleaned up exceptions
- Updated and corrected docs

## [0.5.0] -- 2017-05-20

- Added ability to access the webpack asset path information from application
- Fixed potential crash when formatting errors
- Added django 1.11 to test suite

## [0.4.0] -- 2016-10-26

- Added ability to compile webpack to gzip bundles
- Added poll interval option (time to wait between polling the stats file)
- Added timeout (maximum wait-time before throwing an Exception)
- Added django 1.10 to test suite

## [0.3.3] -- 2016-07-24

- Added Makefile for easier development
- Added ability timeout when waiting for webpack to compile a bundle

## [0.3.2] -- 2016-07-24

- Added ability to add attrs to render_bundle tag

## [0.3.1] -- 2016-07-24

- documented webpack_static tag

## [0.3.0] -- 2015-02-21

- breaking 💥: new CACHE setting which when set to true makes the loader cache the contents of the stats files in memory. If set to True, server will restart every time the stats file contents change or it'll keep serving old, cached URLs. CACHE defaults to not DEBUG by default.
- Fixed Exception
- Added django 1.9 to test suite

## [0.2.4] -- 2015-12-23

- Fix unicode errors

## [0.2.3] -- 2015-12-03

- mark safe template tags

## [0.2.2] -- 2015-09-21

- fix webpack exceptions

## [0.2.1] -- 2015-12-03

- add custom exception for WebpackLoaderBadStatsError

## [0.2.0] -- 2015-09-10

- breaking 💥: revised django settings configuration syntax
- webpack loader can now consume the output of multiple stats files in the same project
- add ``get_files`` template tag

## [0.1.2] -- 2015-05-25

- first documented release

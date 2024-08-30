# django-webpack-loader changelog

For more general information, view the [readme](README.md).

Releases are added to the
[github release page](https://github.com/ezhome/django-webpack-loader/releases).

## [3.1.1] -- 2024-08-30

- Add support for Django 5.1

## [3.1.0] -- 2024-04-04

Support `webpack_asset` template tag to render transformed assets URL: `{% webpack_asset 'path/to/original/file' %} == "/static/assets/resource-3c9e4020d3e3c7a09c68.txt"`

## [3.0.1] -- 2024-01-16

Added `skip_common_chunks` option to the `get_files()` template tag.

## [3.0.0] -- 2023-12-19

- Fix support for `publicPath: auto` in Webpack config, check updated examples at https://github.com/django-webpack/django-webpack-loader/tree/master/examples
- Add support for Python 3.12
- Add support for Django 5.0

## [2.0.1] -- 2023-06-14
- Add support for Django 4.2

## [2.0.0] -- 2023-05-22
- Update examples to use `webpack-bundle-tracker@2.0.0` API and keep version parity with it
- Update Django to 3.2.19
- Add mocked `get_assets` method to `FakeWebpackLoader` for usage in tests

## [1.8.1] -- 2023-02-06
- Add a `FakeWebpackLoader` for running tests

## [1.8.0] -- 2022-12-09
- Add compatibility for Django 4.1 and Python 3.10

## [1.7.0] -- 2022-11-14
- Bump django to 3.2.15

## [1.6.0] -- 2022-06-20
- Add a setting to configure skip common chunks behaviour globally
- Bump django from 3.2.12 to 3.2.13
- Add support for Django 4.0

## [1.5.0] -- 2022-03-25
- Added support for Subresource Integrity 
- Bump django from 3.2.7 to 3.2.12
- Fix get_files on readme 
- Use r-prefixed strings in IGNORE
- Fix small typo in README.md 
- Use assertNotEqual instead of assertNotEquals for Python 3.11 compatibility
- Readme revamp

## [1.4.1] -- 2021-10-04

- Fixes #300, failsafe request checking #301

## [1.4.0] -- 2021-09-24

- Bump django from 3.2.4 to 3.2.5 #299
- Add issue templates #293
- Add skip_common_chunks functionality #297

## [1.3.0] -- 2021-08-30

- Add option for rel="preload" in JS/CSS tags #203
- Add option for extension appending in the url files #135
- Fixes RemovedInDjango41Warning #290
- Applies IGNORE setting before checking assets #286
- Removed type from link and script tags per #152

NOTE: Skipped version 1.2.0 to match `webpack-bundle-tracker` version


## [1.1.0] -- 2021-06-18

- Added compatibility with `webpack-bundle-tracker@1.1.0`
- Removes bower references in project
- Fix jinja configuration example in README.md

## [1.0.0] -- 2021-05-12

- Added support for custom loader classes
- Added compatibility with `webpack-bundle-tracker@1.0.0-alpha.1`
- Updated and corrected examples
- Updated Python and Django supported versions on tests
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

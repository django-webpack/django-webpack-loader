# requires-port

The module name says it all, check if a protocol requires a given port.

## Installation

This module is intended to be used with browserify or Node.js and is distributed
in the public npm registry. To install it simply run the following command from
your CLI:

```j
npm install --save requires-port
```

## Usage

The module exports it self as function and requires 2 arguments:

1. The port number, can be a string or number.
2. Protocol, can be `http`, `http:` or even `https://yomoma.com`. We just split
   it at `:` and use the first result. We currently accept the following
   protocols:
   - `http`
   - `https`
   - `ws`
   - `wss`
   - `ftp`
   - `gopher`
   - `file`

It returns a boolean that indicates if protocol requires this port to be added
to your URL.

```js
'use strict';

var required = require('requires-port');

console.log(required('8080', 'http')) // true
console.log(required('80', 'http'))   // false
```

# License

MIT

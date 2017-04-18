Use this plugin to add support for making http requests through lua scripts

This is basically a wrapper around python-requests. It's documentation can be found here:  
<http://www.python-requests.org/en/master/>

```lua
local http = require("http.Request")
http:get{
	url='http://example.com'
}
```

Due to technical reasons all calls are async. To retrieve the response from a http call a callback must be supplied.

More examples can be found here:  
<https://github.com/telldus/tellstick-lua-examples/tree/master/plugins/http>

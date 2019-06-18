/* eslint-disable */
'use strict';
var  validation = require('./pattern-validation');

module.exports = (() => {

  function validate(expression, config) {
    try {
      validation(expression, config);
    } catch(e) {

      return {status: false, msg: e.toString()};

    }

    return {status: true, msg: ''};
  }

  return {
    validate: validate
  };
})();

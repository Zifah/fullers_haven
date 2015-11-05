(function () {
    'use strict';

    var app = angular
        .module('fullers_haven', [
            'fullers_haven.config',
            'fullers_haven.orders',
            'mgo-angular-wizard',
            'pickadate'
        ]);

    app.directive('integer', integer);
    
    function integer() {
        return {
            require: 'ngModel',
            link: function (scope, ele, attr, ctrl) {
                ctrl.$parsers.unshift(function (viewValue) {
                    return parseInt(viewValue, 10);
                });
            }
        };
    }
})();
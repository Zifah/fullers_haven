(function () {
    'use strict';

    //angular
    //    .module('fullers_haven.orders.controllers', []);

    //angular
    //    .module('fullers_haven.orders.services', []);

    angular
        .module('fullers_haven.orders', [
            'fullers_haven.orders.services',
            'fullers_haven.orders.controllers'            
        ]);
})();
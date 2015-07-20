(function () {
    'use strict';

    angular
        .module('fullers_haven.orders.controllers', [])
        .controller('OrderController', OrderController);

    function OrderController($scope, $http) {
        $scope.order = {
            types: [
                {
                    name: 'Normal',
                    value: 'N'
                },
                {
                    name: 'Bulk',
                    value: 'B'
                }
            ]
        };

        $scope.customers = [
            {
                id: 1,
                name: 'Adewuyi Hafiz',
                email: 'hoadewuyi@gmail.com'
            },
            {
                id: 2,
                name: 'Adeolu Adewuyi',
                email: 'adeoluadewuyi@gmail.com'
            },
            {
                id: 3,
                name: 'Wale Olajumoke',
                email: 'wale.olajumoke@gmail.com'
            }
        ];

        $scope.text = "ADEMOLA";
    }
})();
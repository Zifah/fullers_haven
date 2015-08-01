(function () {
    'use strict';

    angular
        .module('fullers_haven.orders.services', [])
        .factory('Orders', Orders);

    function Orders($http) {
        var Orders = {
            getCustomers: getCustomers,
            getProducts: getProducts,
            getProductsById: getProductsById
        };

        function getCustomers() {
            return $http.get('/api/v1/customers/');
        }

        function getProducts(customerUsername, orderType) {
            var url = '/api/v1/products/?customer=' + customerUsername + '&order_type='+orderType;
            return $http.get(url);
            //var products = {
            //    maxPieces: null, //only for bulk
            //    products: [
            //        {
            //            id: '1',
            //            name: 'Teabag',
            //            items: 'Rope, leaves and paper bag',
            //            numberOfItems: 2,
            //            price: 500.03,
            //            maxAllowed: null //only for bulk
            //        }
            //    ]
            //};

            //return products;
        }

        function getProductsById(productIds) {
            var url = '/api/v1/products/?ids='+JSON.stringify(productIds);
            return $http.get(url);
        }

        return Orders;
    }
})();
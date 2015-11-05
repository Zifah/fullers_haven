(function () {
    'use strict';

    angular
        .module('fullers_haven.orders.services', [])
        .factory('Orders', Orders);

    function Orders($http) {
        var Orders = {
            getCustomers: getCustomers,
            getProducts: getProducts,
            getProductsById: getProductsById,
            getColours: getColours,
            getAlterations: getAlterations,
            saveOrder: saveOrder,
            getOrderById: getOrderById,
            updateOrder: updateOrder
        };

        function getCustomers() {
            return $http.get('/api/v1/customers/');
        }

        function getColours() {
            return $http.get('/api/v1/colours/');
        }

        function getAlterations() {
            return $http.get('/api/v1/alterations/');
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
            var url = '/api/v1/products/?ids='+encodeURIComponent(JSON.stringify(productIds));
            return $http.get(url);
        }

        function saveOrder(theOrder) {
            return $http.post('/api/v1/orders/', theOrder);
        }

        function getOrderById(orderId) {
            return $http.get('/api/v1/orders/'+orderId+'/');
        }

        function updateOrder(orderId, theOrder) {
            return $http.put('/api/v1/orders/'+orderId+'/', theOrder);
        }

        return Orders;
    }
})();
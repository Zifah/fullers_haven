(function () {
    'use strict';

    angular
        .module('fullers_haven.orders.controllers', [])
        .controller('OrderController', OrderController);

    function OrderController($scope, $http, Orders, WizardHandler) {
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
            ],
            products: []
        };

        activate();

        //VARIABLES
        $scope.newProduct = {};

        // METHODS
        // declaration
        $scope.getProductsAndGoNext = getProductsAndGoNext;
        $scope, getSelectedItemsAndProceed = getSelectedItemsAndProceed;
        $scope.getFullProduct = getFullProduct;
        $scope.addProductToOrder = addProductToOrder;
        $scope.deleteProduct = deleteProduct;


        // definition
        function activate() {
            Orders
                .getCustomers()
                .then(orderSuccessFn, orderErrorFn);

            function orderSuccessFn(data, status, headers, config) {
                $scope.customers = data.data;
            }

            function orderErrorFn(data, status, headers, config) {
                alert("Error! Could not get customers list");
            }
        }

        function getProductsAndGoNext() {
            Orders
                .getProducts($scope.order.customer, $scope.order.type)
                .then(productSuccessFn, productErrorFn);

            function productSuccessFn(data, status, headers, config) {
                $scope.productsBackup = data.data;
                $scope.products = angular.copy($scope.productsBackup);
                WizardHandler.wizard().next();
            }

            function productErrorFn(data, status, headers, config) {
                alert("Error! Could not get product list");
            }
        }

        function getSelectedItemsAndProceed() {
            //get array of product ids from array of selected products (lodash probably)
            //pass this to the API in service
            //the returned list contains the items (id, count and name) in each product whose id was supplied initially

            //On the next page, each member of order.products will be exploded according to the returned list of items (count in items list will be taken into cognizance)
            //each item in the exploded list would have: name (auto), colour (manual), alteration (manual), serial_no (auto gen) (item_tag will be autogen on server on saving order)
        }

        function getFullProduct(productID) {
            var theMatch = _.find($scope.productsBackup.products, { 'id': parseInt(productID, 10) })
            return theMatch;
        }

        function addProductToOrder() {
            $scope.order.products.push(angular.copy($scope.newProduct));
            _.remove($scope.products.products, { 'id': parseInt($scope.newProduct.id, 10) })
            $scope.newProduct = {}
        }

        function deleteProduct(index, product) {
            delete $scope.order.products.splice(index, 1);
            if (product && product.id) {
                $scope.products.products.push(angular.copy(_.find($scope.productsBackup.products, { 'id': parseInt(product.id, 10) })));
            }
        }
    }
})();
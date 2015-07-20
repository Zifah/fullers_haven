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
            $scope.productsBackup = Orders.getProducts($scope.order.customer, $scope.order.type);
            $scope.products = angular.copy($scope.productsBackup);
            WizardHandler.wizard().next();
            //.then(productSuccessFn, productErrorFn);

            //function productSuccessFn(data, status, headers, config) {
            //    $scope.products = data.data;
            //    WizardHandler.wizard().next();
            //}

            //function productErrorFn(data, status, headers, config) {
            //    alert("Error! Could not get product list");
            //}
        }

        function getFullProduct(productID) {
            var theMatch = _.find($scope.productsBackup.products, { 'id': productID })
            return theMatch;
        }

        function addProductToOrder() {
            $scope.order.products.push(angular.copy($scope.newProduct));
            _.remove($scope.products.products, { 'id': $scope.newProduct.id })
            $scope.newProduct = {}
        }

        function deleteProduct(index, product) {
            delete $scope.order.products.splice(index, 1);
            if (product && product.id) {
                $scope.products.products.push(angular.copy(_.find($scope.productsBackup.products, { 'id': product.id })));
            }
        }
    }
})();
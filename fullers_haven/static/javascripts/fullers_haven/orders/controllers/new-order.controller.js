(function () {
    'use strict';

    angular
        .module('fullers_haven.orders.controllers', [])
        .controller('OrderController', OrderController);

    function OrderController($scope, $http, Orders, WizardHandler) {
        //VARIABLES
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
            products: [],
            productItems: [],
        };

        $scope.newProduct = {};
        $scope.colours = [];
        $scope.alterations = [];

        // METHODS
        // declaration
        $scope.getProductsAndGoNext = getProductsAndGoNext;
        $scope.getSelectedItemsAndProceed = getSelectedItemsAndProceed;
        $scope.getFullProduct = getFullProduct;
        $scope.addProductToOrder = addProductToOrder;
        $scope.deleteProduct = deleteProduct;

        activate();

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
            var selectedProductIDs = _.pluck($scope.order.products, 'id');
            //pass this to the API in service
            Orders
                .getProductsById(selectedProductIDs)
                .then(productSuccessFn, productErrorFn);

            function productSuccessFn(data, status, headers, config) {
                $scope.selectedProducts = data.data;
                //product: id, name, price, items
                //the returned list contains the items (id, count and name) in each product whose id was supplied initially

                //On the next page, each member of order.products will be exploded according to the returned list of items (count in items list will be taken into cognizance)
                //each item in the exploded list would have: name (auto), colour (manual), alteration (manual), serial_no (auto gen) (item_tag will be autogen on server on saving order)
                var itemCounter = 1;
                var productCounter = 1;

                for (var i = 0; i < $scope.order.products.length; i++) {
                    var thisProduct = $scope.order.products[i];
                    var fullProduct = _.find($scope.selectedProducts, { 'id': parseInt(thisProduct.id, 10) });

                    for (var j = 0; j < thisProduct.quantity; j++) {
                        var newProduct = {};
                        newProduct.id = thisProduct.id;
                        newProduct.serialNumber = productCounter;
                        newProduct.name = fullProduct.name;
                        newProduct.items = [];

                        for (var k = 0; k < fullProduct.items.length; k++) {
                            var thisItem = fullProduct.items[k];

                            for (var l = 0; l < thisItem.count; l++) {
                                var newItem = {
                                    serialNumber: itemCounter,
                                    id: thisItem.id,
                                    name: thisItem.name,
                                    colourId: '',
                                    alterationId: ''
                                };
                                newProduct.items.push(newItem);
                                itemCounter++;
                            }
                        }
                        $scope.order.productItems.push(newProduct);
                        productCounter++;
                    }
                }
                populateAlterations();
                populateColours();
                WizardHandler.wizard().next();
            }

            function productErrorFn(data, status, headers, config) {
                alert("Error! Could not get product list");
            }

        }

        function populateAlterations() {
            Orders
                .getAlterations()
                .then(alterationSuccessFn, alterationErrorFn);

            function alterationSuccessFn(data, status, headers, config) {
                $scope.alterations = data.data;
            }

            function alterationErrorFn(data, status, headers, config) {
                alert("Error! Could not get alteration list");
            }
        }

        function populateColours() {
            Orders
                .getColours()
                .then(colourSuccessFn, colourErrorFn);

            function colourSuccessFn(data, status, headers, config) {
                $scope.colours = data.data;
            }

            function colourErrorFn(data, status, headers, config) {
                alert("Error! Could not get colour list");
            }
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
(function () {
    'use strict';

    angular
        .module('fullers_haven.orders.controllers', [])
        .controller('OrderController', OrderController);

    function OrderController($scope, $http, Orders, WizardHandler) {
        //VARIABLES
        $scope.order = {
            products: [],
            productItems: [],
        };

        $scope.orderTypes = [
                {
                    name: 'Normal',
                    value: 'N'
                },
                {
                    name: 'Bulk',
                    value: 'B'
                }
        ];
        $scope.newProduct = {};
        $scope.colours = [];
        $scope.alterations = [];
        $scope.changeOrder = {};

        // METHODS
        // declaration
        $scope.getProductsAndGoNext = getProductsAndGoNext;
        $scope.getSelectedItemsAndProceed = getSelectedItemsAndProceed;
        $scope.getFullProduct = getFullProduct;
        $scope.addProductToOrder = addProductToOrder;
        $scope.deleteProduct = deleteProduct;
        $scope.getNameById = getNameById;
        $scope.refreshColours = refreshColours;
        $scope.refreshAlterations = refreshAlterations;
        $scope.saveOrder = saveOrder;
        $scope.getOrderType = getOrderType;
        $scope.getTotalOrderPieces = getTotalOrderPieces;
        $scope.getOrderTotalPrice = getOrderTotalPrice;
        $scope.validateItemsAndProceed = validateItemsAndProceed;
        $scope.initChange = initChange;
        $scope.getChangeOrder = getChangeOrder;

        //order manipulation methods
        $scope.recordOrderCompletion = recordOrderCompletion;
        $scope.recordOrderDelivery = recordOrderDelivery;
        $scope.cancelOrder = cancelOrder;

        activate();

        // definition
        function activate() {
            getCustomers();
        }

        function getCustomers() {
            if (!$scope.change) {
                Orders
                    .getCustomers()
                    .then(orderSuccessFn, orderErrorFn);
            }


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
            $scope.order.productItems = [];

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
                        itemCounter = 1;

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
            if ($scope.newProduct && $scope.newProduct.id && $scope.newProduct.quantity) {
                var fullProduct = getFullProduct($scope.newProduct.id);

                if (fullProduct.max_allowed || fullProduct.max_allowed == null || fullProduct.max_allowed >= $scope.newProduct.quantity) {
                    $scope.order.products.push(angular.copy($scope.newProduct));
                    _.remove($scope.products.products, { 'id': parseInt($scope.newProduct.id, 10) })

                    var maxPieces = $scope.productsBackup.max_pieces;

                    if (maxPieces != null && getTotalOrderPieces() > maxPieces) {
                        deleteProduct($scope.order.products.length - 1, $scope.newProduct.id);
                        alert("Item limit has been exceeded!");
                    }

                    else {
                        $scope.newProduct = {};
                    }
                }

                else {
                    alert("Limit exceeded!\r\n You cannot add more than " + fullProduct.max_allowed + " '" + fullProduct.name + "' to this order.");
                }
            }

            else {
                alert("Looks like you are missing something?");
            }
        }

        function deleteProduct(index, productId) {
            delete $scope.order.products.splice(index, 1);
            if (productId) {
                $scope.products.products.push(angular.copy(_.find($scope.productsBackup.products, { 'id': parseInt(productId, 10) })));
            }
        }

        function getNameById(id, list) {
            if (id) {
                var theMatch = _.find(list, { 'id': parseInt(id, 10) });
                return theMatch.name;
            }

            return "None";
        }

        function refreshColours() {
            populateColours();
        }

        function refreshAlterations() {
            populateAlterations();
        }

        function saveOrder() {
            var theOrder = $scope.order;

            Orders
                .saveOrder(theOrder)
                .then(orderSuccessFn, orderErrorFn);

            function orderSuccessFn(data, status, headers, config) {
                window.location.replace("/admin/app/order/" + data.data["order_id"]);
                //redirect to order details page
            }

            function orderErrorFn(data, status, headers, config) {
                alert("Error! Could not save your order!");
            }
        }

        function getOrderType() {
            var theMatch = _.find($scope.orderTypes, { 'value': $scope.order.type });

            var name = "";

            if (theMatch) {
                name = theMatch.name;
            }

            return name;
        }

        function getTotalOrderPieces() {
            var totalPieces = 0;
            var products = $scope.order.products;
            for (var i = 0; i < products.length; i++) {
                var product = products[i];
                var fullProduct = getFullProduct(product.id);
                totalPieces += fullProduct.number_of_items * product.quantity;
            }

            return totalPieces;
        }

        function getOrderTotalPrice() {
            var totalPrice = 0;

            if ($scope.order.type == 'N') {
                var products = $scope.order.products;
                for (var i = 0; i < products.length; i++) {
                    var product = products[i];
                    var fullProduct = getFullProduct(product.id);
                    totalPrice += fullProduct.price * product.quantity;
                }
            }

            return totalPrice;
        }

        function validateItemsAndProceed() {
            var productItems = $scope.order.productItems;
            var shouldProceed = true;

            for (var i = 0; i < productItems.length; i++) {
                var items = productItems[i].items;
                for (var j = 0; j < items.length; j++) {
                    var item = items[j];

                    if (!item.colourId) {
                        shouldProceed = false;
                        break;
                    }
                }

                if (!shouldProceed) {
                    alert("Colour must be selected for each item!");
                    return;
                }
            }

            WizardHandler.wizard().next();
        }

        function initChange(orderId) {
            $scope.change = true;
            $scope.orderId = orderId;
            getChangeOrder(orderId);
        }

        function getChangeOrder(orderID) {
            if (orderID) {
                Orders
                    .getOrderById(orderID)
                    .then(orderSuccessFn, orderErrorFn);
            }

            function orderSuccessFn(data, status, headers, config) {
                $scope.changeOrder = data.data;
            }

            function orderErrorFn(data, status, headers, config) {
                alert("Error getting change order");
            }
        }

        function recordOrderCompletion() {
            var orderId = $scope.orderId;

            if (orderId) {
                if ($scope.changeOrder.status != "Processing") {
                    alert("Sorry. Only 'Processing' orders can be completed.");
                }

                else {
                    var ok = confirm("You are about to mark this order as ready for pick-up/delivery. Click OK  only if this is intended.");

                    if (ok) {
                        Orders
                            .updateOrder(orderId, { 'status': 'Fulfilled' })
                            .then(orderSuccessFn, orderErrorFn);
                    }
                }
            }

            function orderSuccessFn(data, status, headers, config) {
                $scope.changeOrder = data.data;
                alert("Order has been completed and customer successfully notified.");
            }

            function orderErrorFn(data, status, headers, config) {
                alert("Error completing order");
            }
        }

        function recordOrderDelivery() {

            var orderId = $scope.orderId;

            if (orderId) {

                if ($scope.changeOrder.status != "Fulfilled") {
                    alert("Sorry. Only 'Fulfilled' orders can be delivered.");
                }

                else {
                    var ok = confirm("You are about to mark this order as delivered. Click OK  only if this is intended.");

                    if (ok) {
                        Orders
                            .updateOrder(orderId, { 'status': 'Delivered' })
                            .then(orderSuccessFn, orderErrorFn);
                    }
                }
            }

            function orderSuccessFn(data, status, headers, config) {
                $scope.changeOrder = data.data;
                alert("Order has been delivered and customer successfully notified.");
            }

            function orderErrorFn(data, status, headers, config) {
                alert("Error delivering order");
            }
        }

        function cancelOrder() {

            var orderId = $scope.orderId;

            if (orderId) {
                if ($scope.changeOrder.status != "Processing") {
                    alert("Sorry. Only 'Processing' orders can be cancelled.");
                }

                else {
                    var ok = confirm("You are about to cancel this order. Click OK  only if this is intended.");

                    if (ok) {
                        Orders
                            .updateOrder(orderId, { 'status': 'Cancelled' })
                            .then(orderSuccessFn, orderErrorFn);
                    }
                }
            }

            function orderSuccessFn(data, status, headers, config) {
                $scope.changeOrder = data.data;
                alert("Order has been cancelled and customer successfully notified.");
            }

            function orderErrorFn(data, status, headers, config) {
                alert("Error cancelling order");
            }
        }
    }
})();
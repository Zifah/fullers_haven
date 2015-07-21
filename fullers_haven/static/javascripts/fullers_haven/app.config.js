(function () {
    'use strict';

    angular
        .module('fullers_haven.config', [])
        .config(config);

    function config($locationProvider, $httpProvider) {
        $locationProvider.html5Mode(true);
        $locationProvider.hashPrefix('!');

        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    }

})();
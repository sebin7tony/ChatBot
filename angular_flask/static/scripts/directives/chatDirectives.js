'use strict';

angular.module('chatWebApp')
    .directive("bindCompiledHtml", function($compile,$templateRequest) {
	  	return {
		    template: '<div></div>',
		    scope: {
		      rawHtml: '=bindCompiledHtml'
		},
	    link: function(scope, elem, attrs) {
	      scope.$watch('rawHtml', function(value) {
	        if (!value) return;
	        // we want to use the scope OUTSIDE of this directive
	        // (which itself is an isolate scope).
	        $templateRequest(value).then(function(html){
	        	
		        var newElem = $compile(html)(scope.$parent);
		        elem.contents().remove();
		        elem.append(newElem);
		    });
	        
	      });
	    }
	  };
	});
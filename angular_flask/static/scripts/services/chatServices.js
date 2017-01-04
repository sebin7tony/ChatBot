'use strict';

angular.module('chatWebApp')
    .factory('chatservice', function ($http,$location) {

    	var data = {};

		//var hostname = $location.host()+":"+$location.port();
		var hostname = 'localhost:5000';


	    data.getReply = function(text){

	        var url = "http://"+hostname+"/jarvis/api/v1.0/text_processor";
	        var data = JSON.parse('{"text": "'+text+'"}');
	        var config = {
	                headers : {
	                    'Content-Type': 'application/json'
	                }
	        }

	        return $http.post(url, data, config)
	            .success(function (data, status, headers, config) {

	                //console.log("inside getemailwiseAnalyticsData success : "+JSON.stringify(data,null,4));
	                return data;
	            })
	            .error(function (data, status, header, config) {

	                console.error('Error in executing the getReply');
	                console.log(data);
	                return undefined;
	            });

	    }; //end of getReply function

	    return data;
        
    });
'use strict';

angular.module('chatWebApp')
    .controller('ChatCtrl', function ($scope,chatservice) {

        $scope.exmplMessage = {
            "sender" : "Jarvis",
            "dataitem" : ['one', 'two', 'three'],
            "template" : "/static/partials/test.html"
        };

        $scope.messages = [];
        $scope.newMessage = '';
        $scope.glued = true;

        $scope.getReplyFromJarvis = function(text){

            chatservice.getReply(text).then(
                function (data){

                    if(data !== undefined){
                        console.log("getReplyFromJarvis :"+JSON.stringify(data.data,null,4));
                        $scope.responseOBJ = data.data;

                        $scope.currentMessage = {
                            "sender" : "Jarvis",
                            "dataitem" : $scope.responseOBJ.data,
                            "template" : "/static/partials/"+$scope.responseOBJ.template
                        };

                        $scope.messages.push($scope.currentMessage);
                    }
                    else{
                        
                        $scope.responseOBJ = undefined;
                        //console.log("getEmailWiseData is undefined");
                    }

                },
                function(error){

                    //console.log("getEmailWiseData call failed");
                    $scope.responseOBJ = undefined;
                }
            );
        };


        $scope.sendMessage = function(){

            var currentUsers = 'User'

            $scope.currentMessage = {
                "sender" : currentUsers,
                "dataitem" : $scope.newMessage,
                "template" : "/static/partials/text-message.html"
            };

            $scope.messages.push($scope.currentMessage);
            $scope.getReplyFromJarvis($scope.newMessage);
            $scope.newMessage = undefined;
        }

        $scope.appliedClass = function(sender){

            if(sender == 'Jarvis'){
                return 'left-in';
            }
            else{
                return 'right-in pull-right user-comment';
            }
        }

        $scope.setChoiceForAxis = function(axis,choice){

            if(axis === 'x'){

                $scope.x_axis = choice;
            }
            else if(axis === 'y'){

                $scope.y_axis = choice;
            }

            console.log("x "+$scope.x_axis+" and y "+$scope.y_axis)
        }

    });

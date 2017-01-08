'use strict';

angular.module('chatWebApp')
    .controller('ChatCtrl', function ($scope,chatservice,$timeout) {

        $scope.graphCount = 0;

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
                        //console.log("getReplyFromJarvis :"+JSON.stringify(data.data,null,4));
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

        $scope.addToMessageList = function(user,data,template){

            $scope.currentMessage = {
                "sender" : user,
                "dataitem" : data,
                "template" : template
            };

            $scope.messages.push($scope.currentMessage);

        }


        $scope.sendMessage = function(){

            var currentUsers = 'User';
            var template = "/static/partials/text-message.html";
            var tmp = {};
            tmp['text'] = $scope.newMessage;

            $scope.addToMessageList(currentUsers,tmp,template);
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

            //console.log("x "+$scope.x_axis+" and y "+$scope.y_axis)
        }


        $scope.getChartData = function(){

            if($scope.x_axis !== undefined && $scope.y_axis !== undefined){

                chatservice.getChart($scope.x_axis,$scope.y_axis,$scope.responseOBJ.context).then(
                    function (data){

                        if(data !== undefined){
                            //console.log("getChartData :"+JSON.stringify(data.data,null,4));
                            $scope.responseOBJ = data.data;

                            $scope.currentMessage = {
                                "sender" : "Jarvis",
                                "dataitem" : $scope.responseOBJ.data,
                                "template" : "/static/partials/"+$scope.responseOBJ.template
                            };

                            $scope.messages.push($scope.currentMessage);
                            console.log(JSON.stringify($scope.messages,null,4));
                            console.log($scope.messages.length,null,4);
                            $timeout(function(){
                                $scope.showChart($scope.responseOBJ.data.template_data,$scope.messages.length-1);
                            }, 500);
                            //$scope.showChart($scope.responseOBJ.data.template_data);
          
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
            }
            else{
                var currentUsers = "Jarvis";
                var tmp = {};
                tmp['text'] = "Please make sure that you have properly selected both x and y axis";
                var template = "/static/partials/text-message.html";
                $scope.addToMessageList(currentUsers,tmp,template);
            }
        }


        $scope.showChart = function(chartdata,index){

            console.log("Inside showChart "+JSON.stringify(chartdata,null,4));
            var showdataLabel= [];

            for(var label in chartdata['x']){

                showdataLabel.push(chartdata['x'][label]);
            }

            var showdata = [$scope.responseOBJ.context.frame['x_axis']]
            for(var data in chartdata['y']){

                showdata.push(parseFloat(chartdata['y'][data]).toFixed(2));
            }

            //console.log("showdataLabel "+JSON.stringify(showdataLabel,null,4));
            //console.log("showdata "+JSON.stringify(showdata,null,4));

            /*showdata =['data1', 30, 200, 100, 400, 150, 250];
            showdataLabel = ["jab","s","ss","ds","sads","wer"]*/

            $scope.emobarchart = c3.generate({
                bindto: '#detailemo-bar-'+index,
                size: {
                      height: 250
                },
                data: {
                    columns: [
                        showdata
                    ],
                    type: 'bar'
                },
                axis: {
                    x:{
                        type: 'category',
                        categories: showdataLabel
                    }
                }
            });
        }

    }); // End of controller

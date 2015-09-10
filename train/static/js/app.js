var app = angular.module("train-station", ['angularMoment']);

app.controller("mainCtrl", function($scope, $http, $location) {

    $scope.trains = [];

    var fetchTrains = function(){
        $http.get('/v1/train/')
        .success(function(data, status, headers, config){
            $scope.trains = data.result;
            var thing = $location.search().train;
            if(thing !== undefined) {
                for (var i = 0; i < $scope.trains.length; i++){
                    if($scope.trains[i].id == thing){
                        $scope.status.activePage = 'train';
                        $scope.status.currentTrain = $scope.trains[i];
                    }
                }
            }
        });
    };

    $scope.logout = function(){
        $http.get('/v1/account/logout')
        .success(function(data, status, headers, config){
            $scope.status.loggedIn = false;
        })
        .error(function(data, status, headers, config){
            alert('Logout Fail!');
        });
    };

    $scope.status = {
        loggedIn: false,
        newTrain: false,
        activePage: 'index',
        currentTrain: null,
        currentUser: null,
        editMode: false,
        loginMethods: window.config.loginMethods,
        registrationRules: window.config.registration,
        customInput: false
    };

    if(window.user !== undefined && window.user !== null){
        $scope.status.loggedIn = true;
        console.log("User: " + window.user);
        $scope.status.currentUser = window.user.username;
        fetchTrains()
    }

    $scope.viewTrain = function(train){
        $scope.status.activePage = 'train';
        $scope.status.currentTrain = train;
    };

    $scope.activateTrainForm = function(){
        $scope.status.newTrain = true;
        $scope.status.activePage = 'train-form';
    };

    $scope.createTrain = function(){

        if($scope.status.customInput){
            $scope.newTrainExpires = $scope.newTrainExpiresCustom * 60;
        }

        console.log("Train Name: " + $scope.newTrainName);
        console.log("Train Expires: " + $scope.newTrainExpires);
        console.log("Custom Time: " + $scope.customInput);

        $http.post('/v1/train/', {
            "name": $scope.newTrainName,
            "expires": $scope.newTrainExpires
        })
        .success(function(data, status, headers, config){
            $scope.trains.push(data.result);
            $scope.status.newTrain = false;
            $scope.newTrainName = null;
            $scope.newTrainExpires = null;
            $scope.newTrainExpiresCustom = null;
            $scope.hideCustomInput();
            $scope.status.activePage = 'index';
        })
        .error(function(data, status, headers, config){
            console.log(data);
        });
    };

    $scope.register = function(){
        $http.post('/v1/account/register', {
            "username": $scope.username,
            "password": $scope.password
        })
        .success(function(data, status, headers, config){
            console.log(data);
            alert(data.message);
        })
        .error(function(data, status, headers, config){
            console.log(data);
        });

    };

    $scope.deleteTrain = function(train){
        $http.delete('/v1/train/'+train.id)
        .success(function(data, status, headers, config){
            console.log ('successful delete');
            fetchTrains();
            $scope.status.activePage = 'index';
        })
        .error(function(data, status, headers, config){
            console.log(data);
        })
    };

    $scope.leaveTrain = function(){
        $http.post('/v1/train/'+$scope.status.currentTrain.id+'/leave')
        .success(function(data, status, headers, config){
            var toRemove = $scope.status.currentTrain.passengers.indexOf($scope.status.currentUser)
            $scope.status.currentTrain.passengers.splice(toRemove, 1);
            $scope.status.activePage = 'index';
        })
        .error(function(data, status, headers, config){
            console.log(data)
        });
    };

    $scope.boardTrain = function(){
        $http.post('/v1/train/'+$scope.status.currentTrain.id+'/join')
        .success(function(data, status, headers, config){
            $scope.status.currentTrain.passengers.push($scope.status.currentUser);
        })
        .error(function(data, status, headers, config){
            console.log(data);
        });
    };

    $scope.signIn = function(){
        $http.post('/v1/account/login', {
            "username": $scope.username,
            "password": $scope.password
        })
        .success(function(data, status, headers, config){
            console.log(data);
            $scope.status.loggedIn = true;
            $scope.status.currentUser = $scope.username.toLowerCase();
            fetchTrains();
        })
        .error(function(data, status, headers, config){
            console.log(data);
            alert(data.error);
        });
    };

    $scope.casSignIn = function(){
        window.location = "/v1/account/cas_login";
    };

    $scope.showCustomInput = function(){
        console.log("Time selected: " + $scope.newTrainExpires);
        if($scope.newTrainExpires == -1){
            console.log("Custom time selected");

            $scope.status.customInput = true;
            $scope.newTrainExpires = null;
            $scope.newTrainExpiresCustom = null;
        }
    };

    $scope.hideCustomInput = function(){
        $scope.status.customInput = false;
        $scope.newTrainExpires = null;
        $scope.newTrainExpiresCustom = null;
    };

});


<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="description" content="PROVaaS">
        <meta name="author" content="Lingduo Kong/Tanu Malik">
        <link rel="icon" href="img/icon.png">
        <title>PROVaaS</title>
        <!-- Bootstrap core CSS -->
        <link rel="stylesheet" href="css/bootstrap.css">
        <script src="js/jquery.js"></script>
        <script src="js/bootstrap-dropdown.js"></script>
        <style>h1, h2, h3{color:#8A2E2E}</style>
    </head>
    <body>
        <?php include 'php/nav.php';?>
        <div class="container" style="padding-top:70px">
            <div id="API" class="jumbotron" style="height:1000px;">
                <h2>API</h2><hr>
                <div class="col-md-4">
                    <p>
                        <small>
                        <a href="">Link for POST API</a><br>
                        show the description for API 1<br>
                        </small>
                    </p>
                    <img src="img/Download.png" style="width:50px;height:50p" id="post" value="post_client">
                    <hr>
<!--                     <p>
                        <small>
                        <a href="">Link for API 1</a><br>
                        show the description for API 1<br>
                        </small>
                    </p>
                    <button class="btn btn-primary btn" id="q1" value="q1_client">GET API 1</button> -->
                </div>
                <div class="col-md-4">
                    <p>
                        <small>
                        <a href="">Link for API 2</a><br>
                        show the description for API 2<br>
                        </small>
                    </p>
                    <img src="img/Upload.png" style="width:50px;height:50p" id="q2" value="q2_client">
                    <hr>
<!--                     <p>
                        <small>
                        <a href="">Link for API 3</a><br>
                        show the description for API 3<br>
                        </small>
                    </p>
                    <button class="btn btn-primary btn" id="q3" value="q3_client">GET API 3</button> -->
                </div>
                <div class="col-md-4">
                    <p>
                        <small>
                        <a href="">Link for API 5</a><br>
                        show the description for API 5<br>
                        </small>
                    </p>
                    <img src="img/Cancel.png" style="width:50px;height:50p" id="q5" value="q5_client">
                    <hr>
<!--                     <p>
                        <small>
                        <a href="">Link for API 7</a><br>
                        show the description for API 7<br>
                        </small>
                    </p>
                    <button class="btn btn-primary btn" id="q7" value="q7_client">GET API 7</button> -->
                </div>
                <div class="col-md-12">
                    <br><a href="" class="btn btn-lg btn-link pull-right" role="button">Explore More</a><br>
                </div>
                <div class="col-md-6 ">
                    <br>
                    <textarea id="myTextarea" name="JsonRaw" cols="60" rows ="20"></textarea>
                </div>
                <div class="col-md-6">
                    <br>
                    <img src="img/sampledata1.png" style="width:400px;height:400px">
                </div>
                <div class="col-md-12" id="interactive"></div>
                <script src="js/api.js">
                </script>
            </div>
            <div id="Responses" class="jumbotron" style="height:400px">
                <h2>Responses</h2>
                <hr style="padding:5px">
                <div class="col-md-2"><h4>
                    GET
                </h4></div>
                <div class="col-md-2"><h4>
                    <span class="label label-success">200 OK</span>
                </h4></div>
                <div class="col-md-8"><h4>
                    The resource was successfully retrieved.
                </h4></div>
                <hr style="padding:5px">
                <div class="col-md-2"><h4>
                    POST
                </h4></div>
                <div class="col-md-2"><h4>
                    <span class="label label-success">201 OK</span>
                </h4></div>
                <div class="col-md-8"><h4>
                    The resource was successfully created. The information held in the new resource will be provided in the response body.
                </h4></div>
                <hr style="padding:5px">
                <div class="col-md-2"><h4>
                    POST
                </h4></div>
                <div class="col-md-2"><h4>
                    <span class="label label-success">202 Accepted</span>
                </h4></div>
                <div class="col-md-8"><h4>
                    The sub-resource was successfully added to the target resource.
                </h4></div>
                <hr style="padding:5px">
            </div>
            <div id="Authentication" class="jumbotron" >
                <h2>Authentication</h2><hr>
                <p>
                    <small>
                    The API supports authentication by either API key or OAuth. The API can also be accessed anonymously if you do not wish to authenticate. In this case only public documents will be visible and documents may not be added/modified.<br>
                    </small>
                </p>
                <hr>
                <p>
                    <small>
                    <a href="">Create user</a><br>
                    curl -i -X POST -H "Content-Type: application/json" -d '{"username":"demouser","password":"demopass"}' http://SERVER_IP:5000/api/users<br>
                    </small>
                </p>
                <p>
                    <small>
                    <a href="">Generate token for demouser</a><br>
                    curl -u demouser:demopass  http://SERVER_IP:5000/api/token<br>
                    </small>
                </p>
                <p>
                    <small>
                    <a href="">Test authentication with user and password</a><br>
                    curl -u demouser:demopass  http://SERVER_IP:5000/api/resource<br>
                    </small>
                </p>
                <p>
                    <small>
                    <a href="">Test authentication with token</a><br>
                    If your generated token is:<br>
                    "token": some_long_string<br>
                    Then you can use:<br>
                    curl -u some_long_string: http://SERVER_IP:5000/api/resource<br>
                    Please note that request contains your token followed by colon
                    </small>
                </p>
            </div>
            <div id="GithubRepo" class="jumbotron">
                <h2>Github Repository</h2>
                <hr>
                <p>
                    <small>
                    <class="active"><a href="">Link 1</a><br>
                    </small>
                </p>
            </div>
        </div>
    </div>
</body>

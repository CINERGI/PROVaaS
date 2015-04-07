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
        <style>
        h1, h2, h3{color:#A30000}
        h1{font-size: 50px}
        .cloud{
        width: 600px;
        position: absolute;
        right: 0px;
        }
        .logo{
        width:300px;
        position:absolute;
        top:130px;
        right:140px;
        background-color:#993333;
        border: 2px solid #a1a1a1;
        border-radius: 25px;
        }
        .stats{
        width:300px;
        position:absolute;
        top:310px;
        bottom: 450px;
        right:140px;
        border-radius: 25px;
        text-align: center;
        }
        .hrline{
        background-color:#8A8A8A;
        height:23px;
        margin-left: -15px;
        margin-right: -15px;
        }
        </style>
    </head>
    <body>
        <?php include 'php/nav.php';?>
        <div class="container-fluid" style="background-color:#f8f8f8">
            <div class="container" style="padding-top:100px; height:450px">
                <div class="col-xs-5" style="text-align: center;">
                    <br>
                    <br>
                    <br>
                    <h1>Provass</h1>
                    <h1>data</h1>
                    <h1>servise</h1>
                </div>
                <div class="col-xs-7">
                    <img src="img/basic_cloud.png" class="cloud">
                    <img src="img/logo2.png" class="logo pull-right">
                    <div class="stats"><h3>Documents number: 50</h3></div>
                </div>
            </div>
            <hr class="hrline">
            <div class="container">
                <h2 id="News" style="text-align: left;">News</h2>
                <hr>
                <div class="row">
                    <div class="col-xs-4">Title1</div>
                    <div class="col-xs-8">Details</div>
                    <div class="col-xs-4">Title2</div>
                    <div class="col-xs-8">Details</div>
                    <div class="col-xs-4">Title3</div>
                    <div class="col-xs-8">Details</div>
                </div>
                <br>
                <br>
            </div>
        </div>
        <div class="container" style="padding-top:30px">
            <div id="introduction" class="jumbotron" >
                <h2>Introduction</h2><br>
                <hr>
                <p>
                    <small>
                    PROVaaS is a RESTful service for storage and access of provenance documents, following the W3C <a href="#">PROV</a> standard. Using the REST API, clients can upload multiple documents described in PROV. The service maintains the provenance, if any, among the documents. The clients can query the provenance of an entity or activity using the PROV description model.
                    <p>
                        This document provides details and examples of the available endpoints and resources at a low level, and how provenance is maintained across documents.
                        <!--Existing libraries can be used instead to publish and access provenance documents available through PROVaaS-->
                    </p>
                    </small>
                </p>
            </div>
            <div id="Service_Features" class="jumbotron">
                <h2>Service Features</h2><hr>
            </div>
            <div id="Service_Use" class="jumbotron">
                <h2>Service use</h2><hr>
            </div>
            <div id="Related_Links" class="jumbotron">
                <h2>About</h2><hr>
                <p>
                    <small>
                    <class="active"><a href="">Link 1</a><br>
                    </small>
                </p>
            </div>
            <div id="Contact_us" class="jumbotron">
                <h2>Contact US</h2><hr>
                <p>
                </p>
            </div>
        </div>
    </body>

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
                    <h1>Your</h1>
                    <h1>Provenance</h1>
                    <h1>Host</h1>
                </div>
                <div class="col-xs-7">
                    <img src="img/basic_cloud.png" class="cloud">
                    <!--<img src="img/logo2.png" class="logo pull-right">-->
                    <img src="img/Icon2.png" class="logo pull-right">
                    <!--<div class="stats"><h3>Documents number: 50</h3></div>-->
                </div>
            </div>
            <hr class="hrline">
            <div class="container">
                <h2 id="News" style="text-align: left;">News</h2>
             <!--   <hr>-->
                <div class="row">
                    <div class="col-xs-4">07-05-14</div>
                    <div class="col-xs-8">Presenting PROVaaS at Theory and Practice of Provenance (TaPP)</div>
                    <div class="col-xs-4">04-09-14</div>
                    <div class="col-xs-8">Demonstrating PROVaaS at Earth Tech Hands Meeting</div>
                    <div class="col-xs-4">04-05-14</div>
                    <div class="col-xs-8">PROVaaS website launched</div>
                    <div class="col-xs-4">04-01-14</div>
                    <div class="col-xs-8">Provenance API launched</div>
                </div>
                <br>
                <br>
            </div>
        </div>
        <div class="container" style="padding-top:30px">
            <!--<div id="introduction" class="jumbotron" >
                <h2>Introduction</h2><br>
                <hr>
                <p>
                    <small>
                   </small>
                </p>
            </div>-->
            <div id="Service_Features" class="jumbotron">
              <h2>PROV-As-A-Service </h2><hr>
                    <p>
	      PROVaaS is a RESTful service for storage and access of provenance documents, following the W3C <a href="#">PROV</a> standard. Using the REST API, clients can upload multiple documents described in PROV. The service maintains the provenance, if any, among the documents. The clients can query the provenance of an entity or activity using the PROV description model.
            </p>
<p>            This document provides details and examples of the available endpoints and resources at a low level, and how provenance is maintained across documents.
                        <!--Existing libraries can be used instead to publish and access provenance documents available through PROVaaS-->
                    </p>

            </div>
            <div id="Service_Use" class="jumbotron">
                <h2>Service Use</h2><hr>
		<p>
	 We currently host provenance data for the following projects: <a href="http://hydro10.sdsc.edu">CINERGI</a>, <a href="http://earthcube.org/group/geodataspace">GeoDataspace</a>, <a href="http://swift-lang.org">Swift</a>, and <a href="ihttp://www.cs.iit.edu/%7edbgroup/research/gprom.php">GPRoM</a>.
		</p>
            </div>
	    <div id="Publications" class="jumbotron">
                <h2>Publications</h2><hr>
		<p>
		<small>T. Malik, M. Yu, and C. Vlaescu. PROVaaS: A Pay-as-you-service for Storing and Querying Provenance. Poster in Theory and Practice of Provenance (TaPP), 2015. <a href="https://www.dropbox.com/s/tnlxgg7ksu1rxdv/TaPPPoster.pdf?dl=0">(pdf)</a></small>
		</p>
            </div>

            <div id="Related_Links" class="jumbotron">
                <h2>About</h2><hr>
                <p>
		    The PROVaaS data management is built by the Computation Institute, University of Chicago, with the generous support of the National Science Foundation under awards ICER-1343816(sub-contract) and ICER-1440327.
                </p>
            </div>
            <div id="Contact_us" class="jumbotron">
                <h2>Contact Us</h2><hr>
                <p>
		  For more information about service use, please contact us at <a href="mailto:scidataspace@gmail.com">PROVaaS</a>

                </p>
            </div>
        </div>
    </body>

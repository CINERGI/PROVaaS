<?php
$myfile = fopen("../JSON/json-post.txt", "r") or die("Unable to open file!");
echo fread($myfile,filesize("../JSON/json-post.txt"));
fclose($myfile);
?>

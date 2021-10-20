<?php

$uploadOk = 1;

// Check if image file is a actual image or fake image
if(isset($_POST["submit"]))
{
  $UserId = $_POST['UserId'];
  $ProjectId = $_POST['ProjectId'];
}
$target_dir = "D:/ineuron/ML/ML project/test_scrapper_and_sentiment/training_data/";
$target_file = $target_dir . '/' . $UserId . '/' . $ProjectId . '/' .  basename($_FILES["fileToUpload"]["name"]);
$jsonFileType = strtolower(pathinfo($target_file,PATHINFO_EXTENSION));


// Allow certain file formats
if($jsonFileType != "json" ) {
  echo "Sorry, only json files are allowed.";
  $uploadOk = 0;
}

// Check if $uploadOk is set to 0 by an error
if ($uploadOk == 0) {
  echo "Sorry, your file was not uploaded.";
// if everything is ok, try to upload file
} else {
  if (move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file)) {
    echo "The file ". htmlspecialchars( basename( $_FILES["fileToUpload"]["name"])). " has been uploaded.";
  } else {
    echo "Sorry, there was an error uploading your file.";
  }
}
?>


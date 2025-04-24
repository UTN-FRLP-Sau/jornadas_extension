<?php
require 'php_terceros/PHPMAILER-5.2/PHPMailerAutoload.php';

// Crear una nueva instancia de PHPMailer
$mail = new PHPMailer;

// Configuración del servidor SMTP
$mail->isSMTP();
$mail->Host = 'smtp.office365.com';
$mail->Port = 587;
$mail->SMTPSecure = 'tls';
$mail->SMTPAuth = true;
$mail->Username = 'graduados@frlp.utn.edu.ar'; // Reemplaza con tu dirección de correo electrónico de Office 365
$mail->Password = 'gRxd2022'; // Reemplaza con tu contraseña de Office 365

if ($_SERVER["REQUEST_METHOD"] == "POST") {
  // Obtener los valores del formulario
  $correo = $_POST["email"];


  // Destinatario del correo
  $destinatario = "graduados@frlp.utn.edu.ar";


  // Contenido del correo
  $contenido .= "Correo Electrónico: " . $correo . "\n";


  // Configuración del remitente y destinatario
  $mail->setFrom('graduados@frlp.utn.edu.ar', 'Formulario WEB'); // Reemplaza con tu dirección de correo electrónico y nombre del remitente
  $mail->addAddress('graduados@frlp.utn.edu.ar', 'SEU'); // Reemplaza con la dirección de correo electrónico y nombre del destinatario

  // Contenido del correo
  $mail->Body = $contenido;

  // Enviar el correo
  if (!$mail->send()) {
      echo 'Error al enviar el mensaje: ' . $mail->ErrorInfo;
  } else {
      header("Location: index.html", TRUE, 301);;
  }
  }
  ?>
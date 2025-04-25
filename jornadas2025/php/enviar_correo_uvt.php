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
  $nombre = $_POST["name"];
  $correo = $_POST["email"];
  $asunto = $_POST["subject"];
  $mensaje = $_POST["message"];

  // Destinatario del correo
  $destinatario = "uvt@frlp.utn.edu.ar";

  // Asunto del correo
  $asunto = "Formulario de contacto: " . $asunto;

  // Contenido del correo
  $contenido = "Nombre: " . $nombre . "\n";
  $contenido .= "Correo Electrónico: " . $correo . "\n";
  $contenido .= "Motivo: " . $asunto . "\n";
  $contenido .= "Mensaje: " .$mensaje ;

  // Configuración del remitente y destinatario
  $mail->setFrom('graduados@frlp.utn.edu.ar', 'Consulta WEB'); // Reemplaza con tu dirección de correo electrónico y nombre del remitente
  $mail->addAddress('uvt@frlp.utn.edu.ar', 'UVT'); // Reemplaza con la dirección de correo electrónico y nombre del destinatario

  // Contenido del correo
  $mail->Subject = $asunto;
  $mail->Body = $contenido;

  // Enviar el correo
  if (!$mail->send()) {
      echo 'Error al enviar el mensaje: ' . $mail->ErrorInfo;
  } else {
      header("Location: index.html", TRUE, 301);;
  }
  }
  ?>
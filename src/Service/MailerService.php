<?php

namespace App\Service;

use Symfony\Bridge\Twig\Mime\TemplatedEmail;
use Symfony\Component\Filesystem\Filesystem;
use Symfony\Component\Mailer\MailerInterface;
use Symfony\Component\Mime\Address;

class MailerService
{
    private $admins;
    private $mailer;
    private $fileSystem;

    public function __construct(MailerInterface $mailer)
    {
        $this->admins = [new Address('kevin.ayrault87@gmail.com', 'Kévin')];
        $this->mailer = $mailer;
        $this->fileSystem = new Filesystem();
    }

    function sendLog(string $typeLog, array $logFiles) {
        $email = (new TemplatedEmail())
            ->from('admin@chourmolympique.fr')
            ->to(...$this->admins)
            ->subject("Logs de la/le ". strtolower($typeLog))
            ->htmlTemplate('emails/logs.html.twig')
            ->context([
                'typeLog' => $typeLog
            ]);

        foreach ($logFiles as $logFile) {
            if ($this->fileSystem->exists($logFile)) {
                $email->attachFromPath($logFile);
            }
        }

        $this->mailer->send($email);
    }

    function sendErreurRoute(string $route, \Exception $e) {
        $email = (new TemplatedEmail())
            ->from('admin@chourmolympique.fr')
            ->to(...$this->admins)
            ->subject("Erreur sur la route ${route}")
            ->htmlTemplate('emails/erreurs_lors_traitement.html.twig')
            ->context([
                'route' => $route,
                'fichier' => $e->getFile(),
                'ligne' => $e->getLine(),
                'message' => $e->getMessage()
            ]);

        $this->mailer->send($email);
    }

}
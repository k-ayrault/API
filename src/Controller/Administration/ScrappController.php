<?php

namespace App\Controller\Administration;

use App\Service\MailerService;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpKernel\Attribute\AsController;
use App\Service\ScrappService;
use Symfony\Component\HttpKernel\KernelInterface;

#[AsController]
class ScrappController
{
    private $scrappService;
    private $mailerService;
    private $cheminPublic;

    public function __construct(ScrappService $scrappService, MailerService $mailerService, KernelInterface $kernel)
    {
        $this->scrappService = $scrappService;
        $this->mailerService = $mailerService;
        $this->cheminPublic = $kernel->getProjectDir() . "/public/";
    }

    public function scrappClubs(Request $request)
    {
        try {
            $logFichiers = $this->scrappService->scrapp();
            $this->mailerService->sendLog("Scrapping des données des joueurs et clubs", $logFichiers);
            return new JsonResponse(["pass" => true]);
        } catch (\Exception $e) {
            $route = $request->attributes->get("_route");
            $this->mailerService->sendErreurRoute($route, $e);
            return new JsonResponse(["pass" => false, "message" => $e->getMessage()]);
        }
    }

    public function saveScrapp(Request $request)
    {
        try {
            $logFichiers = [];

            $log_save_club = $this->cheminPublic;
            $log_save_club .= $this->scrappService->saveClubScrapp();
            $logFichiers[] = $log_save_club;

            $log_save_joueur = $this->cheminPublic;
            $log_save_joueur .= $this->scrappService->saveJoueursScrapp();
            $logFichiers[] = $log_save_joueur;

            $this->mailerService->sendLog("Sauvegarde des données scrappées pour les clubs et les joueurs", $logFichiers);

            return new JsonResponse(["pass" => true]);
        } catch (\Exception $e) {
            $route = $request->attributes->get("_route");
            $this->mailerService->sendErreurRoute($route, $e);
            return new JsonResponse(["pass" => false, "message" => $e->getMessage()]);
        }
    }

}
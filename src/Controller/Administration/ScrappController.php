<?php

namespace App\Controller\Administration;

use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpKernel\Attribute\AsController;
use App\Service\ScrappService;

#[AsController]
class ScrappController
{
    private $scrappService;

    public function __construct(ScrappService $scrappService)
    {
        $this->scrappService = $scrappService;
    }

    public function scrappClubs() {
        try {
            $this->scrappService->scrapp();
            return new JsonResponse(["pass"=> true]);
        } catch (\Exception $e) {
            return new JsonResponse(["pass"=> false, "message" => $e->getMessage()]);
        }
    }

    public function saveScrapp() {
        try {
            $this->scrappService->saveClubScrapp();
            $this->scrappService->saveJoueursScrapp();
            return new JsonResponse(["pass"=> true]);
        } catch (\Exception $e) {
            return new JsonResponse(["pass"=> false, "message" => $e->getMessage()]);
        }
    }

}
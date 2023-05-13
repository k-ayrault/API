<?php

namespace App\Controller\ApiCustom;

use App\Entity\Joueur;
use App\Repository\JoueurRepository;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpKernel\Attribute\AsController;
use Symfony\Component\HttpKernel\Exception\NotFoundHttpException;

#[AsController]
class GetJoueurByIdTransferMarkt extends AbstractController
{
    public function __construct(private readonly JoueurRepository $joueurRepository)
    {
    }

    public function __invoke(Request $request): Joueur
    {
        $idTransfermarkt = $request->query->get("id_transfermarkt");
        
        # On vérifie que l'ID TransferMarkt est présent pour faire la recherche    
        if (!$idTransfermarkt) {
            throw new \Exception("No id_transfermarkt");
        }
        
        # On vérifie que cet ID TransferMarkt est un entier
        if (!is_numeric($idTransfermarkt)) {
            throw new \Exception("L'ID TransferMarkt doit être un entier !!");
        }
        
        $joueur = $this->joueurRepository->findByIdTransfermarkt(idTransferMarkt:$idTransfermarkt);
        
        # On vérifie que l'on a bien trouvé un joueur pour cet ID TransferMarkt
        if (!$joueur) {
            throw new NotFoundHttpException("Aucun joueur pour l'ID TransferMarkt : $idTransfermarkt");
        }
        
        return $joueur;
    }
}

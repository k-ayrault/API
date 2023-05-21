<?php

namespace App\Controller\ApiCustom;

use App\Entity\Poste;
use App\Repository\PosteRepository;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpKernel\Attribute\AsController;
use Symfony\Component\HttpKernel\Exception\NotFoundHttpException;

#[AsController]
class GetPosteByIdTransferMarkt extends AbstractController
{
    public function __construct(private readonly PosteRepository $posteRepository)
    {
    }

    public function __invoke(Request $request): Poste
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
        
        $poste = $this->posteRepository->findByIdTransfermarkt(idTransferMarkt:$idTransfermarkt);
        
        # On vérifie que l'on a bien trouvé un joueur pour cet ID TransferMarkt
        if (!$poste) {
            throw new NotFoundHttpException("Aucun poste pour l'ID TransferMarkt : $idTransfermarkt");
        }
        
        return $poste;
    }
}

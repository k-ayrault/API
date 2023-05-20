<?php

namespace App\Controller\ApiCustom;

use App\Entity\Pays;
use App\Repository\PaysRepository;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpKernel\Attribute\AsController;
use Symfony\Component\HttpKernel\Exception\NotFoundHttpException;

#[AsController]
class GetPaysByNomFr extends AbstractController
{
    public function __construct(private readonly PaysRepository $paysRepository)
    {
    }

    public function __invoke(Request $request): Pays
    {
        $nomFr = $request->query->get("nom_fr");

        # On vérifie que l'ID TransferMarkt est présent pour faire la recherche    
        if (!$nomFr) {
            throw new \Exception("No nom_fr");
        }

        $pays = $this->paysRepository->findOneBy(criteria: ["nom_fr" => $nomFr]);

        # On vérifie que l'on a bien trouvé un joueur pour cet ID TransferMarkt
        if (!$pays) {
            throw new NotFoundHttpException("Aucun pays répondant au nom : $nomFr");
        }

        return $pays;
    }
}

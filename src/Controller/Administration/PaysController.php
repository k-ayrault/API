<?php

namespace App\Controller\Administration;

use App\Entity\Pays;
use App\Repository\PaysRepository;
use phpDocumentor\Reflection\Types\Boolean;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpKernel\Attribute\AsController;
use Symfony\Component\HttpKernel\KernelInterface;

#[AsController]
class PaysController
{
    /** KernelInterface $appKernel */
    private $appKernel;

    # Chemin vers le fichier json qui contient les pays
    private $cheminPaysJson;

    # Repository pour les entities Pays
    private $rep;

    public function __construct(KernelInterface $appKernel, PaysRepository $paysRepository)
    {
        $this->appKernel = $appKernel;

        $this->cheminPaysJson = $this->appKernel->getProjectDir() . "/data_json/countries.json";

        $this->rep = $paysRepository;

        $this->lienImgPays = "https://www.countryflagsapi.com/png/{code}";
    }

    public function initPays()
    {
        # Contenu du fichier json qui contient les payss
        $contenu_fichier_pays_json = file_get_contents($this->cheminPaysJson);

        # Tableau contenant les pays du json avec comme index le code du pays et comme valeur le pays de ce dernier
        # (Ex : { "FR": "France" })
        $pays = json_decode($contenu_fichier_pays_json, true);

        try {
            # Pour chaque pays du fichier json, on vérifie si le pays n'est pas déjà présent dans la base avec le code
            # de ce dernier, si tel est le cas alors on l'enregistre
            $liste_pays = [];
            foreach ($pays as $code=>$country) {
                if (!$this->rep->find($code)) {
                    $pays = new Pays();
                    $pays->setCode($code);
                    $pays->setNom($country);
                    $drapeau_lien = str_replace("{code}", $code, $this->lienImgPays);
                    $pays->setDrapeau($drapeau_lien);
                    $this->rep->add($pays, true);
                }
            }
            return new JsonResponse(["pass"=> true]);
        } catch (\Exception $e) {
            return new JsonResponse(["pass"=> false]);
        }
    }

}
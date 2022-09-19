<?php

namespace App\Service;

use App\Entity\Club;
use App\Entity\CouleurClub;
use App\Entity\LogoClub;
use App\Entity\Pays;
use App\Entity\Stade;
use App\Repository\ClubRepository;
use App\Repository\CouleurClubRepository;
use App\Repository\JoueurRepository;
use App\Repository\PaysRepository;
use App\Repository\StadeRepository;
use DateTime;
use Locale;
use Psr\Log\LoggerInterface;
use Symfony\Component\Process\Exception\ProcessFailedException;
use Symfony\Component\Process\Process;

class ScrappService
{

    private $python;
    private $clubsJson;
    private $joueursJson;
    private $joueurRepository;
    private $clubRepository;
    private $couleurClubRepository;
    private $paysRepository;
    private $stadeRepository;
    private $logger;

    public function __construct(JoueurRepository      $joueurRepository, ClubRepository $clubRepository,
                                CouleurClubRepository $couleurClubRepository, PaysRepository $paysRepository,
                                StadeRepository       $stadeRepository, LoggerInterface $logger)
    {
        $this->python = "scrapp/scrapp.py";
        $this->clubsJson = "scrapp/clubs.json";
        $this->joueursJson = "scrapp/joueurs.json";
        $this->joueurRepository = $joueurRepository;
        $this->clubRepository = $clubRepository;
        $this->couleurClubRepository = $couleurClubRepository;
        $this->paysRepository = $paysRepository;
        $this->stadeRepository = $stadeRepository;
        $this->logger = $logger;
    }

    public function scrapp()
    {
        $process = new Process(['python', $this->python]);
        $process->setTimeout(3600);
        $process->run();

        if (!$process->isSuccessful()) {
            throw new ProcessFailedException($process);
        }
        // Cela affichera "Hello World"
        echo $process->getOutput();
    }

    public function saveClubScrapp()
    {
        //  Récupération des informations dans le json stockant les clubs récupérés via transfermarkt
        $clubsData = file_get_contents($this->clubsJson);
        $clubs = json_decode($clubsData, true);

        //  Traitement de chaque club présent dans le json
        foreach ($clubs as $clubArray) {
            //  Récupération du club déjà présent dans la base si il est déjà présent
            $clubInDb = $this->clubRepository->findOneBy(["id_transfermarkt" => $clubArray["id_transfermarkt"] ?: null]);
            //  Si le club n'est pas déjà dans la base et que le club qu'on traite a un nom, on créé un nouveau club
            if (!$clubInDb && $clubArray["nom"]) {

                $club = new Club();

                $club->setNom($clubArray["nom"] ?: null);

                $dateCreation = new DateTime($clubArray["creation"]);
                $club->setDateCreation($dateCreation ?: null);

                $club->setIdTransfermarkt($clubArray["id_transfermarkt"] ?: null);

                $club->setSiteWeb($clubArray["site"] ?: null);

                foreach ($clubArray["couleurs"] as $couleur_hexa) {
                    //  Suppression du '#' dans le code hexa scrappé
                    $couleur_hexa = str_replace("#", "", $couleur_hexa);
                    //  On regarde si le code hexa de la couleur est conforme, çàd 6 caractères (ou moins) et ne correspond pas à un string vide
                    if (strlen($couleur_hexa) <= 6 && $couleur_hexa) {
                        //  Récupération de la couleur si code hexa déjà dans la base sinon on le créer
                        $couleur = $this->couleurClubRepository->findOneBy(["hexa" => $couleur_hexa ?: null]) ?: new CouleurClub($couleur_hexa);
                        $club->addCouleur($couleur);
                    } else {
                        if ($couleur_hexa) {
                            $this->logger->warning("[SCRAPP_TO_SAVE] Le code hexa {$couleur_hexa} dépasse les 6 caractères.");
                        }
                    }
                }

                foreach ($clubArray["logos"] as $logo) {
                    if ($logo) {
                        $club->addLogo(new LogoClub($logo));
                    }
                }

                $pays = null;
                if (!$clubArray["pays"]) {
                    $this->logger->warning("[SCRAPP_TO_SAVE] Aucun pays pour le club : {$clubArray["nom"]}");
                } else {
                    //  Récupération du pays correspondant au string scrappé
                    $pays = $this->paysRepository->findOneBy(["nom_fr" => $clubArray["pays"]]);
                    //  Log afin de savoir quel club ne sera associé à aucun pays pour le faire à la main
                    if (!$pays or !$pays instanceof Pays) {
                        $this->logger->warning("[SCRAPP_TO_SAVE] Aucun pays n'a été associé dans la base au pays : '{$clubArray["pays"]}' pour le club : '{$clubArray["nom"]}'");
                    } else {
                        $club->setPays($pays);
                    }
                }
            }
            else {
                $club = $clubInDb;
            }

            if ($club) {

                $stadeArray = $clubArray["stade"];

                $anneeConstruction = intval($stadeArray["construction"]);
                //  Si le stade scrappé a un nom
                if ($stadeArray["nom"]) {
                    //  Récupération du stade déjà associé au club
                    $stade = $club->getStade();
                    //  Si le club n'a pas de stade ou que ce dernier est différent de celui scrappé, on lui associe un stade
                    if ((!$stade) || ($stade->getNom() != $stadeArray["nom"])) {
                        //  Recherche dans la base si un stade est déjà existant pour le nom et l'année de construction scrappés
                        $nouveauStade = $this->stadeRepository->findOneBy(["nom" => $stadeArray["nom"], "annee_construction" => $anneeConstruction]);
                        //  Si aucun stade ne correspond dans la base, on le créé avec les infos scrappées
                        if (!$nouveauStade) {
                            $nouveauStade = new Stade();
                            $nouveauStade->setNom($stadeArray["nom"]);
                            $nouveauStade->setAdresse($stadeArray["adresse"] ?: null);
                            $nouveauStade->setCapacite($stadeArray["capacite"] ?: null);
                            $nouveauStade->setAnneeConstruction($anneeConstruction ?: null);
                            //  Utilisation du même pays que le stade
                            $nouveauStade->setPays($pays);
                        }
                        $club->setStade($nouveauStade);
                    }
                }

                $this->clubRepository->add($club, true);
            }
        }
    }

}
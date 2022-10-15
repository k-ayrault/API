<?php

namespace App\Service;

use App\Entity\Club;
use App\Entity\Contrat;
use App\Entity\CouleurClub;
use App\Entity\ImageStade;
use App\Entity\InformationsPersonelles;
use App\Entity\Joueur;
use App\Entity\LogoClub;
use App\Entity\Pays;
use App\Entity\Poste;
use App\Entity\PosteJoueur;
use App\Entity\Pret;
use App\Entity\Stade;
use App\Entity\Transfert;
use App\Repository\ClubRepository;
use App\Repository\CouleurClubRepository;
use App\Repository\ImageStadeRepository;
use App\Repository\JoueurRepository;
use App\Repository\LogoClubRepository;
use App\Repository\PaysRepository;
use App\Repository\PosteRepository;
use App\Repository\StadeRepository;
use DateTime;
use Locale;
use Psr\Log\LoggerInterface;
use Symfony\Component\Process\Exception\ProcessFailedException;
use Symfony\Component\Process\Process;
use Symfony\Component\Validator\Constraints\Image;

class ScrappService
{

    private $scrappJoueurs;
    private $clubsJson;
    private $joueursJson;
    private $joueurRepository;
    private $clubRepository;
    private $couleurClubRepository;
    private $paysRepository;
    private $stadeRepository;
    private $posteRepository;
    private $imageStadeRepository;
    private $logoClubRepository;
    private $logDir;

    public function __construct(JoueurRepository      $joueurRepository, ClubRepository $clubRepository,
                                CouleurClubRepository $couleurClubRepository, PaysRepository $paysRepository,
                                StadeRepository       $stadeRepository, PosteRepository $posteRepository,
                                ImageStadeRepository $imageStadeRepository, LogoClubRepository $logoClubRepository)
    {
        $this->scrappJoueurs = "scrapp/scrapp.py";
        $this->clubsJson = "scrapp/donnees/clubs.json";
        $this->joueursJson = "scrapp/donnees/joueurs.json";
        $this->logDir = "scrapp/log";
        $this->joueurRepository = $joueurRepository;
        $this->clubRepository = $clubRepository;
        $this->couleurClubRepository = $couleurClubRepository;
        $this->paysRepository = $paysRepository;
        $this->stadeRepository = $stadeRepository;
        $this->posteRepository = $posteRepository;
        $this->imageStadeRepository = $imageStadeRepository;
        $this->logoClubRepository = $logoClubRepository;
    }

    public function scrapp()
    {
        $process = new Process(['python', $this->scrappJoueurs]);
        $process->setTimeout(3600);
        $process->run();

        if (!$process->isSuccessful()) {
            throw new ProcessFailedException($process);
        }

        $logFile = trim(preg_replace('/\s\s+/', ' ', $process->getOutput()));

        return [$logFile];
    }

    public function saveClubScrapp()
    {
        $logger = new LogService($this->logDir, "save_clubs");

        //  Récupération des informations dans le json stockant les clubs récupérés via transfermarkt
        $clubsData = file_get_contents($this->clubsJson);
        $clubs = json_decode($clubsData, true);

        //  Traitement de chaque club présent dans le json
        foreach ($clubs as $clubArray) {
            //  Récupération du club déjà présent dans la base si il est déjà présent
            $clubInDb = $this->clubRepository->findOneBy(["id_transfermarkt" => intval($clubArray["id_transfermarkt"]) ?: null]);
            //  Si le club n'est pas déjà dans la base et que le club qu'on traite a un nom, on créé un nouveau club
            if (!$clubInDb && $clubArray["nom"]) {

                $club = new Club();

                $club->setNom($clubArray["nom"] ?: null);

                $dateCreation = new DateTime($clubArray["creation"]);
                $club->setDateCreation($dateCreation ?: null);

                $club->setIdTransfermarkt(intval($clubArray["id_transfermarkt"]) ?: null);

                $club->setSiteWeb($clubArray["site"] ?: null);

                foreach ($clubArray["couleurs"] as $couleur_hexa) {
                    //  Suppression du '#' dans le code hexa scrappé
                    $couleur_hexa = str_replace("#", "", $couleur_hexa);

                    //  On regarde si le code hexa de la couleur est conforme, çàd 6 caractères (ou moins) et ne correspond pas à un string vide
                    if (strlen($couleur_hexa) <= 6 && $couleur_hexa) {
                        //  On regarde si la couleur n'est pas déjà présente dans les couleurs du club
                        $searchCouleur = $club->getCouleurs()->filter(function (CouleurClub $couleurClub) use ($couleur_hexa) {
                            return $couleurClub->getHexa() === $couleur_hexa;
                        })->getValues();

                        // Si la couleur n'est pas déjà associé au club, on l'associe
                        if (empty($searchCouleur)) {
                            //  Récupération de la couleur si code hexa déjà dans la base sinon on le créer
                            $couleur = $this->couleurClubRepository->findOneBy(["hexa" => $couleur_hexa ?: null]) ?: new CouleurClub($couleur_hexa);
                            $club->addCouleur($couleur);
                        }
                    } else {
                        if ($couleur_hexa) {
                            $logger->warning("Le code hexa {$couleur_hexa} dépasse les 6 caractères.");
                        }
                    }
                }

                foreach ($clubArray["logos"] as $logo) {
                    //  Récupération du LogoClub si un déjà existant pour ce lien
                    $logoClub = $this->logoClubRepository->findOneBy(["lien" => $logo]);

                    $searchLogo = [];
                    //  Si aucun logo correspondant création d'un nouveau sinon on cherche si ce dernier est déjà associé à ce club
                    if (!$logoClub) {
                        $logoClub = new LogoClub($logo);
                    } else {
                        $searchLogo = $club->getLogos()->filter(function (LogoClub $lc) use ($logoClub) {
                            return $lc->getId() === $logoClub->getId();
                        })->getValues();
                    }

                    //  S'il s'agit d'un nouveau logo ou que celui-ci n'était pas lié à ce club, on le lie à ce club
                    if (!$logoClub->getId() || empty($searchLogo)) {
                        $club->addLogo($logoClub);
                    }
                }

                $pays = null;
                if (!$clubArray["pays"]) {
                    $logger->warning("Aucun pays dans le json associé pour le club : {$clubArray["nom"]}");
                } else {
                    //  Récupération du pays correspondant au string scrappé
                    $pays = $this->paysRepository->findOneBy(["nom_fr" => $clubArray["pays"]]);
                    //  Log afin de savoir quel club ne sera associé à aucun pays pour le faire à la main
                    if (!$pays || !$pays instanceof Pays) {
                        $logger->warning("Aucun pays n'a été associé dans la base au pays : '{$clubArray["pays"]}' pour le club : '{$clubArray["nom"]}'");
                    } else {
                        $club->setPays($pays);
                    }
                }
            } else {
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
                            $nouveauStade->setCapacite(intval($stadeArray["capacite"]) ?: null);
                            $nouveauStade->setAnneeConstruction($anneeConstruction ?: null);
                            //  Utilisation du même pays que le stade
                            $nouveauStade->setPays($pays);
                        }
                        $stade = $nouveauStade;
                    }

                    foreach ($stadeArray["images"] as $img) {

                        //  Récupération de l'ImageStade si un déjà existant pour ce lien
                        $imageStade = $this->imageStadeRepository->findOneBy(["lien"=>$img]);

                        $searchImage = [];
                        //  Si cette image n'existe pas encore, on la créé sinon on regarde si elle est liée à ce stade
                        if (!$imageStade) {
                            $imageStade = new ImageStade();
                            $imageStade->setLien($img);
                        } else {
                            $searchImage = $stade->getImages()->filter(function(ImageStade $i) use ($imageStade) {
                                return $i->getId() === $imageStade->getId();
                            })->getValues();
                        }

                        //  Si l'image n'existait pas encore ou qu'elle n'était pas liée à ce stade, on les lie
                        if (!$imageStade->getId() || empty($searchImage)) {
                            $stade->addImage($imageStade);
                        }
                    }

                    $club->setStade($stade);
                }

                $this->clubRepository->add($club, true);
                $logger->info("Le club {$club->getNom()} a correctement été ". $club->getId() ? "modifié" : "ajouté"." !");
            }
        }

        return $logger->getCheminFichierLog();
    }

    public function saveJoueursScrapp()
    {
        $logger = new LogService($this->logDir, "save_joueurs");

        //  Récupération des informations dans le json stockant les joueurs récupérés via transfermarkt
        $joueursJson = file_get_contents($this->joueursJson);
        $joueurs = json_decode($joueursJson, true);

        //  Traitement de chaque joueur présent dans le json
        foreach ($joueurs as $joueurArray) {
            //  Récupération du joueur déjà présent dans la base si il est déjà présent
            $joueurInDb = $this->joueurRepository->findOneBy(["id_transfermarkt" => intval($joueurArray["id_transfermarkt"]) ?: null]);

            //  Si le joueur n'est pas déjà dans la base et que le joueur qu'on traite a un nom, on créé un nouveau joueur
            if (!$joueurInDb && $joueurArray["nom"]) {

                $joueur = new Joueur();
                $joueur->setIdTransfermarkt(intval($joueurArray["id_transfermarkt"]) ?: null);
                $informationsPerso = new InformationsPersonelles();
                $informationsPerso->setNom($joueurArray["nom"]);
                $informationsPerso->setPrenom($joueurArray["prenom"] ?: null);
                $informationsPerso->setNomComplet($joueurArray["nom_complet"] ?: null);
                $dateNaissance = new DateTime($joueurArray["date_naissance"]);
                $informationsPerso->setDateNaissance($dateNaissance ?: null);
                $informationsPerso->setEquipementier($joueurArray["equipementier"] ?: null);
                $informationsPerso->setMeilleurPied($joueurArray["pied"]);
                $informationsPerso->setTaille(intval($joueurArray["taille"]) ?: null);
                foreach ($joueurArray["pays"] as $nationnalite) {
                    if ($nationnalite) {
                        //  Récupération du pays correspondant au string scrappé
                        $pays = $this->paysRepository->findOneBy(["nom_fr" => $nationnalite]);
                        //  Log afin de savoir quel club ne sera associé à aucun pays pour le faire à la main
                        if (!$pays or !$pays instanceof Pays) {
                            $logger->warning("Aucun pays n'a été associé dans la base au pays : '{$nationnalite}' pour le joueur : '{$informationsPerso->getNomComplet()}'");
                        } else {
                            $informationsPerso->addNationnalite($pays);
                        }
                    }
                }
                $joueur->setInformationsPersonnelles($informationsPerso);

            } else {
                $joueur = $joueurInDb;
            }

            if ($joueur) {
                $postes = $joueur->getPostes();
                foreach ($joueurArray["positions_principales"] as $postePrinc) {
                    //  Vérification que le poste que l'on veut sauvegarder existe dans la base
                    $poste = $this->posteRepository->findOneBy(["id_transfermarkt" => intval($postePrinc)]);
                    //  S'il existe
                    if ($poste && $poste instanceof Poste) {
                        //  On regarde si le joueur avait déjà ce poste
                        $pp = $postes->filter(function (PosteJoueur $p) use ($poste) {
                            return $p->getPoste() === $poste;
                        })->getValues();
                        //  S'il avait déjà ce poste
                        if (!empty($pp)) {
                            $posteJoueur = $pp[0];
                            //  Si ce poste n'était pas encore considéré comme un de ces principaux, on le fait
                            if (!$posteJoueur->isPrincipal()) {
                                $posteJoueur->setPrincipal(true);
                            }
                        }
                        //  Si le joueur n'avait pas encore ce poste, on le créé (en principal via le constructeur)
                        else {
                            $posteJoueur = new PosteJoueur(true);
                            $posteJoueur->setPoste($poste);
                        }

                        $joueur->addPoste($posteJoueur);

                    }
                    //  Si le poste n'existe pas dans la base on le log afin de permettre de le créer si nécessaire
                    else {
                        $logger->warning("Aucun poste ne correspond à l'id transfermarkt '{$postePrinc}' dans la base de donnée");
                    }
                }

                $postes = $joueur->getPostes();
                foreach ($joueurArray["positions_secondaires"] as $posteSec) {
                    //  Vérification que le poste que l'on veut sauvegarder existe dans la base
                    $poste = $this->posteRepository->findOneBy(["id_transfermarkt" => intval($posteSec)]);
                    //  S'il existe
                    if ($poste && $poste instanceof Poste) {
                        //  On regarde si le joueur l'avait déjà
                        $pp = $postes->filter(function (PosteJoueur $p) use ($poste) {
                            return $p->getPoste() === $poste;
                        })->getValues();
                        //  Si le joueur l'avait déjà
                        if (!empty($pp)) {
                            $posteJoueur = $pp[0];
                            //  Si ce poste était considéré comme étant un de ces principaux, on lui enlève ce "statut" de poste principal
                            if ($posteJoueur->isPrincipal()) {
                                $posteJoueur->setPrincipal(false);
                            }
                        }
                        //  Si le joueur n'avait pas encore ce poste, on le créé (en non-principal via le constructeur)
                        else {
                            $posteJoueur = new PosteJoueur(false);
                            $posteJoueur->setPoste($poste);
                        }

                        $joueur->addPoste($posteJoueur);

                    }
                    //  Si le poste n'existe pas dans la base on le log afin de permettre de le créer si nécessaire
                    else {
                        $logger->warning("Aucun poste ne correspond à l'id transfermarkt '{$posteSec}' dans la base de donnée");
                    }
                }

                $contrats = $joueur->getContrats();
                foreach ($joueurArray["contrats"] as $contratArray) {
                    //  On regarde si le joueur n'a pas déjà un contrat qui correspond à celui qu'on traite
                    // çad: même date de début et même club
                    $searchContrat = $contrats->filter(function (Contrat $c) use ($contratArray) {
                        return $c->getDebut() == new DateTime($contratArray["debut"]) && (!$c->getClub() || $c->getClub()->getIdTransfermarkt() === intval($contratArray["club"]));
                    })->getValues();
                    //  On récupère le club lié au contrat qu'on est en train de traité
                    $club = $this->clubRepository->findOneBy(["id_transfermarkt" => intval($contratArray["club"])]);
                    $contrat = null;

                    if (!$club || !$club instanceof Club) {
                        $club = null;
                    }

                    //  Si un contrat correspond, modification de ce dernier
                    if (!empty($searchContrat)) {
                        $contratCorrespondant = $searchContrat[0];
                        //  On modifie la date de fin (qui peut avoir été modifié via un transfert ou une prolongation)
                        $contratCorrespondant->setFin(new DateTime($contratArray["fin"]) ?: null);

                        $contrat = $contratCorrespondant;
                        $contrat->setClub($club);

                        //  S'il s'agit de son dernier contrat avant sa retraite, on indique que le joueur est retraité
                        if ($contratArray["retraite_fin"]) {
                            $joueur->getInformationsPersonnelles()->setRetraiteJoueur(true);
                        }
                        //  Sinon l'inverse (au cas où le joueur mette fin à sa retraite)
                        else {
                            $joueur->getInformationsPersonnelles()->setRetraiteJoueur(false);
                        }

                        //  Multiple vérifications afin de modifier le type de contrat si nécessaire
                        if ($contrat instanceof Transfert) {
                            if ($contratArray["libre"] && !$contrat->isLibre()) {
                                $contrat->setLibre(true);
                                $contrat->setMontant(null);
                            } elseif ($contratArray["transfert"]) {
                                $contrat->setLibre(false);
                                $contrat->setMontant(intval($contratArray["montant"]) ?: null);
                            } elseif ($contratArray["pret"]) {
                                $joueur->removeContrat($contrat);
                                $contrat = new Pret();
                                if ($club) $contrat->setClub($club);
                                $contrat->setDebut(new DateTime($contratArray["debut"]) ?: null);
                                $contrat->setFin(new DateTime($contratArray["fin"]) ?: null);
                            } elseif ($contratArray["formation"]) {
                                $joueur->removeContrat($contrat);
                                $contrat = new Contrat();
                                if ($club) $contrat->setClub($club);
                                $contrat->setDebut(new DateTime($contratArray["debut"]) ?: null);
                                $contrat->setFin(new DateTime($contratArray["fin"]) ?: null);
                            }
                        }
                        elseif ($contrat instanceof Pret) {
                            if ($contratArray["libre"]) {
                                $joueur->removeContrat($contrat);
                                $contrat = new Transfert();
                                if ($club) $contrat->setClub($club);
                                $contrat->setDebut(new DateTime($contratArray["debut"]) ?: null);
                                $contrat->setFin(new DateTime($contratArray["fin"]) ?: null);
                                $contrat->setLibre(true);
                                $contrat->setMontant(null);
                            } elseif ($contratArray["transfert"]) {
                                $joueur->removeContrat($contrat);
                                $contrat = new Transfert();
                                if ($club) $contrat->setClub($club);
                                $contrat->setDebut(new DateTime($contratArray["debut"]) ?: null);
                                $contrat->setFin(new DateTime($contratArray["fin"]) ?: null);
                                $contrat->setLibre(false);
                                $contrat->setMontant(intval(intval($contratArray["montant"]) ?: null));
                            } elseif ($contratArray["formation"]) {
                                $joueur->removeContrat($contrat);
                                $contrat = new Contrat();
                                if ($club) $contrat->setClub($club);
                                $contrat->setDebut(new DateTime($contratArray["debut"]) ?: null);
                                $contrat->setFin(new DateTime($contratArray["fin"]) ?: null);
                            }
                        }
                        elseif ($contrat instanceof Contrat) {
                            if ($contratArray["libre"]) {
                                $joueur->removeContrat($contrat);
                                $contrat = new Transfert();
                                if ($club) $contrat->setClub($club);
                                $contrat->setDebut(new DateTime($contratArray["debut"]) ?: null);
                                $contrat->setFin(new DateTime($contratArray["fin"]) ?: null);
                                $contrat->setLibre(true);
                                $contrat->setMontant(null);
                            } elseif ($contratArray["transfert"]) {
                                $joueur->removeContrat($contrat);
                                $contrat = new Transfert();
                                if ($club) $contrat->setClub($club);
                                $contrat->setDebut(new DateTime($contratArray["debut"]) ?: null);
                                $contrat->setFin(new DateTime($contratArray["fin"]) ?: null);
                                $contrat->setLibre(false);
                                $contrat->setMontant(intval($contratArray["montant"] ?: null));
                            } elseif ($contratArray["pret"]) {
                                $joueur->removeContrat($contrat);
                                $contrat = new Pret();
                                if ($club) $contrat->setClub($club);
                                $contrat->setDebut(new DateTime($contratArray["debut"]) ?: null);
                                $contrat->setFin(new DateTime($contratArray["fin"]) ?: null);
                            }
                        }
                    }
                    //  Sinon donc nouveau contrat
                    else {
                        //  Création du contrat selon le type de mouvement
                        if ($contratArray["libre"]) {
                            $contrat = new Transfert();
                            if ($club) $contrat->setClub($club);
                            $contrat->setDebut(new DateTime($contratArray["debut"]) ?: null);
                            $contrat->setFin(new DateTime($contratArray["fin"]) ?: null);
                            $contrat->setLibre(true);
                            $contrat->setMontant(null);
                        } elseif ($contratArray["transfert"]) {
                            $contrat = new Transfert();
                            if ($club) $contrat->setClub($club);
                            $contrat->setDebut(new DateTime($contratArray["debut"]) ?: null);
                            $contrat->setFin(new DateTime($contratArray["fin"]) ?: null);
                            $contrat->setLibre(false);
                            $contrat->setMontant(intval($contratArray["montant"] ?: null));
                        } elseif ($contratArray["pret"]) {
                            $contrat = new Pret();
                            if ($club) $contrat->setClub($club);
                            $contrat->setDebut(new DateTime($contratArray["debut"]) ?: null);
                            $contrat->setFin(new DateTime($contratArray["fin"]) ?: null);
                        } elseif ($contratArray["formation"]) {
                            $contrat = new Contrat();
                            if ($club) $contrat->setClub($club);
                            $contrat->setDebut(new DateTime($contratArray["debut"]) ?: null);
                            $contrat->setFin(new DateTime($contratArray["fin"]) ?: null);
                        }
                    }
                    //  Si le club pour ce contrat n'est pas enregistré dans la base, donc log pour l'indiquer
                    if(!$club) {
                        $logger->warning("Aucun club ne correspond à l'id transfermarkt '{$contratArray["club"]}' dans la base de donnée pour le contrat du joueur : '{$joueur->getInformationsPersonnelles()->getNomComplet()}' pour son contrat allant du '{$contratArray["debut"]}' au {$contratArray["fin"]}'");
                    }

                    if ($contrat && !$contrat->getId()) {
                        $joueur->addContrat($contrat);
                    }
                }

                $this->joueurRepository->add($joueur, true);
                $logger->info("Le joueur {$joueur->getInformationsPersonnelles()->getNom()} {$joueur->getInformationsPersonnelles()->getPrenom()} a correctement été ". $joueur->getId() ? "modifié" : "ajouté"." !");
            }
        }

        return $logger->getCheminFichierLog();
    }

}
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
    private $scrappMatchsLigue1;
    private $clubsJson;
    private $joueursJson;
    private $matchsLigue1Json;
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
        $this->scrappMatchsLigue1 = "scrapp/scrapp_matchs.py";
        $this->clubsJson = "scrapp/donnees/clubs.json";
        $this->joueursJson = "scrapp/donnees/joueurs.json";
        $this->matchsLigue1Json = "scrapp/donnees/matchs.json";
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

    public function scrappJoueursEtClubs()
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

        //  R??cup??ration des informations dans le json stockant les clubs r??cup??r??s via transfermarkt
        $clubsData = file_get_contents($this->clubsJson);
        $clubs = json_decode($clubsData, true);

        //  Traitement de chaque club pr??sent dans le json
        foreach ($clubs as $clubArray) {
            //  R??cup??ration du club d??j?? pr??sent dans la base si il est d??j?? pr??sent
            $clubInDb = $this->clubRepository->findOneBy(["id_transfermarkt" => intval($clubArray["id_transfermarkt"]) ?: null]);
            //  Si le club n'est pas d??j?? dans la base et que le club qu'on traite a un nom, on cr???? un nouveau club
            if (!$clubInDb && $clubArray["nom"]) {

                $club = new Club();

                $club->setNom($clubArray["nom"] ?: null);

                $dateCreation = new DateTime($clubArray["creation"]);
                $club->setDateCreation($dateCreation ?: null);

                $club->setIdTransfermarkt(intval($clubArray["id_transfermarkt"]) ?: null);

                $club->setSiteWeb($clubArray["site"] ?: null);

                foreach ($clubArray["couleurs"] as $couleur_hexa) {
                    //  Suppression du '#' dans le code hexa scrapp??
                    $couleur_hexa = str_replace("#", "", $couleur_hexa);

                    //  On regarde si le code hexa de la couleur est conforme, ????d 6 caract??res (ou moins) et ne correspond pas ?? un string vide
                    if (strlen($couleur_hexa) <= 6 && $couleur_hexa) {
                        //  On regarde si la couleur n'est pas d??j?? pr??sente dans les couleurs du club
                        $searchCouleur = $club->getCouleurs()->filter(function (CouleurClub $couleurClub) use ($couleur_hexa) {
                            return $couleurClub->getHexa() === $couleur_hexa;
                        })->getValues();

                        // Si la couleur n'est pas d??j?? associ?? au club, on l'associe
                        if (empty($searchCouleur)) {
                            //  R??cup??ration de la couleur si code hexa d??j?? dans la base sinon on le cr??er
                            $couleur = $this->couleurClubRepository->findOneBy(["hexa" => $couleur_hexa ?: null]) ?: new CouleurClub($couleur_hexa);
                            $club->addCouleur($couleur);
                        }
                    } else {
                        if ($couleur_hexa) {
                            $logger->warning("Le code hexa {$couleur_hexa} d??passe les 6 caract??res.");
                        }
                    }
                }

                foreach ($clubArray["logos"] as $logo) {
                    //  R??cup??ration du LogoClub si un d??j?? existant pour ce lien
                    $logoClub = $this->logoClubRepository->findOneBy(["lien" => $logo]);

                    $searchLogo = [];
                    //  Si aucun logo correspondant cr??ation d'un nouveau sinon on cherche si ce dernier est d??j?? associ?? ?? ce club
                    if (!$logoClub) {
                        $logoClub = new LogoClub($logo);
                    } else {
                        $searchLogo = $club->getLogos()->filter(function (LogoClub $lc) use ($logoClub) {
                            return $lc->getId() === $logoClub->getId();
                        })->getValues();
                    }

                    //  S'il s'agit d'un nouveau logo ou que celui-ci n'??tait pas li?? ?? ce club, on le lie ?? ce club
                    if (!$logoClub->getId() || empty($searchLogo)) {
                        $club->addLogo($logoClub);
                    }
                }

                $pays = null;
                if (!$clubArray["pays"]) {
                    $logger->warning("Aucun pays dans le json associ?? pour le club : {$clubArray["nom"]}");
                } else {
                    //  R??cup??ration du pays correspondant au string scrapp??
                    $pays = $this->paysRepository->findOneBy(["nom_fr" => $clubArray["pays"]]);
                    //  Log afin de savoir quel club ne sera associ?? ?? aucun pays pour le faire ?? la main
                    if (!$pays || !$pays instanceof Pays) {
                        $logger->warning("Aucun pays n'a ??t?? associ?? dans la base au pays : '{$clubArray["pays"]}' pour le club : '{$clubArray["nom"]}'");
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
                //  Si le stade scrapp?? a un nom
                if ($stadeArray["nom"]) {
                    //  R??cup??ration du stade d??j?? associ?? au club
                    $stade = $club->getStade();

                    //  Si le club n'a pas de stade ou que ce dernier est diff??rent de celui scrapp??, on lui associe un stade
                    if ((!$stade) || ($stade->getNom() != $stadeArray["nom"])) {
                        //  Recherche dans la base si un stade est d??j?? existant pour le nom et l'ann??e de construction scrapp??s
                        $nouveauStade = $this->stadeRepository->findOneBy(["nom" => $stadeArray["nom"], "annee_construction" => $anneeConstruction]);
                        //  Si aucun stade ne correspond dans la base, on le cr???? avec les infos scrapp??es
                        if (!$nouveauStade) {
                            $nouveauStade = new Stade();
                            $nouveauStade->setNom($stadeArray["nom"]);
                            $nouveauStade->setAdresse($stadeArray["adresse"] ?: null);
                            $nouveauStade->setCapacite(intval($stadeArray["capacite"]) ?: null);
                            $nouveauStade->setAnneeConstruction($anneeConstruction ?: null);
                            //  Utilisation du m??me pays que le stade
                            $nouveauStade->setPays($pays);
                        }
                        $stade = $nouveauStade;
                    }

                    foreach ($stadeArray["images"] as $img) {

                        //  R??cup??ration de l'ImageStade si un d??j?? existant pour ce lien
                        $imageStade = $this->imageStadeRepository->findOneBy(["lien"=>$img]);

                        $searchImage = [];
                        //  Si cette image n'existe pas encore, on la cr???? sinon on regarde si elle est li??e ?? ce stade
                        if (!$imageStade) {
                            $imageStade = new ImageStade();
                            $imageStade->setLien($img);
                        } else {
                            $searchImage = $stade->getImages()->filter(function(ImageStade $i) use ($imageStade) {
                                return $i->getId() === $imageStade->getId();
                            })->getValues();
                        }

                        //  Si l'image n'existait pas encore ou qu'elle n'??tait pas li??e ?? ce stade, on les lie
                        if (!$imageStade->getId() || empty($searchImage)) {
                            $stade->addImage($imageStade);
                        }
                    }

                    $club->setStade($stade);
                }

                $this->clubRepository->add($club, true);
                $logger->info("Le club {$club->getNom()} a correctement ??t?? ". $club->getId() ? "modifi??" : "ajout??"." !");
            }
        }

        return $logger->getCheminFichierLog();
    }

    public function saveJoueursScrapp()
    {
        $logger = new LogService($this->logDir, "save_joueurs");

        //  R??cup??ration des informations dans le json stockant les joueurs r??cup??r??s via transfermarkt
        $joueursJson = file_get_contents($this->joueursJson);
        $joueurs = json_decode($joueursJson, true);

        //  Traitement de chaque joueur pr??sent dans le json
        foreach ($joueurs as $joueurArray) {
            //  R??cup??ration du joueur d??j?? pr??sent dans la base si il est d??j?? pr??sent
            $joueurInDb = $this->joueurRepository->findOneBy(["id_transfermarkt" => intval($joueurArray["id_transfermarkt"]) ?: null]);

            //  Si le joueur n'est pas d??j?? dans la base et que le joueur qu'on traite a un nom, on cr???? un nouveau joueur
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
                        //  R??cup??ration du pays correspondant au string scrapp??
                        $pays = $this->paysRepository->findOneBy(["nom_fr" => $nationnalite]);
                        //  Log afin de savoir quel club ne sera associ?? ?? aucun pays pour le faire ?? la main
                        if (!$pays or !$pays instanceof Pays) {
                            $logger->warning("Aucun pays n'a ??t?? associ?? dans la base au pays : '{$nationnalite}' pour le joueur : '{$informationsPerso->getNomComplet()}'");
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
                    //  V??rification que le poste que l'on veut sauvegarder existe dans la base
                    $poste = $this->posteRepository->findOneBy(["id_transfermarkt" => intval($postePrinc)]);
                    //  S'il existe
                    if ($poste && $poste instanceof Poste) {
                        //  On regarde si le joueur avait d??j?? ce poste
                        $pp = $postes->filter(function (PosteJoueur $p) use ($poste) {
                            return $p->getPoste() === $poste;
                        })->getValues();
                        //  S'il avait d??j?? ce poste
                        if (!empty($pp)) {
                            $posteJoueur = $pp[0];
                            //  Si ce poste n'??tait pas encore consid??r?? comme un de ces principaux, on le fait
                            if (!$posteJoueur->isPrincipal()) {
                                $posteJoueur->setPrincipal(true);
                            }
                        }
                        //  Si le joueur n'avait pas encore ce poste, on le cr???? (en principal via le constructeur)
                        else {
                            $posteJoueur = new PosteJoueur(true);
                            $posteJoueur->setPoste($poste);
                        }

                        $joueur->addPoste($posteJoueur);

                    }
                    //  Si le poste n'existe pas dans la base on le log afin de permettre de le cr??er si n??cessaire
                    else {
                        $logger->warning("Aucun poste ne correspond ?? l'id transfermarkt '{$postePrinc}' dans la base de donn??e");
                    }
                }

                $postes = $joueur->getPostes();
                foreach ($joueurArray["positions_secondaires"] as $posteSec) {
                    //  V??rification que le poste que l'on veut sauvegarder existe dans la base
                    $poste = $this->posteRepository->findOneBy(["id_transfermarkt" => intval($posteSec)]);
                    //  S'il existe
                    if ($poste && $poste instanceof Poste) {
                        //  On regarde si le joueur l'avait d??j??
                        $pp = $postes->filter(function (PosteJoueur $p) use ($poste) {
                            return $p->getPoste() === $poste;
                        })->getValues();
                        //  Si le joueur l'avait d??j??
                        if (!empty($pp)) {
                            $posteJoueur = $pp[0];
                            //  Si ce poste ??tait consid??r?? comme ??tant un de ces principaux, on lui enl??ve ce "statut" de poste principal
                            if ($posteJoueur->isPrincipal()) {
                                $posteJoueur->setPrincipal(false);
                            }
                        }
                        //  Si le joueur n'avait pas encore ce poste, on le cr???? (en non-principal via le constructeur)
                        else {
                            $posteJoueur = new PosteJoueur(false);
                            $posteJoueur->setPoste($poste);
                        }

                        $joueur->addPoste($posteJoueur);

                    }
                    //  Si le poste n'existe pas dans la base on le log afin de permettre de le cr??er si n??cessaire
                    else {
                        $logger->warning("Aucun poste ne correspond ?? l'id transfermarkt '{$posteSec}' dans la base de donn??e");
                    }
                }

                $contrats = $joueur->getContrats();
                foreach ($joueurArray["contrats"] as $contratArray) {
                    //  On regarde si le joueur n'a pas d??j?? un contrat qui correspond ?? celui qu'on traite
                    // ??ad: m??me date de d??but et m??me club
                    $searchContrat = $contrats->filter(function (Contrat $c) use ($contratArray) {
                        return $c->getDebut() == new DateTime($contratArray["debut"]) && (!$c->getClub() || $c->getClub()->getIdTransfermarkt() === intval($contratArray["club"]));
                    })->getValues();
                    //  On r??cup??re le club li?? au contrat qu'on est en train de trait??
                    $club = $this->clubRepository->findOneBy(["id_transfermarkt" => intval($contratArray["club"])]);
                    $contrat = null;

                    if (!$club || !$club instanceof Club) {
                        $club = null;
                    }

                    //  Si un contrat correspond, modification de ce dernier
                    if (!empty($searchContrat)) {
                        $contratCorrespondant = $searchContrat[0];
                        //  On modifie la date de fin (qui peut avoir ??t?? modifi?? via un transfert ou une prolongation)
                        $contratCorrespondant->setFin(new DateTime($contratArray["fin"]) ?: null);

                        $contrat = $contratCorrespondant;
                        $contrat->setClub($club);

                        //  S'il s'agit de son dernier contrat avant sa retraite, on indique que le joueur est retrait??
                        if ($contratArray["retraite_fin"]) {
                            $joueur->getInformationsPersonnelles()->setRetraiteJoueur(true);
                        }
                        //  Sinon l'inverse (au cas o?? le joueur mette fin ?? sa retraite)
                        else {
                            $joueur->getInformationsPersonnelles()->setRetraiteJoueur(false);
                        }

                        //  Multiple v??rifications afin de modifier le type de contrat si n??cessaire
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
                        //  Cr??ation du contrat selon le type de mouvement
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
                    //  Si le club pour ce contrat n'est pas enregistr?? dans la base, donc log pour l'indiquer
                    if(!$club) {
                        $logger->warning("Aucun club ne correspond ?? l'id transfermarkt '{$contratArray["club"]}' dans la base de donn??e pour le contrat du joueur : '{$joueur->getInformationsPersonnelles()->getNomComplet()}' pour son contrat allant du '{$contratArray["debut"]}' au {$contratArray["fin"]}'");
                    }

                    if ($contrat && !$contrat->getId()) {
                        $joueur->addContrat($contrat);
                    }
                }

                $this->joueurRepository->add($joueur, true);
                $logger->info("Le joueur {$joueur->getInformationsPersonnelles()->getNom()} {$joueur->getInformationsPersonnelles()->getPrenom()} a correctement ??t?? ". $joueur->getId() ? "modifi??" : "ajout??"." !");
            }
        }

        return $logger->getCheminFichierLog();
    }

    public function scrappMatchsLigue1() {
        $process = new Process(['python', $this->scrappMatchsLigue1]);
        $process->setTimeout(3600);
        $process->run();

        if (!$process->isSuccessful()) {
            throw new ProcessFailedException($process);
        }

        $logFile = trim(preg_replace('/\s\s+/', ' ', $process->getOutput()));

        return [$logFile];
    }

}
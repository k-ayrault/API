<?php

namespace App\Entity;

use App\Repository\TitulaireRepository;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: TitulaireRepository::class)]
class Titulaire
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: 'integer')]
    private $id;

    #[ORM\ManyToOne(targetEntity: Poste::class)]
    private $poste;

    #[ORM\ManyToOne(targetEntity: Joueur::class)]
    private $joueur;

    #[ORM\ManyToOne(targetEntity: RencontreLigue1::class, inversedBy: 'titulaires_domicile')]
    private $id_rencontre_ligue_1;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getPoste(): ?Poste
    {
        return $this->poste;
    }

    public function setPoste(?Poste $poste): self
    {
        $this->poste = $poste;

        return $this;
    }

    public function getJoueur(): ?Joueur
    {
        return $this->joueur;
    }

    public function setJoueur(?Joueur $joueur): self
    {
        $this->joueur = $joueur;

        return $this;
    }

    public function getIdRencontreLigue1(): ?RencontreLigue1
    {
        return $this->id_rencontre_ligue_1;
    }

    public function setIdRencontreLigue1(?RencontreLigue1 $id_rencontre_ligue_1): self
    {
        $this->id_rencontre_ligue_1 = $id_rencontre_ligue_1;

        return $this;
    }
}

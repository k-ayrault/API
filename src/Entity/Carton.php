<?php

namespace App\Entity;

use App\Repository\CartonRepository;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: CartonRepository::class)]
class Carton extends Evenement
{

    #[ORM\Column(type: 'boolean')]
    private $jaune;

    #[ORM\Column(type: 'boolean')]
    private $rouge;

    public function isJaune(): ?bool
    {
        return $this->jaune;
    }

    public function setJaune(bool $jaune): self
    {
        $this->jaune = $jaune;

        return $this;
    }

    public function isRouge(): ?bool
    {
        return $this->rouge;
    }

    public function setRouge(bool $rouge): self
    {
        $this->rouge = $rouge;

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
}

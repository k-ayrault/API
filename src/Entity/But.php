<?php

namespace App\Entity;

use App\Repository\ButRepository;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: ButRepository::class)]
class But extends Evenement
{
    #[ORM\Column(type: 'boolean')]
    private $csc;

    #[ORM\Column(type: 'boolean')]
    private $penalty;

    #[ORM\ManyToOne(targetEntity: Joueur::class)]
    private $buteur;

    #[ORM\ManyToOne(targetEntity: Joueur::class)]
    private $passeur;

    public function isCsc(): ?bool
    {
        return $this->csc;
    }

    public function setCsc(bool $csc): self
    {
        $this->csc = $csc;

        return $this;
    }

    public function isPenalty(): ?bool
    {
        return $this->penalty;
    }

    public function setPenalty(bool $penalty): self
    {
        $this->penalty = $penalty;

        return $this;
    }

    public function getButeur(): ?Joueur
    {
        return $this->buteur;
    }

    public function setButeur(?Joueur $buteur): self
    {
        $this->buteur = $buteur;

        return $this;
    }

    public function getPasseur(): ?Joueur
    {
        return $this->passeur;
    }

    public function setPasseur(?Joueur $passeur): self
    {
        $this->passeur = $passeur;

        return $this;
    }
}

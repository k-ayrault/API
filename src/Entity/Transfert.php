<?php

namespace App\Entity;

use App\Repository\TransfertRepository;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: TransfertRepository::class)]
class Transfert extends Contrat
{

    #[ORM\Column(type: 'boolean')]
    private $club_formateur;

    #[ORM\Column(type: 'boolean')]
    private $libre;

    #[ORM\Column(type: 'integer', nullable: true)]
    private $montant;
    
    public function isClubFormateur(): ?bool
    {
        return $this->club_formateur;
    }

    public function setClubFormateur(bool $club_formateur): self
    {
        $this->club_formateur = $club_formateur;

        return $this;
    }

    public function isLibre(): ?bool
    {
        return $this->libre;
    }

    public function setLibre(bool $libre): self
    {
        $this->libre = $libre;

        return $this;
    } 

    public function getMontant(): ?int
    {
        return $this->montant;
    }

    public function setMontant(?int $montant): self
    {
        $this->montant = $montant;

        return $this;
    }
}

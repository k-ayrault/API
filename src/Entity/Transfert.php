<?php

namespace App\Entity;

use App\Repository\TransfertRepository;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: TransfertRepository::class)]
class Transfert extends Contrat
{

    #[ORM\Column(type: 'boolean')]
    private $libre;

    #[ORM\Column(type: 'integer', nullable: true)]
    private $montant;

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

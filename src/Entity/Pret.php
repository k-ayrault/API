<?php

namespace App\Entity;

use App\Repository\PretRepository;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: PretRepository::class)]
class Pret extends Contrat
{

    #[ORM\Column(type: 'boolean')]
    private $option_achat;

    #[ORM\Column(type: 'integer', nullable: true)]
    private $montant_option;

    public function __construct()
    {
        $this->setOptionAchat(false);
    }

    public function isOptionAchat(): ?bool
    {
        return $this->option_achat;
    }

    public function setOptionAchat(bool $option_achat): self
    {
        $this->option_achat = $option_achat;

        return $this;
    }

    public function getMontantOption(): ?int
    {
        return $this->montant_option;
    }

    public function setMontantOption(?int $montant_option): self
    {
        $this->montant_option = $montant_option;

        return $this;
    }
}

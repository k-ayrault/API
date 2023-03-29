<?php

namespace App\Entity;

use App\Repository\ScoreRepository;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: ScoreRepository::class)]
class Score
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: 'integer')]
    private $id;

    #[ORM\Column(type: 'integer')]
    private $buts_domicile;

    #[ORM\Column(type: 'integer')]
    private $buts_exterieur;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getButsDomicile(): ?int
    {
        return $this->buts_domicile;
    }

    public function setButsDomicile(int $buts_domicile): self
    {
        $this->buts_domicile = $buts_domicile;

        return $this;
    }

    public function getButsExterieur(): ?int
    {
        return $this->buts_exterieur;
    }

    public function setButsExterieur(int $buts_exterieur): self
    {
        $this->buts_exterieur = $buts_exterieur;

        return $this;
    }
}

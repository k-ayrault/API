<?php

namespace App\Entity;

use App\Repository\ArbitreRepository;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: ArbitreRepository::class)]
class Arbitre
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: 'integer')]
    private $id;

    #[ORM\OneToOne(targetEntity: InformationsPersonelles::class, cascade: ['persist', 'remove'])]
    private $informations_personelles;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getInformationsPersonelles(): ?InformationsPersonelles
    {
        return $this->informations_personelles;
    }

    public function setInformationsPersonelles(?InformationsPersonelles $informations_personelles): self
    {
        $this->informations_personelles = $informations_personelles;

        return $this;
    }
}

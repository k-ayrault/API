<?php

namespace App\Entity;

use App\Repository\LogoClubRepository;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Annotation\Groups;

#[ORM\Entity(repositoryClass: LogoClubRepository::class)]
class LogoClub
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: 'integer')]
    #[Groups(['read.Club'])]
    private $id;

    #[ORM\Column(type: 'string', length: 255)]
    #[Groups(['read.Club', 'persist.Club'])]
    private $lien;

    #[ORM\Column(type: 'boolean')]
    #[Groups(['read.Club', 'persist.Club'])]
    private $principal;

    #[ORM\ManyToOne(targetEntity: Club::class, inversedBy: 'logos', cascade: ['persist'])]
    private $club;

    public function __construct(string $lien)
    {
        $this->setLien($lien);
    }

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getLien(): ?string
    {
        return $this->lien;
    }

    public function setLien(string $lien): self
    {
        $this->lien = $lien;

        return $this;
    }

    public function getClub(): ?Club
    {
        return $this->club;
    }

    public function setClub(?Club $club): self
    {
        $this->club = $club;

        return $this;
    }

    public function isPrincipal(): ?bool
    {
        return $this->principal;
    }

    public function setPrincipal(bool $principal): self
    {
        $this->principal = $principal;

        return $this;
    } 
}

<?php

namespace App\Entity;

use App\Repository\PosteRepository;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Annotation\Groups;

#[ORM\Entity(repositoryClass: PosteRepository::class)]
class Poste
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: 'integer')]
    #[Groups(['persist.Joueur', 'read.Joueur', "get.Poste"])]
    private $id;

    #[ORM\Column(type: 'string', length: 10, nullable: true)]
    #[Groups(["persist.Position", "get.Poste"])]
    private $abreviation;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    #[Groups(["persist.Position", "get.Poste"])]
    private $nom;

    #[ORM\Column(type: 'integer', nullable: true)]
    #[Groups(["persist.Position", "get.Poste"])]
    private $id_transfermarkt;

    #[ORM\ManyToOne(targetEntity: Position::class, inversedBy: 'postes')]
    #[Groups(["get.Poste"])]
    private $position;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getAbreviation(): ?string
    {
        return $this->abreviation;
    }

    public function setAbreviation(?string $abreviation): self
    {
        $this->abreviation = $abreviation;

        return $this;
    }

    public function getNom(): ?string
    {
        return $this->nom;
    }

    public function setNom(?string $nom): self
    {
        $this->nom = $nom;

        return $this;
    }

    public function getIdTransfermarkt(): ?int
    {
        return $this->id_transfermarkt;
    }

    public function setIdTransfermarkt(?int $id_transfermarkt): self
    {
        $this->id_transfermarkt = $id_transfermarkt;

        return $this;
    }

    public function getPosition(): ?Position
    {
        return $this->position;
    }

    public function setPosition(?Position $position): self
    {
        $this->position = $position;

        return $this;
    }
}

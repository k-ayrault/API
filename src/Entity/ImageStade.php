<?php

namespace App\Entity;

use App\Repository\ImageStadeRepository;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Annotation\Groups;

#[ORM\Entity(repositoryClass: ImageStadeRepository::class)]
class ImageStade
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: 'integer')]
    #[Groups(['read.Club'])]
    private $id;

    #[ORM\Column(type: 'string', length: 255)]
    #[Groups(['read.Club'])]
    private $lien;

    #[ORM\ManyToOne(targetEntity: Stade::class, inversedBy: 'images', cascade: ['persist'])]
    private $stade;

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

    public function getStade(): ?Stade
    {
        return $this->stade;
    }

    public function setStade(?Stade $stade): self
    {
        $this->stade = $stade;

        return $this;
    }
}

<?php

namespace App\Entity;

use App\Repository\PosteJoueurRepository;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Annotation\Groups;

#[ORM\Entity(repositoryClass: PosteJoueurRepository::class)]
class PosteJoueur
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: 'integer')]
    private $id;

    #[ORM\Column(type: 'boolean')]
    #[Groups(['persist.Joueur', 'read.Joueur'])]
    private $principal;

    #[ORM\ManyToOne(targetEntity: Poste::class, cascade: ["persist"])]
    #[Groups(['persist.Joueur', 'read.Joueur'])]
    private $poste;

    #[ORM\ManyToOne(targetEntity: Joueur::class, inversedBy: 'postes')]
    private $joueur;

    public function __construct(bool $principal)
    {
        $this->setPrincipal($principal);
    }

    public function getId(): ?int
    {
        return $this->id;
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

    public function getPoste(): ?Poste
    {
        return $this->poste;
    }

    public function setPoste(?Poste $poste): self
    {
        $this->poste = $poste;

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

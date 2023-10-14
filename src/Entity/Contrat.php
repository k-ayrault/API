<?php

namespace App\Entity;

use App\Repository\ContratRepository;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Annotation\Groups;

#[ORM\Entity(repositoryClass: ContratRepository::class)]
#[ORM\InheritanceType('SINGLE_TABLE')]
#[ORM\DiscriminatorColumn(name: 'type', type: 'string')]
#[ORM\DiscriminatorMap(['contrat' => 'Contrat', 'pret' => 'Pret', 'transfert' => 'Transfert'])]
class Contrat
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: 'integer')]
    private $id;

    #[ORM\Column(type: 'date', nullable: true)]
    #[Groups(['persist.Joueur', 'read.Joueur'])]
    private $debut;

    #[ORM\Column(type: 'date', nullable: true)]
    #[Groups(['persist.Joueur', 'read.Joueur'])]
    private $fin;

    #[ORM\ManyToOne(targetEntity: Club::class, cascade: ['persist', 'remove'], fetch: 'EAGER')]
    #[Groups(['persist.Joueur', 'read.Joueur'])]
    private $club;

    #[ORM\ManyToOne(targetEntity: Joueur::class, inversedBy: 'contrats', cascade: ['persist', 'remove'])]
    private $joueur;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getDebut(): ?\DateTimeInterface
    {
        return $this->debut;
    }

    public function setDebut(?\DateTimeInterface $debut): self
    {
        $this->debut = $debut;

        return $this;
    }

    public function getFin(): ?\DateTimeInterface
    {
        return $this->fin;
    }

    public function setFin(?\DateTimeInterface $fin): self
    {
        $this->fin = $fin;

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

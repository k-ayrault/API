<?php

namespace App\Entity;

use App\Repository\RemplacementRepository;
use Doctrine\ORM\Mapping as ORM;

/**
 * @ORM\Entity(repositoryClass=RemplacementRepository::class)
 */
class Remplacement extends Evenement
{

    /**
     * @ORM\ManyToOne(targetEntity=Joueur::class)
     */
    private $joueur_entrant;

    /**
     * @ORM\ManyToOne(targetEntity=Joueur::class)
     */
    private $joueur_sortant;

    public function getJoueurEntrant(): ?Joueur
    {
        return $this->joueur_entrant;
    }

    public function setJoueurEntrant(?Joueur $joueur_entrant): self
    {
        $this->joueur_entrant = $joueur_entrant;

        return $this;
    }

    public function getJoueurSortant(): ?Joueur
    {
        return $this->joueur_sortant;
    }

    public function setJoueurSortant(?Joueur $joueur_sortant): self
    {
        $this->joueur_sortant = $joueur_sortant;

        return $this;
    }
}

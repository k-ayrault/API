<?php

namespace App\Entity;

use App\Repository\JoueurRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;

/**
 * @ORM\Entity(repositoryClass=JoueurRepository::class)
 */
class Joueur
{
    /**
     * @ORM\Id
     * @ORM\GeneratedValue
     * @ORM\Column(type="integer")
     */
    private $id;

    /**
     * @ORM\Column(type="integer", nullable=true)
     */
    private $id_transfermarkt;

    /**
     * @ORM\OneToOne(targetEntity=InformationsPersonelles::class, cascade={"persist", "remove"}, fetch="EAGER")
     * @ORM\JoinColumn(nullable=false)
     */
    private $informations_personnelles;

    /**
     * @ORM\OneToMany(targetEntity=PosteJoueur::class, mappedBy="joueur", cascade={"persist", "remove"}, fetch="EAGER")
     */
    private $postes;

    /**
     * @ORM\OneToMany(targetEntity=Contrat::class, mappedBy="joueur", cascade={"persist", "remove"}, fetch="EAGER")
     */
    private $contrats;

    public function __construct()
    {
        $this->postes = new ArrayCollection();
        $this->contrats = new ArrayCollection();
    }

    public function getId(): ?int
    {
        return $this->id;
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

    public function getInformationsPersonnelles(): ?InformationsPersonelles
    {
        return $this->informations_personnelles;
    }

    public function setInformationsPersonnelles(InformationsPersonelles $informations_personnelles): self
    {
        $this->informations_personnelles = $informations_personnelles;

        return $this;
    }

    /**
     * @return Collection<int, PosteJoueur>
     */
    public function getPostes(): Collection
    {
        return $this->postes;
    }

    public function addPoste(PosteJoueur $poste): self
    {
        if (!$this->postes->contains($poste)) {
            $this->postes[] = $poste;
            $poste->setJoueur($this);
        }

        return $this;
    }

    public function removePoste(PosteJoueur $poste): self
    {
        if ($this->postes->removeElement($poste)) {
            // set the owning side to null (unless already changed)
            if ($poste->getJoueur() === $this) {
                $poste->setJoueur(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, Contrat>
     */
    public function getContrats(): Collection
    {
        return $this->contrats;
    }

    public function addContrat(Contrat $contrat): self
    {
        if (!$this->contrats->contains($contrat)) {
            $this->contrats[] = $contrat;
            $contrat->setJoueur($this);
        }

        return $this;
    }

    public function removeContrat(Contrat $contrat): self
    {
        if ($this->contrats->removeElement($contrat)) {
            // set the owning side to null (unless already changed)
            if ($contrat->getJoueur() === $this) {
                $contrat->setJoueur(null);
            }
        }

        return $this;
    }
}

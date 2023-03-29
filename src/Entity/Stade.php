<?php

namespace App\Entity;

use App\Repository\StadeRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: StadeRepository::class)]
class Stade
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: 'integer')]
    private $id;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    private $nom;

    #[ORM\ManyToOne(targetEntity: Pays::class)]
    #[ORM\JoinColumn(referencedColumnName: 'code')]
    private $pays;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    private $adresse;

    #[ORM\Column(type: 'integer', nullable: true)]
    private $capacite;

    #[ORM\Column(type: 'integer', nullable: true)]
    private $annee_construction;

    #[ORM\OneToMany(targetEntity: ImageStade::class, mappedBy: 'stade', cascade: ['persist', 'remove'], fetch: 'EAGER')]
    private $images;

    public function __construct()
    {
        $this->images = new ArrayCollection();
    }

    public function getId(): ?int
    {
        return $this->id;
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

    public function getPays(): ?Pays
    {
        return $this->pays;
    }

    public function setPays(?Pays $pays): self
    {
        $this->pays = $pays;

        return $this;
    }

    public function getAdresse(): ?string
    {
        return $this->adresse;
    }

    public function setAdresse(?string $adresse): self
    {
        $this->adresse = $adresse;

        return $this;
    }

    public function getCapacite(): ?int
    {
        return $this->capacite;
    }

    public function setCapacite(?int $capacite): self
    {
        $this->capacite = $capacite;

        return $this;
    }

    public function getAnneeConstruction(): ?int
    {
        return $this->annee_construction;
    }

    public function setAnneeConstruction(?int $annee_construction): self
    {
        $this->annee_construction = $annee_construction;

        return $this;
    }

    /**
     * @return Collection<int, ImageStade>
     */
    public function getImages(): Collection
    {
        return $this->images;
    }

    public function addImage(ImageStade $image): self
    {
        if (!$this->images->contains($image)) {
            $this->images[] = $image;
            $image->setStade($this);
        }

        return $this;
    }

    public function removeImage(ImageStade $image): self
    {
        if ($this->images->removeElement($image)) {
            // set the owning side to null (unless already changed)
            if ($image->getStade() === $this) {
                $image->setStade(null);
            }
        }

        return $this;
    }
}

<?php

namespace App\Entity;

use App\Repository\ClubRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Annotation\Groups;

/**
 * @ORM\Entity(repositoryClass=ClubRepository::class)
 */
class Club
{
    /**
     * @ORM\Id
     * @ORM\GeneratedValue
     * @ORM\Column(type="integer")
     * @Groups ({"read.Pays"})
     */
    private $id;

    /**
     * @ORM\Column(type="string", length=255, nullable=true)
     */
    private $nom;

    /**
     * @ORM\ManyToOne(targetEntity=Pays::class, cascade={"persist"})
     * @ORM\JoinColumn(referencedColumnName="code")
     */
    private $pays;

    /**
     * @ORM\Column(type="date", nullable=true)
     */
    private $date_creation;

    /**
     * @ORM\Column(type="string", length=255, nullable=true)
     */
    private $site_web;

    /**
     * @ORM\OneToMany(targetEntity=LogoClub::class, mappedBy="club", cascade={"persist", "remove"})
     */
    private $logos;

    /**
     * @ORM\Column(type="integer", nullable=true)
     */
    private $id_transfermarkt;

    /**
     * @ORM\ManyToOne(targetEntity=Stade::class, cascade={"persist", "remove"})
     */
    private $stade;

    /**
     * @ORM\ManyToMany(targetEntity=CouleurClub::class, cascade={"persist"})
     */
    private $couleurs;

    public function __construct()
    {
        $this->logos = new ArrayCollection();
        $this->couleurs = new ArrayCollection();
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

    public function getDateCreation(): ?\DateTimeInterface
    {
        return $this->date_creation;
    }

    public function setDateCreation(?\DateTimeInterface $date_creation): self
    {
        $this->date_creation = $date_creation;

        return $this;
    }

    public function getSiteWeb(): ?string
    {
        return $this->site_web;
    }

    public function setSiteWeb(?string $site_web): self
    {
        $this->site_web = $site_web;

        return $this;
    }

    /**
     * @return Collection<int, LogoClub>
     */
    public function getLogos(): Collection
    {
        return $this->logos;
    }

    public function addLogo(LogoClub $logo): self
    {
        if (!$this->logos->contains($logo)) {
            $this->logos[] = $logo;
            $logo->setClub($this);
        }

        return $this;
    }

    public function removeLogo(LogoClub $logo): self
    {
        if ($this->logos->removeElement($logo)) {
            // set the owning side to null (unless already changed)
            if ($logo->getClub() === $this) {
                $logo->setClub(null);
            }
        }

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

    public function getStade(): ?Stade
    {
        return $this->stade;
    }

    public function setStade(?Stade $stade): self
    {
        $this->stade = $stade;

        return $this;
    }

    /**
     * @return Collection<int, CouleurClub>
     */
    public function getCouleurs(): Collection
    {
        return $this->couleurs;
    }

    public function addCouleur(CouleurClub $couleur): self
    {
        if (!$this->couleurs->contains($couleur)) {
            $this->couleurs[] = $couleur;
        }

        return $this;
    }

    public function removeCouleur(CouleurClub $couleur): self
    {
        $this->couleurs->removeElement($couleur);

        return $this;
    }
}

<?php

namespace App\Entity;

use Doctrine\ORM\Mapping\InverseJoinColumn;
use App\Repository\ClubRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Annotation\Groups;
use Doctrine\ORM\Mapping\JoinColumn;
use Doctrine\ORM\Mapping\JoinTable;

#[ORM\Entity(repositoryClass: ClubRepository::class)]
class Club
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: 'integer')]
    #[Groups(['read.Pays', 'read.Club'])]
    private $id;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    #[Groups(['read.Club'])]
    private $nom;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    #[Groups(['read.Club'])]
    private $adresse;

    #[ORM\ManyToOne(targetEntity: Pays::class, cascade: ['persist'], fetch: 'EAGER')]
    #[ORM\JoinColumn(referencedColumnName: 'code')]
    #[Groups(['read.Club'])]
    private $pays;

    #[ORM\Column(type: 'date', nullable: true)]
    #[Groups(['read.Club'])]
    private $date_creation;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    #[Groups(['read.Club'])]
    private $site_web;

    #[ORM\OneToMany(targetEntity: LogoClub::class, mappedBy: 'club', cascade: ['persist', 'remove'], fetch: 'EAGER')]
    #[Groups(['read.Club'])]
    private $logos;

    #[ORM\Column(type: 'integer', nullable: true)]
    #[Groups(['read.Club'])]
    private $id_transfermarkt;

    #[ORM\ManyToOne(targetEntity: Stade::class, cascade: ['persist', 'remove'], fetch: 'EAGER')]
    #[Groups(['read.Club'])]
    private $stade;

    #[JoinTable(name: 'club_couleur_club')]
    #[JoinColumn(name: 'club_id', referencedColumnName: 'id')]
    #[InverseJoinColumn(name: 'couleur_club_id', referencedColumnName: 'id')]
    #[ORM\ManyToMany(targetEntity: CouleurClub::class, cascade: ['persist'])]
    #[Groups(['read.Club'])]
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
    
    public function getAdresse(): ?string
    {
        return $this->adresse;
    }

    public function setAdresse(?string $adresse): self
    {
        $this->adresse = $adresse;

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

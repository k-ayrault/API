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
    #[Groups(['read.Club', 'persist.Club'])]
    private $nom;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    #[Groups(['read.Club', 'persist.Club'])]
    private $adresse;

    #[ORM\ManyToOne(targetEntity: Pays::class)]
    #[ORM\JoinColumn(referencedColumnName: 'code')]
    #[Groups(['read.Club', 'persist.Club'])]
    private $pays;

    #[ORM\Column(type: 'date', nullable: true)]
    #[Groups(['read.Club', 'persist.Club'])]
    private $dateCreation;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    #[Groups(['read.Club', 'persist.Club'])]
    private $siteWeb;

    #[ORM\OneToMany(targetEntity: LogoClub::class, mappedBy: 'club', cascade: ['persist', 'remove'], fetch: 'EAGER')]
    #[Groups(['read.Club', 'persist.Club'])]
    private $logos;

    #[ORM\Column(type: 'integer', nullable: true)]
    #[Groups(['read.Club', 'persist.Club'])]
    private $idTransfermarkt;

    #[ORM\ManyToOne(targetEntity: Stade::class, cascade: ['persist', 'remove'], fetch: 'EAGER')]
    #[Groups(['read.Club', 'persist.Club'])]
    private $stade;

    #[JoinTable(name: 'club_couleur_club')]
    #[JoinColumn(name: 'club_id', referencedColumnName: 'id')]
    #[InverseJoinColumn(name: 'couleur_club_id', referencedColumnName: 'id')]
    #[ORM\ManyToMany(targetEntity: CouleurClub::class, cascade: ['persist'])]
    #[Groups(['read.Club', 'persist.Club'])]
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
        return $this->dateCreation;
    }

    public function setDateCreation(?\DateTimeInterface $dateCreation): self
    {
        $this->dateCreation = $dateCreation;

        return $this;
    }

    public function getSiteWeb(): ?string
    {
        return $this->siteWeb;
    }

    public function setSiteWeb(?string $siteWeb): self
    {
        $this->siteWeb = $siteWeb;

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
        return $this->idTransfermarkt;
    }

    public function setIdTransfermarkt(?int $idTransfermarkt): self
    {
        $this->idTransfermarkt = $idTransfermarkt;

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

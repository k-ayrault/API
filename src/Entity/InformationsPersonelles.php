<?php

namespace App\Entity;

use App\Repository\InformationsPersonellesRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Annotation\Groups;

#[ORM\Entity(repositoryClass: InformationsPersonellesRepository::class)]
class InformationsPersonelles
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: 'integer')]
    private $id;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    #[Groups(['persist.Joueur'])]
    private $nom_complet;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    #[Groups(['persist.Joueur'])]
    private $nom;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    #[Groups(['persist.Joueur'])]
    private $prenom;

    #[ORM\Column(type: 'date', nullable: true)]
    #[Groups(['persist.Joueur'])]
    private $date_naissance;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    #[Groups(['persist.Joueur'])]
    private $meilleur_pied;

    #[ORM\Column(type: 'integer', nullable: true)]
    #[Groups(['persist.Joueur'])]
    private $taille;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    #[Groups(['persist.Joueur'])]
    private $equipementier;

    #[ORM\JoinTable(name: 'nationnalites_joueur')]
    #[ORM\JoinColumn(name: 'informations_personelles_id', referencedColumnName: 'id')]
    #[ORM\InverseJoinColumn(name: 'pays_id', referencedColumnName: 'code')]
    #[ORM\ManyToMany(targetEntity: Pays::class, cascade: ['persist'], fetch: 'EAGER')]
    #[Groups(['persist.Joueur'])]
    private $nationnalites;

    #[ORM\Column(type: 'boolean')]
    #[Groups(['persist.Joueur'])]
    private $retraite_joueur;

    public function __construct()
    {
        $this->nationnalites = new ArrayCollection();
        $this->setRetraiteJoueur(false);
    }

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getNomComplet(): ?string
    {
        return $this->nom_complet;
    }

    public function setNomComplet(?string $nom_complet): self
    {
        $this->nom_complet = $nom_complet;

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

    public function getPrenom(): ?string
    {
        return $this->prenom;
    }

    public function setPrenom(?string $prenom): self
    {
        $this->prenom = $prenom;

        return $this;
    }

    public function getDateNaissance(): ?\DateTimeInterface
    {
        return $this->date_naissance;
    }

    public function setDateNaissance(?\DateTimeInterface $date_naissance): self
    {
        $this->date_naissance = $date_naissance;

        return $this;
    }

    public function getMeilleurPied(): ?string
    {
        return $this->meilleur_pied;
    }

    public function setMeilleurPied(?string $meilleur_pied): self
    {
        $this->meilleur_pied = $meilleur_pied;

        return $this;
    }

    public function getTaille(): ?int
    {
        return $this->taille;
    }

    public function setTaille(?int $taille): self
    {
        $this->taille = $taille;

        return $this;
    }

    public function getEquipementier(): ?string
    {
        return $this->equipementier;
    }

    public function setEquipementier(?string $equipementier): self
    {
        $this->equipementier = $equipementier;

        return $this;
    }

    /**
     * @return Collection<int, Pays>
     */
    public function getNationnalites(): Collection
    {
        return $this->nationnalites;
    }

    public function addNationnalite(Pays $nationnalite): self
    {
        if (!$this->nationnalites->contains($nationnalite)) {
            $this->nationnalites[] = $nationnalite;
        }

        return $this;
    }

    public function removeNationnalite(Pays $nationnalite): self
    {
        $this->nationnalites->removeElement($nationnalite);

        return $this;
    }

    public function isRetraiteJoueur(): ?bool
    {
        return $this->retraite_joueur;
    }

    public function setRetraiteJoueur(bool $retraite_joueur): self
    {
        $this->retraite_joueur = $retraite_joueur;

        return $this;
    }
}

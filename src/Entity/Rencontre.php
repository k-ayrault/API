<?php

namespace App\Entity;

use App\Repository\RencontreRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;

/**
 * @ORM\Entity(repositoryClass=RencontreRepository::class)
 */
class Rencontre
{
    /**
     * @ORM\Id
     * @ORM\GeneratedValue
     * @ORM\Column(type="integer")
     */
    private $id;

    /**
     * @ORM\ManyToOne(targetEntity=Club::class)
     */
    private $equpie_domicile;

    /**
     * @ORM\Column(type="datetime", nullable=true)
     */
    private $date_heure;

    /**
     * @ORM\ManyToOne(targetEntity=Club::class)
     */
    private $equipe_exterieur;

    /**
     * @ORM\OneToOne(targetEntity=Score::class, cascade={"persist", "remove"})
     */
    private $score;

    /**
     * @ORM\OneToMany(targetEntity=Titulaire::class, mappedBy="id_rencontre_ligue_1")
     */
    private $titulaires_domicile;

    /**
     * @ORM\OneToMany(targetEntity=Titulaire::class, mappedBy="id_rencontre_ligue_1")
     */
    private $titulaires_exterieur;

    /**
     * @ORM\ManyToMany(targetEntity=Joueur::class)
     * @ORM\JoinTable (name="rencontre_remplaçant_domicile")
     */
    private $remplacants_domicile;

    /**
     * @ORM\ManyToMany(targetEntity=Joueur::class)
     * @ORM\JoinTable (name="rencontre_remplaçant_exterieur")
     */
    private $remplacants_exterieur;

    /**
     * @ORM\Column(type="boolean")
     */
    private $termine;

    /**
     * @ORM\ManyToMany(targetEntity=Diffuseur::class)
     */
    private $diffuseur;

    /**
     * @ORM\ManyToOne(targetEntity=Arbitre::class)
     */
    private $arbitre_principale;

    /**
     * @ORM\ManyToOne(targetEntity=Arbitre::class)
     */
    private $arbitre_video;

    public function __construct()
    {
        $this->titulaires_domicile = new ArrayCollection();
        $this->titulaires_exterieur = new ArrayCollection();
        $this->remplacants_domicile = new ArrayCollection();
        $this->remplacants_exterieur = new ArrayCollection();
        $this->diffuseur = new ArrayCollection();
    }

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getEqupieDomicile(): ?Club
    {
        return $this->equpie_domicile;
    }

    public function setEqupieDomicile(?Club $equpie_domicile): self
    {
        $this->equpie_domicile = $equpie_domicile;

        return $this;
    }

    public function getDateHeure(): ?\DateTimeInterface
    {
        return $this->date_heure;
    }

    public function setDateHeure(?\DateTimeInterface $date_heure): self
    {
        $this->date_heure = $date_heure;

        return $this;
    }

    public function getEquipeExterieur(): ?Club
    {
        return $this->equipe_exterieur;
    }

    public function setEquipeExterieur(?Club $equipe_exterieur): self
    {
        $this->equipe_exterieur = $equipe_exterieur;

        return $this;
    }

    public function getScore(): ?Score
    {
        return $this->score;
    }

    public function setScore(?Score $score): self
    {
        $this->score = $score;

        return $this;
    }

    /**
     * @return Collection<int, Titulaire>
     */
    public function getTitulairesDomicile(): Collection
    {
        return $this->titulaires_domicile;
    }

    public function addTitulairesDomicile(Titulaire $titulairesDomicile): self
    {
        if (!$this->titulaires_domicile->contains($titulairesDomicile)) {
            $this->titulaires_domicile[] = $titulairesDomicile;
            $titulairesDomicile->setIdRencontreLigue1($this);
        }

        return $this;
    }

    public function removeTitulairesDomicile(Titulaire $titulairesDomicile): self
    {
        if ($this->titulaires_domicile->removeElement($titulairesDomicile)) {
            // set the owning side to null (unless already changed)
            if ($titulairesDomicile->getIdRencontreLigue1() === $this) {
                $titulairesDomicile->setIdRencontreLigue1(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, Titulaire>
     */
    public function getTitulairesExterieur(): Collection
    {
        return $this->titulaires_exterieur;
    }

    public function addTitulairesExterieur(Titulaire $titulairesExterieur): self
    {
        if (!$this->titulaires_exterieur->contains($titulairesExterieur)) {
            $this->titulaires_exterieur[] = $titulairesExterieur;
            $titulairesExterieur->setIdRencontreLigue1($this);
        }

        return $this;
    }

    public function removeTitulairesExterieur(Titulaire $titulairesExterieur): self
    {
        if ($this->titulaires_exterieur->removeElement($titulairesExterieur)) {
            // set the owning side to null (unless already changed)
            if ($titulairesExterieur->getIdRencontreLigue1() === $this) {
                $titulairesExterieur->setIdRencontreLigue1(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, Joueur>
     */
    public function getRemplacantsDomicile(): Collection
    {
        return $this->remplacants_domicile;
    }

    public function addRemplacantsDomicile(Joueur $remplacantsDomicile): self
    {
        if (!$this->remplacants_domicile->contains($remplacantsDomicile)) {
            $this->remplacants_domicile[] = $remplacantsDomicile;
        }

        return $this;
    }

    public function removeRemplacantsDomicile(Joueur $remplacantsDomicile): self
    {
        $this->remplacants_domicile->removeElement($remplacantsDomicile);

        return $this;
    }

    /**
     * @return Collection<int, Joueur>
     */
    public function getRemplacantsExterieur(): Collection
    {
        return $this->remplacants_exterieur;
    }

    public function addRemplacantsExterieur(Joueur $remplacantsExterieur): self
    {
        if (!$this->remplacants_exterieur->contains($remplacantsExterieur)) {
            $this->remplacants_exterieur[] = $remplacantsExterieur;
        }

        return $this;
    }

    public function removeRemplacantsExterieur(Joueur $remplacantsExterieur): self
    {
        $this->remplacants_exterieur->removeElement($remplacantsExterieur);

        return $this;
    }

    public function isTermine(): ?bool
    {
        return $this->termine;
    }

    public function setTermine(bool $termine): self
    {
        $this->termine = $termine;

        return $this;
    }

    /**
     * @return Collection<int, Diffuseur>
     */
    public function getDiffuseur(): Collection
    {
        return $this->diffuseur;
    }

    public function addDiffuseur(Diffuseur $diffuseur): self
    {
        if (!$this->diffuseur->contains($diffuseur)) {
            $this->diffuseur[] = $diffuseur;
        }

        return $this;
    }

    public function removeDiffuseur(Diffuseur $diffuseur): self
    {
        $this->diffuseur->removeElement($diffuseur);

        return $this;
    }

    public function getArbitrePrincipale(): ?Arbitre
    {
        return $this->arbitre_principale;
    }

    public function setArbitrePrincipale(?Arbitre $arbitre_principale): self
    {
        $this->arbitre_principale = $arbitre_principale;

        return $this;
    }

    public function getArbitreVideo(): ?Arbitre
    {
        return $this->arbitre_video;
    }

    public function setArbitreVideo(?Arbitre $arbitre_video): self
    {
        $this->arbitre_video = $arbitre_video;

        return $this;
    }
}

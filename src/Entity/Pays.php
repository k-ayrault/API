<?php

namespace App\Entity;

use ApiPlatform\Core\Annotation\ApiResource;
use App\Repository\PaysRepository;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Annotation\Groups;

/**
 * @ORM\Entity(repositoryClass=PaysRepository::class)
 * @ApiResource
 */
class Pays
{

    /**
     * @ORM\Id
     * @ORM\Column(name="code", type="string", length=2, unique=true)
     * @Groups ({"read.Pays"})
     */
    private $code;

    /**
     * @ORM\Column(type="string", length=255)
     * @Groups ({"read.Pays"})
     */
    private $nom;

    /**
     * @ORM\Column(type="string", length=255, nullable=true)
     * @Groups ({"read.Pays"})
     */
    private $drapeau;

    /**
     * @ORM\Column(type="string", length=255, nullable=true)
     */
    private $nom_fr;

    public function getCode(): ?string
    {
        return $this->code;
    }

    public function setCode(string $code): self
    {
        $this->code = $code;

        return $this;
    }

    public function getNom(): ?string
    {
        return $this->nom;
    }

    public function setNom(string $nom): self
    {
        $this->nom = $nom;

        return $this;
    }

    public function getDrapeau(): ?string
    {
        return $this->drapeau;
    }

    public function setDrapeau(?string $drapeau): self
    {
        $this->drapeau = $drapeau;

        return $this;
    }

    public function getNomFr(): ?string
    {
        return $this->nom_fr;
    }

    public function setNomFr(?string $nom_fr): self
    {
        $this->nom_fr = $nom_fr;

        return $this;
    }
}

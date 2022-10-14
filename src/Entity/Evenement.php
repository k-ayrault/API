<?php

namespace App\Entity;

use App\Repository\EvenementRepository;
use Doctrine\ORM\Mapping as ORM;

/**
 * @ORM\Entity(repositoryClass=EvenementRepository::class)
 */
class Evenement
{
    /**
     * @ORM\Id
     * @ORM\GeneratedValue
     * @ORM\Column(type="integer")
     */
    private $id;

    /**
     * @ORM\Column(type="boolean")
     */
    private $domicile;

    /**
     * @ORM\Column(type="integer")
     */
    private $minute;

    /**
     * @ORM\Column(type="integer")
     */
    private $minutes_additionnelles;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function isDomicile(): ?bool
    {
        return $this->domicile;
    }

    public function setDomicile(bool $domicile): self
    {
        $this->domicile = $domicile;

        return $this;
    }

    public function getMinute(): ?int
    {
        return $this->minute;
    }

    public function setMinute(int $minute): self
    {
        $this->minute = $minute;

        return $this;
    }

    public function getMinutesAdditionnelles(): ?int
    {
        return $this->minutes_additionnelles;
    }

    public function setMinutesAdditionnelles(int $minutes_additionnelles): self
    {
        $this->minutes_additionnelles = $minutes_additionnelles;

        return $this;
    }
}

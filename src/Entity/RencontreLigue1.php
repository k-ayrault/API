<?php

namespace App\Entity;

use App\Repository\RencontreLigue1Repository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;

/**
 * @ORM\Entity(repositoryClass=RencontreLigue1Repository::class)
 */
class RencontreLigue1 extends Rencontre
{

    /**
     * @ORM\Column(type="integer")
     */
    private $id_ligue_1;

    /**
     * @ORM\Column(type="integer")
     */
    private $journee;

    public function getIdLigue1(): ?int
    {
        return $this->id_ligue_1;
    }

    public function setIdLigue1(int $id_ligue_1): self
    {
        $this->id_ligue_1 = $id_ligue_1;

        return $this;
    }

    public function getJournee(): ?int
    {
        return $this->journee;
    }

    public function setJournee(int $journee): self
    {
        $this->journee = $journee;

        return $this;
    }

}

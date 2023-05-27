<?php

namespace App\Entity;

use App\Entity\InformationsPersonelles;
use App\Repository\InformationsPersonellesTempRepository;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: InformationsPersonellesTempRepository::class)]
class InformationsPersonellesTemp extends InformationsPersonelles
{

    #[ORM\OneToOne(targetEntity: InformationsPersonelles::class)]
    private InformationsPersonelles $informationsPersonelles;

    public function getInformationsPersonnelles(): ?InformationsPersonelles
    {
        return $this->informationsPersonelles;
    }

    public function setInformationsPersonnelles(InformationsPersonelles $informationsPersonnelles): ?InformationsPersonelles
    {
        $this->informationsPersonelles = $informationsPersonnelles;

        return $this->informationsPersonelles;
    }
}
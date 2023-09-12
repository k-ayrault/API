<?php

namespace App\Entity;

use App\Repository\CouleurClubRepository;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Annotation\Groups;

#[ORM\Entity(repositoryClass: CouleurClubRepository::class)]
class CouleurClub
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: 'integer')]
    #[Groups(['read.Club'])]
    private $id;

    #[ORM\Column(type: 'string', length: 6, unique: true)]
    #[Groups(['read.Club'])]
    private $hexa;

    public function __construct(string $hexa)
    {
        $this->setHexa($hexa);
    }

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getHexa(): ?string
    {
        return $this->hexa;
    }

    public function setHexa(string $hexa): self
    {
        $this->hexa = $hexa;

        return $this;
    }
}

<?php

namespace App\Repository;

use App\Entity\RencontreLigue1;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @extends ServiceEntityRepository<RencontreLigue1>
 *
 * @method RencontreLigue1|null find($id, $lockMode = null, $lockVersion = null)
 * @method RencontreLigue1|null findOneBy(array $criteria, array $orderBy = null)
 * @method RencontreLigue1[]    findAll()
 * @method RencontreLigue1[]    findBy(array $criteria, array $orderBy = null, $limit = null, $offset = null)
 */
class RencontreLigue1Repository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, RencontreLigue1::class);
    }

    public function add(RencontreLigue1 $entity, bool $flush = false): void
    {
        $this->getEntityManager()->persist($entity);

        if ($flush) {
            $this->getEntityManager()->flush();
        }
    }

    public function remove(RencontreLigue1 $entity, bool $flush = false): void
    {
        $this->getEntityManager()->remove($entity);

        if ($flush) {
            $this->getEntityManager()->flush();
        }
    }

//    /**
//     * @return RencontreLigue1[] Returns an array of RencontreLigue1 objects
//     */
//    public function findByExampleField($value): array
//    {
//        return $this->createQueryBuilder('r')
//            ->andWhere('r.exampleField = :val')
//            ->setParameter('val', $value)
//            ->orderBy('r.id', 'ASC')
//            ->setMaxResults(10)
//            ->getQuery()
//            ->getResult()
//        ;
//    }

//    public function findOneBySomeField($value): ?RencontreLigue1
//    {
//        return $this->createQueryBuilder('r')
//            ->andWhere('r.exampleField = :val')
//            ->setParameter('val', $value)
//            ->getQuery()
//            ->getOneOrNullResult()
//        ;
//    }
}

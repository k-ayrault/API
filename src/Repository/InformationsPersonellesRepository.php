<?php

namespace App\Repository;

use App\Entity\InformationsPersonelles;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @extends ServiceEntityRepository<InformationsPersonelles>
 *
 * @method InformationsPersonelles|null find($id, $lockMode = null, $lockVersion = null)
 * @method InformationsPersonelles|null findOneBy(array $criteria, array $orderBy = null)
 * @method InformationsPersonelles[]    findAll()
 * @method InformationsPersonelles[]    findBy(array $criteria, array $orderBy = null, $limit = null, $offset = null)
 */
class InformationsPersonellesRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, InformationsPersonelles::class);
    }

    public function add(InformationsPersonelles $entity, bool $flush = false): void
    {
        $this->getEntityManager()->persist($entity);

        if ($flush) {
            $this->getEntityManager()->flush();
        }
    }

    public function remove(InformationsPersonelles $entity, bool $flush = false): void
    {
        $this->getEntityManager()->remove($entity);

        if ($flush) {
            $this->getEntityManager()->flush();
        }
    }

//    /**
//     * @return InformationsPersonelles[] Returns an array of InformationsPersonelles objects
//     */
//    public function findByExampleField($value): array
//    {
//        return $this->createQueryBuilder('i')
//            ->andWhere('i.exampleField = :val')
//            ->setParameter('val', $value)
//            ->orderBy('i.id', 'ASC')
//            ->setMaxResults(10)
//            ->getQuery()
//            ->getResult()
//        ;
//    }

//    public function findOneBySomeField($value): ?InformationsPersonelles
//    {
//        return $this->createQueryBuilder('i')
//            ->andWhere('i.exampleField = :val')
//            ->setParameter('val', $value)
//            ->getQuery()
//            ->getOneOrNullResult()
//        ;
//    }
}

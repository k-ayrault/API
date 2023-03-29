<?php

namespace App\Controller\Security;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Component\Security\Core\Security;

class SecurityController extends AbstractController
{
    #[Route(path: '/api/login', name: 'api_login', methods: ['POST'])]
    public function login() {

    }

    #[Route(path: '/api/test', name: 'api_test', methods: ['GET'])]
    public function test(Security $security) {
        $user = $security->getUser();
        dd($user);
    }
}